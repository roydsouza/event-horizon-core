import httpx
import logging
import subprocess
from typing import List, Optional, Dict, Any

from .base import BaseLLMProvider

logger = logging.getLogger("event_horizon_core.providers.ollama")

class OllamaProvider(BaseLLMProvider):
    """
    Ollama-based Inference Engine.
    """

    def __init__(self, base_url: str = "http://127.0.0.1:11434", model: str = "llama3.2"):
        self.base_url = base_url
        self.model = model
        self.client = httpx.Client(timeout=60.0)

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        url = f"{self.base_url}/api/chat"
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.7),
                "num_predict": kwargs.get("max_tokens", 1000)
            }
        }

        try:
            response = self.client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"]
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
