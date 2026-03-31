from typing import Dict, Any, Type, Optional
from .providers.base import BaseLLMProvider
from .providers.mlx_provider import MLXProvider
from .providers.ollama_provider import OllamaProvider
from .providers.openrouter_provider import OpenRouterProvider
from .providers.llamacpp_provider import LlamaCppProvider

class LLMFactory:
    """
    Factory class for Event Horizon LLM Providers.
    """

    PROVIDERS: Dict[str, Type[BaseLLMProvider]] = {
        "mlx": MLXProvider,
        "ollama": OllamaProvider,
        "openrouter": OpenRouterProvider,
        "llamacpp": LlamaCppProvider
    }

    @classmethod
    def get_provider(cls, provider_type: str, **kwargs) -> BaseLLMProvider:
        """
        Returns an instance of the requested provider.
        """
        provider_class = cls.PROVIDERS.get(provider_type.lower())
        if not provider_class:
            raise ValueError(f"Unknown provider type: {provider_type}. Available: {list(cls.PROVIDERS.keys())}")
        
        return provider_class(**kwargs)

    @classmethod
    def list_all_models(cls) -> Dict[str, Any]:
        """
        Consolidates model lists from all healthy providers.
        """
        results = {}
        for name, provider_class in cls.PROVIDERS.items():
            try:
                # Need an instance to check health/list models
                instance = provider_class()
                if instance.is_healthy():
                    results[name] = instance.list_models()
                else:
                    results[name] = "Offline"
            except Exception:
                results[name] = "Error"
        return results
