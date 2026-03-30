import os
import logging
from typing import List, Optional
try:
    from mlx_lm import load, generate
except ImportError:
    load = None
    generate = None

from .base import BaseLLMProvider

logger = logging.getLogger("event_horizon_core.providers.mlx")

class MLXProvider(BaseLLMProvider):
    """
    Apple Silicon Native MLX Inference Engine.
    """

    def __init__(self, model_path: str = "mlx-community/Llama-3.2-3B-Instruct-4bit"):
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        
        if load is None:
            logger.warning("mlx_lm not installed. MLXProvider will be unavailable.")

    def _ensure_model(self):
        if self.model is None:
            if load is None:
                raise ImportError("mlx_lm is not installed. Please install it with 'pip install mlx-lm'.")
            logger.info(f"Loading MLX model: {self.model_path}")
            self.model, self.tokenizer = load(self.model_path)

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        self._ensure_model()
        
        # Prepare system prompt for Llama-style instruct models if applicable
        if system_prompt:
            formatted_prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
        else:
            formatted_prompt = prompt

        max_tokens = kwargs.get("max_tokens", 1000)
        return generate(self.model, self.tokenizer, prompt=formatted_prompt, verbose=False, max_tokens=max_tokens)

    def is_healthy(self) -> bool:
        return load is not None

    def list_models(self) -> List[str]:
        # Check ~/.cache/huggingface/hub for mlx models
        cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
        if not os.path.exists(cache_dir):
            return []
        
        models = [d for d in os.listdir(cache_dir) if "mlx" in d.lower()]
        return models
