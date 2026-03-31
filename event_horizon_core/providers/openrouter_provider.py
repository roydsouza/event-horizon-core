import httpx
import logging
import os
from typing import List, Optional, Dict, Any

from .base import BaseLLMProvider, ProviderResponse, UsageMetadata

logger = logging.getLogger("event_horizon_core.providers.openrouter")

class OpenRouterProvider(BaseLLMProvider):
    """
    OpenRouter Remote Inference Engine with Model Aliasing.
    """

    # Model Shorthands for cleaner CLI usage
    ALIASES = {
        "best": "anthropic/claude-3.5-sonnet",
        "fast": "google/gemini-2.0-flash-001",
        "free": "google/gemini-2.0-flash-exp:free",
        "cheap": "meta-llama/llama-3.3-70b-instruct",
        "reasoner": "openai/o1-preview"
    }

    def __init__(self, api_key: Optional[str] = None, model: str = "fast", **kwargs):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        
        # Resolve alias if provided
        self.model = self.ALIASES.get(model.lower(), model)
        
        self.base_url = "https://openrouter.ai/api"
        self.client = httpx.Client(timeout=120.0)
        
        if not self.api_key:
            logger.warning("OPENROUTER_API_KEY not set. OpenRouterProvider will fail.")

    def generate(self, prompt: str, system_prompt: Optional[str] = None, tools: Optional[List[Dict[str, Any]]] = None, **kwargs) -> ProviderResponse:
        import time
        from .base import ProviderResponse, UsageMetadata
        
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable.")

        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/roydsouza/event-horizon-core",
            "Content-Type": "application/json"
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1000)
        }

        start_time = time.time()
        try:
            response = self.client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            duration = time.time() - start_time
            text = data["choices"][0]["message"]["content"]
            
            # Extract Usage
            usage_data = data.get("usage", {})
            usage = UsageMetadata(
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0),
                generation_time=duration
            )
            
            return ProviderResponse(
                text=text,
                usage=usage,
                model=self.model,
                provider="openrouter"
            )
        except Exception as e:
            logger.error(f"OpenRouter inference failed: {e}")
            raise

    def is_healthy(self) -> bool:
        return self.api_key is not None

    def list_models(self) -> List[str]:
        # Return aliases + core recommended models
        return list(self.ALIASES.keys()) + [
            "anthropic/claude-3.5-sonnet",
            "google/gemini-2.0-flash-001", 
            "meta-llama/llama-3.3-70b-instruct"
        ]
