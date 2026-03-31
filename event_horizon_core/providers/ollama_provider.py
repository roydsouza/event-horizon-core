import httpx
import logging
import subprocess
from typing import List, Optional, Dict, Any

from .base import BaseLLMProvider, ProviderResponse, UsageMetadata

logger = logging.getLogger("event_horizon_core.providers.ollama")

class OllamaProvider(BaseLLMProvider):
    """
    Ollama-based Inference Engine.
    """

    def __init__(self, base_url: str = "http://127.0.0.1:11434", model: str = "llama3.1:latest", **kwargs):
        self.base_url = base_url
        self.model = model
        self.client = httpx.Client(timeout=300.0)

    def generate(self, prompt: str, system_prompt: Optional[str] = None, tools: Optional[List[Dict[str, Any]]] = None, **kwargs) -> ProviderResponse:
        import time
        from .base import ProviderResponse, UsageMetadata
        
        url = f"{self.base_url}/api/chat"
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "tools": tools,
            "options": {
                "temperature": kwargs.get("temperature", 0.7),
                "num_predict": kwargs.get("max_tokens", 1000)
            }
        }

        start_time = time.time()
        try:
            response = self.client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            duration = time.time() - start_time
            text = data["message"]["content"]
            
            # Extract Usage
            usage = UsageMetadata(
                prompt_tokens=data.get("prompt_eval_count", 0),
                completion_tokens=data.get("eval_count", 0),
                total_tokens=data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
                generation_time=duration
            )
            
            return ProviderResponse(
                text=text,
                usage=usage,
                model=self.model,
                provider="ollama"
            )
        except Exception as e:
            logger.error(f"Ollama inference failed: {e}")
            raise

    def is_healthy(self) -> bool:
        try:
            response = self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception:
            return False

    def list_models(self) -> List[str]:
        try:
            response = self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            models = [m["name"] for m in response.json().get("models", [])]
            return models
        except Exception:
            # Fallback to CLI if API fails
            try:
                result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')[1:] # Skip header
                    return [line.split()[0] for line in lines]
            except Exception:
                pass
            return []
