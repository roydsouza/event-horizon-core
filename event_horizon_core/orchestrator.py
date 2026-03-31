import asyncio
import logging
import time
from typing import List, Optional, Dict, Any, Callable, Coroutine
from .providers.base import BaseLLMProvider

logger = logging.getLogger("event_horizon_core.orchestrator")

class LocalInferenceQueue:
    """
    Async Priority Queue & Semaphore for Apple Silicon GPU Orchestration.
    Ensures that N (default 2) local inference tasks can run concurrently 
    to prevent Metal shader thrashing and VRAM overflow.
    """
    
    def __init__(self, max_concurrent: int = 2):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.active_tasks = 0
        self.queue_depth = 0

    async def run_task(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        """
        Executes a synchronous provider call within the semaphore guard.
        """
        self.queue_depth += 1
        async with self.semaphore:
            self.queue_depth -= 1
            self.active_tasks += 1
            logger.info(f"[*] Starting local inference task (Active: {self.active_tasks}, Queue: {self.queue_depth})")
            
            try:
                # Providers are currently synchronous, so we run them in an executor
                loop = asyncio.get_running_loop()
                start_time = time.time()
                
                # Execute the provider's generate method
                result = await loop.run_in_executor(None, func, *args, **kwargs)
                
                duration = time.time() - start_time
                logger.debug(f"[+] Task completed in {duration:.2f}s")
                return result
            finally:
                self.active_tasks -= 1

class Orchestrator:
    """
    The Central Traffic Controller for Event Horizon.
    Manages the Fallback Hierarchy: MLX -> Ollama -> OpenRouter.
    """
    
    def __init__(self, local_queue: LocalInferenceQueue):
        self.queue = local_queue

    async def generate_with_fallback(
        self, 
        primary_provider: BaseLLMProvider,
        prompt: str,
        system_prompt: Optional[str] = None,
        fallback_provider: Optional[BaseLLMProvider] = None,
        timeout: float = 300.0,
        **kwargs
    ) -> Any: # Returns ProviderResponse
        """
        Attempts generation with the primary provider (local), 
        falling back to the secondary (remote) if the queue is too deep or local fails.
        """
        from .providers.base import ProviderResponse
        
        # Simple Logic: If local queue is too deep (> 3 waiting), 
        # and we have a fallback (OpenRouter), route it immediately.
        if self.queue.queue_depth > 3 and fallback_provider:
            logger.warning("[!] Local queue saturated. Routing to Fallback Provider (OpenRouter).")
            # Fallback (OpenRouter) is remote, so it doesn't need the local GPU semaphore
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, fallback_provider.generate, prompt, system_prompt, **kwargs)

        # Otherwise, wait for local GPU access
        try:
            return await asyncio.wait_for(
                self.queue.run_task(primary_provider.generate, prompt, system_prompt, **kwargs),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            if fallback_provider:
                logger.error(f"[!] Local task timed out after {timeout}s. Final fallback to OpenRouter.")
                loop = asyncio.get_running_loop()
                return await loop.run_in_executor(None, fallback_provider.generate, prompt, system_prompt, **kwargs)
            raise
