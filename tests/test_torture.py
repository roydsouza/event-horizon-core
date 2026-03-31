import asyncio
import pytest
import os
from event_horizon_core.factory import LLMFactory

@pytest.mark.asyncio
async def test_torture_ollama_concurrency():
    """
    Stress test Ollama with multiple concurrent requests to verify internal queueing.
    """
    provider = LLMFactory.get_provider("ollama", model="llama3.1:latest")
    
    # 5 concurrent requests
    prompts = [
        "Explain quantum entanglement simply.",
        "Write a 500 word story about a lost robot.",
        "List 10 ways to secure a Linux server.",
        "Summarize the history of the Apple Silicon M5.",
        "Write a complex Rust trait for an event bus."
    ]
    
    async def call_generate(prompt):
        # We wrap the synchronous generate call in a thread pool executor
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, provider.generate, prompt)

    print("\n[*] Starting 5 concurrent Ollama calls...")
    tasks = [call_generate(p) for p in prompts]
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    for i, res in enumerate(responses):
        if isinstance(res, Exception):
            print(f"[-] Request {i} failed: {res}")
        else:
            print(f"[+] Request {i} completed: {len(res)} characters")
    
    assert all(not isinstance(r, Exception) for r in responses)

@pytest.mark.asyncio
async def test_torture_mlx_concurrency_race():
    """
    Stress test MLX with concurrent requests to see how it handles Metal lock contention.
    Expectation: Currently might fail or bottleneck.
    """
    provider = LLMFactory.get_provider("mlx")
    
    async def call_generate(prompt):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, provider.generate, prompt)

    print("\n[*] Starting 2 concurrent MLX calls (The Race)...")
    tasks = [
        call_generate("Analyze this log file for security threats: 'Connection timed out for user root'"),
        call_generate("Refactor this python script to use async/await.")
    ]
    
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    for i, res in enumerate(responses):
        if isinstance(res, Exception):
            print(f"[-] MLX Request {i} failed (expected-ish): {res}")
        else:
            print(f"[+] MLX Request {i} completed: {len(res)} characters")

@pytest.mark.asyncio
async def test_torture_mixed_load():
    """
    Test mixed load of local (Ollama) and remote (OpenRouter) if configured.
    """
    if not os.environ.get("OPENROUTER_API_KEY"):
        pytest.skip("OpenRouter API key not set - skipping mixed load.")

    ollama = LLMFactory.get_provider("ollama")
    openrouter = LLMFactory.get_provider("openrouter")

    async def call_gen(provider, prompt):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, provider.generate, prompt)

    print("\n[*] Starting Mixed Load (Ollama + OpenRouter)...")
    tasks = [
        call_gen(ollama, "Count to 10."),
        call_gen(openrouter, "Explain the Fermi Paradox.")
    ]
    
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    assert all(not isinstance(r, Exception) for r in responses)
