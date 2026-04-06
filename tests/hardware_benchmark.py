import asyncio
import httpx
import time
import json
import statistics
from typing import List, Dict, Optional
from dataclasses import dataclass

# Target the Go proxy (Local-Only)
BASE_URL = "http://127.0.0.1:8000/v1/chat/completions"
DEFAULT_MODEL = "mlx-community/Llama-3.2-3B-Instruct-4bit"
SWAP_MODEL = "mlx-community/Llama-3.2-1B-Instruct-4bit"

@dataclass
class BenchmarkResult:
    agent_id: str
    ttft: float      # Time to first token
    total_time: float
    tokens: int
    tps: float       # Tokens per second
    status_code: int

async def stream_completion(client: httpx.AsyncClient, agent_id: str, model: str, prompt: str) -> Optional[BenchmarkResult]:
    """Measures TTFT and TPS via streaming."""
    headers = {"X-Agent-ID": agent_id}
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 100,
        "temperature": 0.0,
        "stream": True
    }
    
    start_time = time.monotonic()
    ttft = 0.0
    tokens = 0
    
    try:
        async with client.stream("POST", BASE_URL, json=payload, headers=headers, timeout=300.0) as response:
            if response.status_code != 200:
                print(f"[-] {agent_id} failed with status {response.status_code}")
                return None
                
            async for line in response.aiter_lines():
                if not line.strip(): continue
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]": break
                    
                    if ttft == 0.0:
                        ttft = time.monotonic() - start_time
                    
                    try:
                        data = json.loads(data_str)
                        content = data["choices"][0]["delta"].get("content", "")
                        if content:
                            tokens += 1
                    except Exception:
                        pass
                        
    except Exception as e:
        print(f"[-] {agent_id} error: {e}")
        return None
        
    total_time = time.monotonic() - start_time
    generation_time = total_time - ttft if ttft > 0 else 0
    tps = tokens / generation_time if generation_time > 0 else 0
    
    return BenchmarkResult(agent_id, ttft, total_time, tokens, tps, 200)

async def run_concurrency_test(num_clients: int):
    print(f"\n[STRESS] Running Concurrency Test with {num_clients} clients...")
    prompt = "Write a 50-word technical summary of a kernel bypass."
    
    async with httpx.AsyncClient() as client:
        tasks = [stream_completion(client, f"stress_agent_{i}", DEFAULT_MODEL, prompt) for i in range(num_clients)]
        results = await asyncio.gather(*tasks)
        
    valid = [r for r in results if r]
    if not valid:
        print("[-] All requests failed.")
        return
        
    ttfts = [r.ttft for r in valid]
    tps_vals = [r.tps for r in valid]
    totals = [r.total_time for r in valid]
    
    print(f"  -> Results ({len(valid)}/{num_clients} success):")
    print(f"     P50 TTFT:  {statistics.median(ttfts):.3f}s")
    print(f"     P95 TTFT:  {max(ttfts):.3f}s")
    print(f"     Avg TPS:   {statistics.mean(tps_vals):.1f} tok/s")
    print(f"     Max Total: {max(totals):.2f}s")

async def run_swap_test():
    print(f"\n[SWAP] Running Model Hot-Swap Benchmark...")
    prompt = "Reply 'Ready'"
    
    async with httpx.AsyncClient() as client:
        # 1. Warm up Primary model
        print(f"[*] Ensuring {DEFAULT_MODEL} is warm...")
        await stream_completion(client, "warmup", DEFAULT_MODEL, prompt)
        
        # 2. Trigger swap to 1B model
        print(f"[*] Swapping to {SWAP_MODEL}...")
        res1 = await stream_completion(client, "swapper_1", SWAP_MODEL, prompt)
        if res1:
            print(f"  -> Hot-Swap Latency: {res1.total_time:.2f}s (TTFT: {res1.ttft:.3f}s)")
            
        # 3. Swap back to 3B model
        print(f"[*] Swapping back to {DEFAULT_MODEL}...")
        res2 = await stream_completion(client, "swapper_2", DEFAULT_MODEL, prompt)
        if res2:
            print(f"  -> Re-Swap Latency:  {res2.total_time:.2f}s (TTFT: {res2.ttft:.3f}s)")

async def main():
    print("=== Event Horizon Core: Hardware Performance Suite ===")
    print("[*] Target: Go Substrate on 127.0.0.1:8000")
    
    # 1. Base Concurrency (Nominal load)
    await run_concurrency_test(3)
    
    # 2. Saturation Concurrency (High load)
    await run_concurrency_test(10)
    
    # 3. Swapping Performance
    await run_swap_test()

if __name__ == "__main__":
    asyncio.run(main())
