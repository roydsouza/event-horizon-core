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

    def __init__(self, model_path: str = "mlx-community/Llama-3.2-3B-Instruct-4bit", **kwargs):
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        
        if load is None:
            logger.warning("mlx_lm not installed. MLXProvider will be unavailable.")

    def get_vram_estimate(self) -> float:
        """
        Estimates VRAM usage based on parameter count.
        For 4-bit models, it's roughly 0.6 GB per 1B parameters + 1GB overhead.
        """
        # Extract parameter count from path if possible (e.g. 3B, 8B, 70B)
        import re
        match = re.search(r"(\d+)[Bb]", self.model_path)
        if match:
            params = int(match.group(1))
            return (params * 0.6) + 1.5 # 1.5GB overhead for KV cache/Metal
        return 4.0 # Default fallback

    def _ensure_model(self):
        if self.model is None:
            if load is None:
                raise ImportError("mlx_lm is not installed. Please install it with 'pip install mlx-lm'.")
            
            # Hardware Guard (Apple Silicon M5 24GB)
            estimate = self.get_vram_estimate()
            if estimate > 22.0: # Leaving 2GB buffer for OS/UI
                raise MemoryError(f"Model {self.model_path} estimated VRAM ({estimate}GB) exceeds safe limit (22GB).")
            
            logger.info(f"Loading MLX model: {self.model_path} (Est. VRAM: {estimate}GB)")
            self.model, self.tokenizer = load(self.model_path)

    def generate(self, prompt: str, system_prompt: Optional[str] = None, tools: Optional[List[Dict[str, Any]]] = None, **kwargs) -> str:
        self._ensure_model()
        
        # Prepare system prompt for Llama-style instruct models if applicable
        if system_prompt:
            formatted_prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
        else:
            formatted_prompt = prompt

        max_tokens = kwargs.get("max_tokens", 1000)
        temp = kwargs.get("temperature", 0.7)
        return generate(self.model, self.tokenizer, prompt=formatted_prompt, verbose=False, max_tokens=max_tokens, temp=temp)

    def is_healthy(self) -> bool:
        return load is not None

    def list_models(self) -> List[str]:
        # Check ~/.cache/huggingface/hub for mlx models
        cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
        if not os.path.exists(cache_dir):
            return []
        
        models = [d for d in os.listdir(cache_dir) if "mlx" in d.lower()]
        return models
