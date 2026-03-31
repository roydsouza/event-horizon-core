from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class UsageMetadata:
    """
    Detailed Token Usage and Performance Metadata.
    """
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    generation_time: float = 0.0 # In seconds
    
    @property
    def tokens_per_second(self) -> float:
        if self.generation_time > 0 and self.completion_tokens > 0:
            return self.completion_tokens / self.generation_time
        return 0.0

@dataclass
class ProviderResponse:
    """
    Standardized response from an Event Horizon provider.
    """
    text: str
    usage: UsageMetadata = field(default_factory=UsageMetadata)
    model: str = "unknown"
    provider: str = "unknown"

class BaseLLMProvider(ABC):
    """
    Abstract Base Class for Event Horizon LLM Providers.
    """

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None, tools: Optional[List[Dict[str, Any]]] = None, **kwargs) -> ProviderResponse:
        """Generates a completion based on a prompt. Supports optional tool definitions."""
        pass

    @abstractmethod
    def is_healthy(self) -> bool:
        """Checks if the provider/service is healthy."""
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """Lists available models for this provider."""
        pass
