"""Token usage tracking utility for monitoring LLM API consumption.

This module provides utilities for tracking and analyzing token usage
across OpenAI API calls throughout the application, supporting cost
monitoring, usage optimization, and analytics.
"""

import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

from langchain_core.callbacks import BaseCallbackHandler
from langchain_openai import ChatOpenAI

try:
    from langchain_ollama import ChatOllama
    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False
import os

from app.database.models.token_usage import TokenUsage, TokenUsageSummary

# Configure logger
logger = logging.getLogger(__name__)


# Define pricing constants for different models (price per 1M tokens)
MODEL_PRICING = {
    # CerebrasAI GPT-OSS models
    "gpt-oss-120b": {"input": 0.70, "output": 0.80},
    "gpt-oss-20b": {"input": 0.35, "output": 0.45},

    # Default model (gpt-oss-120b)
    "default": {"input": 0.70, "output": 0.80}
}


class TokenUsageCallback(BaseCallbackHandler):
    """LangChain callback handler for tracking token usage.

    This callback handler captures token usage data from LangChain's
    LLM interactions and logs it for analysis and cost tracking.
    """

    def __init__(
        self,
        feature: str,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        metadata: Optional[dict] = None
    ):
        """Initialize the token usage callback handler.

        Args:
            feature: The feature or component using the LLM (e.g., "resume_optimization")
            user_id: Optional ID of the user who triggered the request
            request_id: Optional request ID for correlation
            metadata: Additional context about the request
        """
        super().__init__()
        self.feature = feature
        self.user_id = user_id
        self.request_id = request_id or str(uuid.uuid4())
        self.metadata = metadata or {}
        self.start_time = time.time()
        self.tokens = {"prompt": 0, "completion": 0, "total": 0}
        self.model_name = "unknown"
        self.status = "success"

    def on_llm_start(self, serialized, prompts, **kwargs):
        """Called when LLM starts processing."""
        self.start_time = time.time()
        if "model_name" in kwargs.get("invocation_params", {}):
            self.model_name = kwargs["invocation_params"]["model_name"]

    def on_llm_end(self, response, **kwargs):
        """Called when LLM finishes processing."""
        llm_output = getattr(response, "llm_output", {}) or {}
        token_usage = llm_output.get("token_usage", {})

        # Extract token counts
        self.tokens["prompt"] = token_usage.get("prompt_tokens", 0)
        self.tokens["completion"] = token_usage.get("completion_tokens", 0)
        self.tokens["total"] = token_usage.get("total_tokens", 0)

        # Make sure model name is captured
        if not self.model_name or self.model_name == "unknown":
            self.model_name = getattr(response, "model_name", "unknown")

        # Calculate cost
        cost = self._calculate_cost()

        # Log the token usage
        TokenTracker.log_token_usage(
            endpoint="langchain_llm",
            model_name=self.model_name,
            prompt_tokens=self.tokens["prompt"],
            completion_tokens=self.tokens["completion"],
            total_tokens=self.tokens["total"],
            feature=self.feature,
            user_id=self.user_id,
            request_id=self.request_id,
            status=self.status,
            cost_usd=cost,
            metadata=self.metadata
        )

    def on_llm_error(self, error, **kwargs):
        """Called when LLM encounters an error."""
        self.status = "error"

    def _calculate_cost(self) -> float:
        """Calculate the estimated cost based on token usage and model.

        This method converts the pricing from per 1M tokens to per token
        and then calculates the cost based on actual token usage.

        Returns:
            float: The calculated cost in USD
        """
        model_prices = MODEL_PRICING.get(
            self.model_name, MODEL_PRICING["default"])

        # Convert from price per 1M tokens to price per token
        input_price_per_token = model_prices["input"] / 1_000_000
        output_price_per_token = model_prices["output"] / 1_000_000

        # Calculate cost in USD
        prompt_cost = self.tokens["prompt"] * input_price_per_token
        completion_cost = self.tokens["completion"] * output_price_per_token

        return prompt_cost + completion_cost


class TokenTracker:
    """Utility for tracking, analyzing, and optimizing token usage.

    This class provides methods to track token usage across different
    OpenAI API calls, calculate costs, and generate usage reports.
    """

    # In-memory store for token usage data
    # In a production environment, this would typically use a database
    _token_usage_records: List[TokenUsage] = []

    @classmethod
    def create_langchain_callback(
        cls,
        feature: str,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> TokenUsageCallback:
        """Create a LangChain callback handler for token tracking.

        Args:
            feature: The feature or component using the LLM
            user_id: Optional ID of the user who triggered the request
            request_id: Optional request ID for correlation
            metadata: Additional context about the request

        Returns:
            A LangChain callback handler configured for token tracking
        """
        return TokenUsageCallback(
            feature=feature,
            user_id=user_id,
            request_id=request_id,
            metadata=metadata
        )

    @classmethod
    def get_tracked_langchain_llm(
        cls,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        temperature: float = 0.0,
        feature: str = "unspecified",
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        metadata: Optional[dict] = None,
        **kwargs
    ):
        """Create a LangChain LLM instance with token tracking.

        Automatically detects whether to use Ollama (local) or OpenAI (cloud)
        based on the api_base parameter.

        Args:
            model_name: The name of the model to use
            api_key: API key (not needed for Ollama)
            api_base: Base URL for the API (e.g., http://localhost:11434 for Ollama)
            temperature: Temperature setting for the model
            feature: The feature using this LLM instance
            user_id: Optional user ID
            request_id: Optional request correlation ID
            metadata: Additional context
            **kwargs: Additional arguments to pass to the LLM

        Returns:
            A LLM instance (ChatOllama or ChatOpenAI) with token tracking enabled
        """
        # Create the token tracking callback
        callback = cls.create_langchain_callback(
            feature=feature,
            user_id=user_id,
            request_id=request_id,
            metadata=metadata
        )

        provider = (os.getenv("API_TYPE") or os.getenv(
            "LLM_PROVIDER") or "").lower()
        cerebras_key = os.getenv("CEREBRAS_API_KEY")
        forced_provider = (os.getenv("FORCE_LLM_PROVIDER") or "").lower()

        # Prefer Cerebras whenever it is configured, to avoid accidentally routing to a leftover
        # local Ollama base URL (e.g. API_BASE=http://localhost:11434). You can force local
        # behavior explicitly via FORCE_LLM_PROVIDER=ollama (or local).
        force_local = forced_provider in {
            "ollama", "local"} or provider in {"ollama", "local"}
        if cerebras_key and not force_local:
            if not api_key:
                api_key = cerebras_key
            api_base = "https://api.cerebras.ai/v1"

        effective_api_base = (
            api_base
            or os.getenv("API_BASE")
            or os.getenv("OLLAMA_BASE_URL")
            or os.getenv("OLLAMA_HOST")
        )
        if not effective_api_base and provider == "ollama":
            effective_api_base = "http://localhost:11434"

        if effective_api_base:
            effective_api_base = effective_api_base.strip()
            effective_api_base = effective_api_base.rstrip("/")

        # Detect if using Ollama (local) or OpenAI (cloud)
        is_ollama = bool(effective_api_base) and (
            "localhost" in effective_api_base
            or "127.0.0.1" in effective_api_base
            or "11434" in effective_api_base
        )

        # Normalize Ollama base URL. Ollama uses /api/* endpoints (not /v1/*).
        # For OpenAI-compatible providers, keep /v1 if present.
        if is_ollama and effective_api_base.endswith("/v1"):
            effective_api_base = effective_api_base[:-3].rstrip("/")

        if is_ollama:
            if not HAS_OLLAMA:
                logger.warning(
                    "langchain-ollama not installed, falling back to ChatOpenAI")
                return ChatOpenAI(
                    model_name=model_name,
                    temperature=temperature,
                    openai_api_key=api_key,
                    openai_api_base=effective_api_base,
                    callbacks=[callback],
                    **kwargs
                )

            # Use ChatOllama for local models
            # Use Ollama model and base URL from config
            ollama_model_name = model_name or os.getenv("MODEL_NAME")
            ollama_base_url = effective_api_base

            return ChatOllama(
                model=ollama_model_name,
                base_url=ollama_base_url,
                temperature=temperature,
                callbacks=[callback],
                **kwargs
            )
        else:
            # Use ChatOpenAI for cloud models
            return ChatOpenAI(
                model_name=model_name,
                temperature=temperature,
                openai_api_key=api_key,
                openai_api_base=effective_api_base,
                callbacks=[callback],
                **kwargs
            )

    @classmethod
    def log_token_usage(
        cls,
        endpoint: str,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        feature: str,
        cost_usd: float,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        status: str = "success",
        metadata: Optional[dict] = None
    ) -> None:
        """Log token usage from an API call.

        Args:
            endpoint: The specific API endpoint or function called
            model_name: The name of the LLM model used
            prompt_tokens: Number of tokens in the prompt
            completion_tokens: Number of tokens in the completion
            total_tokens: Total tokens used
            feature: The feature or component using the API
            cost_usd: Estimated cost in USD
            user_id: Optional ID of the user who triggered the request
            request_id: Optional request ID for correlation
            status: Success or error status
            metadata: Additional context about the request
        """
        # Create a TokenUsage record
        token_usage = TokenUsage(
            endpoint=endpoint,
            llm_model=model_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            request_id=request_id,
            user_id=user_id,
            feature=feature,
            status=status,
            cost_usd=cost_usd,
            metadata=metadata
        )

        # Store the usage record
        # In a production environment, this would be persisted to a database
        cls._token_usage_records.append(token_usage)

        # Log the usage for monitoring
        logger.info(
            f"Token usage: {model_name} | {feature} | "
            f"Tokens: {total_tokens} | Cost: ${cost_usd:.6f}"
        )

    @classmethod
    def get_usage_summary(
        cls,
        days: int = 30,
        feature: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> TokenUsageSummary:
        """Generate a summary of token usage for the specified period.

        Args:
            days: Number of days to include in the summary
            feature: Filter by specific feature (optional)
            user_id: Filter by specific user (optional)

        Returns:
            A summary of token usage statistics
        """
        # Calculate the start date for the period
        period_start = datetime.utcnow() - timedelta(days=days)

        # Filter records by date and optional parameters
        filtered_records = [
            r for r in cls._token_usage_records
            if r.timestamp >= period_start and
            (feature is None or r.feature == feature) and
            (user_id is None or r.user_id == user_id)
        ]

        # Initialize counters
        total_api_calls = len(filtered_records)
        total_prompt_tokens = sum(r.prompt_tokens for r in filtered_records)
        total_completion_tokens = sum(
            r.completion_tokens for r in filtered_records)
        total_tokens = sum(r.total_tokens for r in filtered_records)
        total_cost_usd = sum(r.cost_usd for r in filtered_records)

        # Group usage by model and feature
        usage_by_model = {}
        usage_by_feature = {}

        for record in filtered_records:
            # Aggregate by model
            if record.llm_model not in usage_by_model:
                usage_by_model[record.llm_model] = {
                    "calls": 0,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                    "cost_usd": 0.0
                }

            usage_by_model[record.llm_model]["calls"] += 1
            usage_by_model[record.llm_model]["prompt_tokens"] += record.prompt_tokens
            usage_by_model[record.llm_model]["completion_tokens"] += record.completion_tokens
            usage_by_model[record.llm_model]["total_tokens"] += record.total_tokens
            usage_by_model[record.llm_model]["cost_usd"] += record.cost_usd

            # Aggregate by feature
            if record.feature not in usage_by_feature:
                usage_by_feature[record.feature] = {
                    "calls": 0,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                    "cost_usd": 0.0
                }

            usage_by_feature[record.feature]["calls"] += 1
            usage_by_feature[record.feature]["prompt_tokens"] += record.prompt_tokens
            usage_by_feature[record.feature]["completion_tokens"] += record.completion_tokens
            usage_by_feature[record.feature]["total_tokens"] += record.total_tokens
            usage_by_feature[record.feature]["cost_usd"] += record.cost_usd

        # Create and return the summary
        return TokenUsageSummary(
            total_api_calls=total_api_calls,
            total_prompt_tokens=total_prompt_tokens,
            total_completion_tokens=total_completion_tokens,
            total_tokens=total_tokens,
            total_cost_usd=total_cost_usd,
            period_start=period_start,
            period_end=datetime.utcnow(),
            usage_by_model=usage_by_model,
            usage_by_feature=usage_by_feature
        )

    @classmethod
    def export_usage_data(cls, format: str = "json") -> Union[str, Dict]:
        """Export token usage data for external analysis.

        Args:
            format: Output format ('json' or 'dict')

        Returns:
            Token usage data in the requested format
        """
        # Convert the records to dictionaries
        records = [record.model_dump() for record in cls._token_usage_records]

        # Convert UUID and datetime objects for JSON serialization
        for record in records:
            record["id"] = str(record["id"])
            record["timestamp"] = record["timestamp"].isoformat()

        # Return in the requested format
        if format.lower() == "json":
            return json.dumps(records, indent=2)
        else:
            return records

    @classmethod
    def clear_usage_data(cls) -> None:
        """Clear all stored token usage data.

        This method is primarily for testing or data management purposes.
        In a production environment, this would typically be handled by
        database retention policies.
        """
        cls._token_usage_records = []
