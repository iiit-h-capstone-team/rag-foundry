class ProviderException(Exception):
    """Base provider exception."""


class ProviderInitializationException(ProviderException):
    """Raised when provider initialization fails."""


class ProviderRateLimitException(ProviderException):
    """Raised when provider is rate limited."""


class AllKeysExhaustedException(ProviderException):
    """Raised when no API keys are currently available."""
