import os

from rag.config.config import ProviderConfig
from rag.config.enums import ProviderType
from providers.groq.groq_provider import GroqProvider


class ProviderFactory:

    @staticmethod
    def _resolve_api_keys(
        provider_name: str,
        config: ProviderConfig
    ) -> list[str]:
        """
        Resolve credentials for a provider from its configured environment
        variable. The env var name is taken from ``config.api_key_env`` so it is
        never hardcoded. A single env var may contain multiple comma-separated
        keys (used for rotation).
        """

        explicit_keys = config.params.get("api_keys")
        if explicit_keys:
            return list(explicit_keys)

        env_var = config.api_key_env
        if not env_var:
            raise ValueError(
                f"Provider '{provider_name}' has no 'api_key_env' configured "
                f"and no 'params.api_keys' fallback."
            )

        env_value = os.getenv(env_var)
        if env_value:
            return [
                key.strip()
                for key in env_value.split(",")
                if key.strip()
            ]

        raise ValueError(
            f"No API keys found for provider '{provider_name}'. "
            f"Expected environment variable '{env_var}' to be set "
            f"(or 'params.api_keys' to be provided)."
        )

    @staticmethod
    def create_provider(
        provider_name: str,
        provider_type: ProviderType,
        config: ProviderConfig
    ):
        provider_type = ProviderType(provider_type)

        api_keys = ProviderFactory._resolve_api_keys(
            provider_name,
            config
        )

        if provider_type == ProviderType.GROQ:
            kwargs = {}
            cooldown_seconds = config.params.get("cooldown_seconds")
            if cooldown_seconds is not None:
                kwargs["cooldown_seconds"] = cooldown_seconds

            return GroqProvider(
                api_keys=api_keys,
                **kwargs
            )

        raise ValueError(
            f"Unsupported provider type: {provider_type.value}"
        )
