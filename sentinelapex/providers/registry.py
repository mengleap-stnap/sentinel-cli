from typing import Dict, Type
from .base import BaseProvider
from .openai_adapter import OpenAIAdapter
# Import other adapters...

class ProviderRegistry:
    _adapters: Dict[str, Type[BaseProvider]] = {
        "openai": OpenAIAdapter,
        # "anthropic": AnthropicAdapter,
        # "gemini": GeminiAdapter,
    }

    @classmethod
    def register(cls, name: str, adapter_cls: Type[BaseProvider]):
        cls._adapters[name] = adapter_cls

    @classmethod
    def get_adapter(cls, name: str, api_key: str, model: str, temp: float) -> BaseProvider:
        if name not in cls._adapters:
            raise ValueError(f"Provider '{name}' not implemented yet.")
        return cls._adapters[name](api_key=api_key, model=model, temperature=temp)