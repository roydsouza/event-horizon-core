import os
import logging
import httpx
from typing import List, Optional, Dict, Any

from .base import BaseLLMProvider, ProviderResponse, UsageMetadata

logger = logging.getLogger("event_horizon_core.providers.mlx")

class MLXProvider(BaseLLMProvider):
    """
    Remote Native MLX Provider.
    Wraps mlx_lm.server for unified memory, KV caching, and multi-process safety.
    """

    def __init__(self, model_path: str = "mlx-community/Llama-3.2-3B-Instruct-4bit", base_url: str = "http://127.0.0.1:8080", **kwargs):
        self.model_path = model_path
        self.base_url = base_url.rstrip("/")
        self.timeout = kwargs.get("timeout", 300.0)

    def generate(self, prompt: str, system_prompt: Optional[str] = None, tools: Optional[List[Dict[str, Any]]] = None, **kwargs) -> ProviderResponse:
        """
        Sends generation request to the mlx_lm.server.
        """
        import time
        from .base import ProviderResponse, UsageMetadata
        
        url = f"{self.base_url}/v1/chat/completions"
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_path,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 1000),
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 1.0),
            "stream": False
        }

        start_time = time.time()
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=payload)
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
                    model=self.model_path,
                    provider="mlx"
                )
        except Exception as e:
            logger.error(f"MLX Server Error: {e}")
            raise RuntimeError(f"Failed to generate completion from MLX server: {e}")

    def is_healthy(self) -> bool:
        """
        Checks if mlx_lm.server is responding on the configured port.
        """
        try:
            with httpx.Client(timeout=2.0) as client:
                response = client.get(f"{self.base_url}/v1/models")
                return response.status_code == 200
        except Exception:
            return False

    def list_models(self) -> List[str]:
        """
        Lists models available on the server.
        """
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/v1/models")
                response.raise_for_status()
                data = response.json()
                return [m["id"] for m in data.get("data", [])]
        except Exception:
            # Fallback to local cache check if server is down
            cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
            if not os.path.exists(cache_dir):
                return []
            return [d for d in os.listdir(cache_dir) if "mlx" in d.lower()]
