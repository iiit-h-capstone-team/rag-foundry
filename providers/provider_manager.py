from providers.provider_factory import ProviderFactory


class ProviderManager:

    _providers = {}

    @classmethod
    def register_provider(
        cls,
        provider_name: str,
        provider_type: str,
        config: dict
    ):

        if provider_name in cls._providers:
            return

        cls._providers[provider_name] = (
            ProviderFactory.create_provider(
                provider_type=provider_type,
                config=config
            )
        )

    @classmethod
    def get_provider(
        cls,
        provider_name: str
    ):

        if provider_name not in cls._providers:
            raise ValueError(
                f"Provider '{provider_name}' not registered"
            )

        return cls._providers[provider_name]

    @classmethod
    def clear(cls):
        cls._providers.clear()