from providers.groq.groq_provider import GroqProvider


class ProviderFactory:

    @staticmethod
    def _resolve_api_keys(
        provider_name: str,
        config: dict
    ) -> list[str]:

        params = config.get("params", {})

        if params.get("api_keys"):
            return params["api_keys"]

        env_var = (
            f"{provider_name.upper()}_API_KEYS"
        )

        env_value = os.getenv(env_var)

        if env_value:

            return [
                key.strip()
                for key in env_value.split(",")
                if key.strip()
            ]

        raise ValueError(
            f"No api keys found. "
            f"Expected either config.params.api_keys "
            f"or env var '{env_var}'"
        )

    @staticmethod
    def create_provider(
        provider_name: str,
        provider_type: str,
        config: dict
    ):

        if provider_type == "groq":

            api_keys = self._resolve_api_keys(provider_name, config)

            return GroqProvider(
                api_keys=api_keys
            )

        raise ValueError(
            f"Unsupported provider type: {provider_type}"
        )