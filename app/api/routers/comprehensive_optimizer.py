"""Comprehensive Resume Optimizer API Endpoints.

This module provides FastAPI endpoints for the comprehensive AI resume optimization system,
including master optimization, ATS analysis, hidden achievements extraction,
three-version creation, and iterative improvement.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

from app.services.ai.comprehensive_optimizer import ComprehensiveResumeOptimizer


# Pydantic models for request/response
class MasterOptimizationRequest(BaseModel):
    """Request model for master resume optimization."""
    target_role: str = Field(..., description="Target job title")
    job_description: str = Field(..., description="Full job description")
    resume_text: str = Field(..., description="Current resume text")
    target_company: str = Field(default="", description="Target company (optional)")
    focus_area: str = Field(default="backend/data/DevOps/leadership", 
                           description="Focus area for optimization")


class ATSAnalysisRequest(BaseModel):
    """Request model for ATS keyword analysis."""
    job_description: str = Field(..., description="Job description text")
    resume_text: str = Field(..., description="Resume text")


class HiddenAchievementsRequest(BaseModel):
    """Request model for hidden achievements extraction."""
    role_description: str = Field(..., description="Description of the role")


class ThreeVersionRequest(BaseModel):
    """Request model for three-version resume creation."""
    job_description: str = Field(..., description="Job description text")
    resume_text: str = Field(..., description="Resume text")


class IterativeImprovementRequest(BaseModel):
    """Request model for iterative improvement."""
    job_description: str = Field(..., description="Job description text")
    resume_text: str = Field(..., description="Resume text")


# Create router
comprehensive_router = APIRouter(
    prefix="/api/comprehensive",
    tags=["comprehensive-optimizer"]
)


def get_comprehensive_optimizer() -> ComprehensiveResumeOptimizer:
    """Dependency to get the comprehensive optimizer instance."""
    return ComprehensiveResumeOptimizer()


@comprehensive_router.post(
    "/optimize/master",
    response_model=Dict[str, Any],
    summary="Master Resume Optimization",
    description="Execute the complete master optimization with all tasks including step-back analysis, keyword extraction, experience optimization, and psychological optimization."
)
async def master_optimization(
    request: MasterOptimizationRequest,
    optimizer: ComprehensiveResumeOptimizer = Depends(get_comprehensive_optimizer)
) -> Dict[str, Any]:
    """Execute the master optimization prompt with all tasks."""
    try:
        result = await optimizer.optimize_resume_master(
            target_role=request.target_role,
            job_description=request.job_description,
            resume_text=request.resume_text,
            target_company=request.target_company,
            focus_area=request.focus_area
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Master optimization failed: {str(e)}"
        )


@comprehensive_router.post(
    "/analyze/ats",
    response_model=Dict[str, Any],
    summary="ATS Keyword Analysis",
    description="Analyze ATS keywords and gaps between job description and resume."
)
async def ats_keyword_analysis(
    request: ATSAnalysisRequest,
    optimizer: ComprehensiveResumeOptimizer = Depends(get_comprehensive_optimizer)
) -> Dict[str, Any]:
    """Analyze ATS keywords and gaps."""
    try:
        result = await optimizer.analyze_ats_keywords(
            job_description=request.job_description,
            resume_text=request.resume_text
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ATS keyword analysis failed: {str(e)}"
        )


@comprehensive_router.post(
    "/extract/achievements",
    response_model=Dict[str, Any],
    summary="Extract Hidden Achievements",
    description="Extract hidden achievements from a role description using targeted questions."
)
async def extract_hidden_achievements(
    request: HiddenAchievementsRequest,
    optimizer: ComprehensiveResumeOptimizer = Depends(get_comprehensive_optimizer)
) -> Dict[str, Any]:
    """Extract hidden achievements."""
    try:
        result = await optimizer.extract_hidden_achievements(
            role_description=request.role_description
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hidden achievements extraction failed: {str(e)}"
        )


@comprehensive_router.post(
    "/create/three-versions",
    response_model=Dict[str, Any],
    summary="Create Three Resume Versions",
    description="Create three resume positioning variants: results-focused, leadership-focused, and technical-depth."
)
async def create_three_versions(
    request: ThreeVersionRequest,
    optimizer: ComprehensiveResumeOptimizer = Depends(get_comprehensive_optimizer)
) -> Dict[str, Any]:
    """Create three resume versions."""
    try:
        result = await optimizer.create_three_versions(
            job_description=request.job_description,
            resume_text=request.resume_text
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Three-version creation failed: {str(e)}"
        )


@comprehensive_router.post(
    "/improve/iterative",
    response_model=Dict[str, Any],
    summary="Iterative Improvement",
    description="Execute iterative improvement with scoring loop to continuously improve the resume."
)
async def iterative_improvement(
    request: IterativeImprovementRequest,
    optimizer: ComprehensiveResumeOptimizer = Depends(get_comprehensive_optimizer)
) -> Dict[str, Any]:
    """Execute iterative improvement."""
    try:
        result = await optimizer.iterative_improvement(
            job_description=request.job_description,
            resume_text=request.resume_text
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Iterative improvement failed: {str(e)}"
        )


@comprehensive_router.get(
    "/workflows",
    response_model=Dict[str, str],
    summary="Get Quick Start Workflows",
    description="Get descriptions of quick start workflows (5-minute, 20-minute, 60-minute)."
)
async def get_quick_start_workflows(
    optimizer: ComprehensiveResumeOptimizer = Depends(get_comprehensive_optimizer)
) -> Dict[str, str]:
    """Get quick start workflow descriptions."""
    return optimizer.get_quick_start_workflows()


@comprehensive_router.get(
    "/tips",
    response_model=List[str],
    summary="Get Pro Tips",
    description="Get professional tips for resume optimization."
)
async def get_pro_tips(
    optimizer: ComprehensiveResumeOptimizer = Depends(get_comprehensive_optimizer)
) -> List[str]:
    """Get pro tips."""
    return optimizer.get_pro_tips()


@comprehensive_router.get(
    "/eu-alignment",
    response_model=Dict[str, List[str]],
    summary="Get EU 2025 Alignment",
    description="Get EU 2025 alignment requirements for ATS, digital skills, soft skills, and regional considerations."
)
async def get_eu_2025_alignment(
    optimizer: ComprehensiveResumeOptimizer = Depends(get_comprehensive_optimizer)
) -> Dict[str, List[str]]:
    """Get EU 2025 alignment requirements."""
    return optimizer.get_eu_2025_alignment()


@comprehensive_router.get(
    "/skills",
    response_model=str,
    summary="Get Master Skills List",
    description="Get the complete master skills list for Europe 2025."
)
async def get_master_skills(
    optimizer: ComprehensiveResumeOptimizer = Depends(get_comprehensive_optimizer)
) -> str:
    """Get master skills list."""
    return optimizer.MASTER_SKILLS_LIST
