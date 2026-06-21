class ProviderException(Exception):
    """Base provider exception."""
    pass


class ProviderInitializationException(ProviderException):
    """Raised when provider initialization fails."""
    pass


class ProviderRateLimitException(ProviderException):
    """Raised when provider is rate limited."""
    pass


class AllKeysExhaustedException(ProviderException):
    """Raised when no API keys are currently available."""
    pass