import os
import logging
import httpx
import time
from typing import List, Optional, Dict, Any

from .base import BaseLLMProvider, ProviderResponse, UsageMetadata

logger = logging.getLogger("event_horizon_core.providers.llamacpp")

class LlamaCppProvider(BaseLLMProvider):
    """
    Native Llama.cpp Provider.
    Wraps llama-server for high-performance GGUF inference on Apple Silicon.
    """

    def __init__(self, base_url: str = "http://127.0.0.1:8081", model: str = "default", **kwargs):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = kwargs.get("timeout", 300.0)
        self.client = httpx.Client(timeout=self.timeout)

    def generate(self, prompt: str, system_prompt: Optional[str] = None, tools: Optional[List[Dict[str, Any]]] = None, **kwargs) -> ProviderResponse:
        """
        Sends generation request to the llama-server via OpenAI-compatible API.
        """
        url = f"{self.base_url}/v1/chat/completions"
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 1000),
            "temperature": kwargs.get("temperature", 0.7),
            "stream": False
        }

        start_time = time.time()
        try:
            response = self.client.post(url, json=payload)
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
                provider="llamacpp"
            )
        except Exception as e:
            logger.error(f"Llama.cpp Server Error: {e}")
            raise RuntimeError(f"Failed to generate completion from llama-server: {e}")

    def is_healthy(self) -> bool:
        """
        Checks if llama-server is responding.
        """
        try:
            response = self.client.get(f"{self.base_url}/v1/models")
            return response.status_code == 200
        except Exception:
            return False

    def list_models(self) -> List[str]:
        """
        Lists models available on the server.
        """
        try:
            response = self.client.get(f"{self.base_url}/v1/models")
            response.raise_for_status()
            data = response.json()
            return [m["id"] for m in data.get("data", [])]
        except Exception:
            return []
