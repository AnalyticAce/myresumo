"""Multi-provider AI client for PowerCV."""
# Re-export from ai_providers for backward compatibility
from app.services.ai_providers import AIClient, get_ai_client

__all__ = ["AIClient", "get_ai_client"]
