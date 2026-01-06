"""Custom exception classes for PowerCV."""


class ConfigurationError(ValueError):
    """Raised when the application is not properly configured.

    This exception is used for configuration-related errors that should
    be addressed before the application can function properly, such as
    missing API keys, invalid database connections, etc.
    """
    
    def __init__(self, message: str, config_key: str = None, provider: str = None):
        super().__init__(message)
        self.config_key = config_key
        self.provider = provider

    def __str__(self):
        base_msg = super().__str__()
        if self.config_key and self.provider:
            return f"{base_msg} (Config: {self.config_key}, Provider: {self.provider})"
        elif self.config_key:
            return f"{base_msg} (Config: {self.config_key})"
        return base_msg


class MissingApiKeyError(ConfigurationError):
    """Raised when a required API key is not configured.

    This is a specific type of ConfigurationError for missing API keys,
    allowing calling code to handle this case explicitly.
    """
    
    def __init__(self, config_key: str, provider: str):
        message = (
            f"API key '{config_key}' not found in settings. "
            f"Configure the API key for provider '{provider}' to enable AI operations."
        )
        super().__init__(message, config_key=config_key, provider=provider)


class DatabaseConnectionError(ConfigurationError):
    """Raised when database connection fails due to configuration issues."""

    pass


class FileValidationError(ValueError):
    """Raised when file validation fails."""

    pass