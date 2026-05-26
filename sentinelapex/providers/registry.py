from typing import Dict, Type

from .base import BaseProvider
from .openai_adapter import OpenAIAdapter


class ProviderRegistry:
    """
    Central registry for AI provider adapters.
    """

    _adapters: Dict[str, Type[BaseProvider]] = {
        "openai": OpenAIAdapter,
        # "anthropic": AnthropicAdapter,
        # "gemini": GeminiAdapter,
    }

    @classmethod
    def register(
        cls,
        name: str,
        adapter_cls: Type[BaseProvider]
    ) -> None:
        """
        Register a new provider adapter.
        """

        if not issubclass(adapter_cls, BaseProvider):
            raise TypeError(
                "adapter_cls must inherit from BaseProvider"
            )

        cls._adapters[name.lower()] = adapter_cls

    @classmethod
    def get_adapter(
        cls,
        name: str,
        api_key: str,
        model: str,
        temp: float
    ) -> BaseProvider:
        """
        Return initialized provider adapter.
        """

        provider_name = name.lower()

        if provider_name not in cls._adapters:
            available = ", ".join(
                cls._adapters.keys()
            )

            raise ValueError(
                f"Provider '{name}' not implemented yet. "
                f"Available providers: {available}"
            )

        adapter_cls = cls._adapters[provider_name]

        return adapter_cls(
            api_key=api_key,
            model=model,
            temperature=temp
        )

    @classmethod
    def list_providers(cls) -> list[str]:
        """
        Return available provider names.
        """

        return list(cls._adapters.keys())