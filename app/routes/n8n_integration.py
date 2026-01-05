"""n8n-friendly API endpoints."""
from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import logging
import os

from app.services.cv_analyzer import CVAnalyzer
from app.services.workflow_orchestrator import CVWorkflowOrchestrator
from app.services.ai_client import get_ai_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/n8n", tags=["n8n"])

# API key authentication
N8N_API_KEY = os.getenv("N8N_API_KEY", "changeme")


def verify_api_key(x_api_key: str = Header(...)):
    """Verify n8n API key."""
    if x_api_key != N8N_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


# Request models
class CVAnalysisRequest(BaseModel):
    cv_text: str = Field(..., description="Full CV text")
    jd_text: str = Field(..., description="Job description text")
    user_id: Optional[str] = Field(None, description="User identifier")


class CVOptimizationRequest(BaseModel):
    cv_text: str
    jd_text: str
    generate_cover_letter: bool = True
    user_id: Optional[str] = None
    callback_url: Optional[str] = None


class ProviderSwitchRequest(BaseModel):
    provider: str = Field(...,
                          description="AI provider to switch to (deepseek/cerebras/openai)")
    test_connection: bool = Field(
        False, description="Whether to test the provider connection")


# Endpoints
@router.get("/health")
async def health_check():
    """Health check endpoint for n8n monitoring."""
    client = get_ai_client()
    info = client.get_provider_info()

    return {
        "status": "healthy",
        "service": "PowerCV",
        "ai_provider": info['provider'],
        "ai_model": info['model']
    }


@router.post("/analyze")
async def analyze_cv(
    request: CVAnalysisRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Analyze CV against job description.
    Returns quick analysis for n8n workflows.
    """
    try:
        logger.info(f"n8n analysis request from user: {request.user_id}")

        analyzer = CVAnalyzer()
        analysis = analyzer.analyze(request.cv_text, request.jd_text)

        # Simplified response for n8n
        return {
            "success": True,
            "ats_score": analysis.get('ats_score', 0),
            "matched_keywords": analysis['keyword_analysis']['matched_keywords'][:10],
            "missing_keywords": analysis['keyword_analysis']['missing_critical'][:5],
            "top_recommendations": analysis['recommendations'][:3],
            "user_id": request.user_id
        }

    except Exception as e:
        logger.error(f"n8n analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize")
async def optimize_cv(
    request: CVOptimizationRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Full CV optimization workflow for n8n.
    Returns structured JSON for easy n8n processing.
    """
    try:
        logger.info(f"n8n optimization request from user: {request.user_id}")

        orchestrator = CVWorkflowOrchestrator()
        result = orchestrator.optimize_cv_for_job(
            cv_text=request.cv_text,
            jd_text=request.jd_text,
            generate_cover_letter=request.generate_cover_letter
        )

        # Format for n8n
        return {
            "success": True,
            "data": {
                "ats_score": result['ats_score'],
                "analysis": result['analysis'],
                "optimized_cv": result.get('optimized_cv', {}),
                "cover_letter": result.get('cover_letter', {}).get('cover_letter', ''),
                "user_id": request.user_id
            },
            "metadata": {
                "processing_time": result.get('processing_time', 0),
                "model_used": get_ai_client().model
            }
        }

    except Exception as e:
        logger.error(f"n8n optimization error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/switch-provider")
async def switch_ai_provider(
    request: ProviderSwitchRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Switch AI provider dynamically.
    Useful for A/B testing in n8n workflows.
    """
    try:
        # Validate provider
        if request.provider not in ['cerebras', 'openai']:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid provider. Choose: cerebras, openai"
            )

        # Set environment variable
        os.environ['AI_PROVIDER'] = request.provider

        # Test new provider if requested
        if request.test_connection:
            try:
                client = get_ai_client()
                # Quick test with minimal request
                test_response = client.chat_completion(
                    system_prompt="Test",
                    user_message="Hello",
                    max_tokens=10,
                    timeout=10
                )
                connection_tested = True
            except Exception as test_error:
                logger.warning(
                    f"Provider connection test failed: {test_error}")
                connection_tested = False
        else:
            connection_tested = None

        # Get provider info
        client = get_ai_client()
        info = client.get_provider_info()

        logger.info(f"Switched to provider: {request.provider}")

        response = {
            "success": True,
            "provider": info['provider'],
            "model": info['model'],
            "message": f"Switched to {request.provider}"
        }

        if request.test_connection:
            response["connection_tested"] = connection_tested

        return response

    except Exception as e:
        logger.error(f"Provider switch error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers")
async def list_providers(api_key: str = Depends(verify_api_key)):
    """
    Get current AI provider information and available providers.
    """
    try:
        client = get_ai_client()
        info = client.get_provider_info()

        # Check which providers are configured
        available_providers = []
        provider_configs = {
            'cerebras': {'model': 'gpt-oss-120b', 'key': 'CEREBRAS_API_KEY'},
            'openai': {'model': 'gpt-4', 'key': 'OPENAI_API_KEY'}
        }

        for provider_name, config in provider_configs.items():
            configured = bool(os.getenv(config['key']))
            available_providers.append({
                "name": provider_name,
                "model": config['model'],
                "configured": configured
            })

        return {
            "current_provider": info['provider'],
            "current_model": info['model'],
            "available_providers": available_providers
        }

    except Exception as e:
        logger.error(f"Provider info error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
