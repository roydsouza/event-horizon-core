from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BaseLLMProvider(ABC):
    """
    Abstract Base Class for Event Horizon LLM Providers.
    """

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generates a completion based on a prompt."""
        pass

    @abstractmethod
    def is_healthy(self) -> bool:
        """Checks if the provider/service is healthy."""
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """Lists available models for this provider."""
        pass
