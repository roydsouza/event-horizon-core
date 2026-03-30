import httpx
import logging
import os
from typing import List, Optional, Dict, Any

from .base import BaseLLMProvider

logger = logging.getLogger("event_horizon_core.providers.openrouter")

class OpenRouterProvider(BaseLLMProvider):
    """
    OpenRouter Remote Inference Engine.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "google/gemini-2.0-flash-001"):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
        self.client = httpx.Client(timeout=120.0)
        
        if not self.api_key:
            logger.warning("OPENROUTER_API_KEY not set. OpenRouterProvider will fail.")

    def generate(self, prompt: str, system_prompt: Optional[str] = None, tools: Optional[List[Dict[str, Any]]] = None, **kwargs) -> str:
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

        try:
            response = self.client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"OpenRouter inference failed: {e}")
            raise

    def is_healthy(self) -> bool:
        # Simple health check by checking model availability or just verifying API key presence
        return self.api_key is not None

    def list_models(self) -> List[str]:
        # This can be very long, so we just return a few popular ones or an empty list
        # to avoid flooding the status output.
        return ["google/gemini-2.0-flash-001", "anthropic/claude-3.5-sonnet", "meta-llama/llama-3.3-70b-instruct"]
