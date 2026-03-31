import asyncio
import httpx
import time
from typing import List, Dict

async def fetch_completion(client: httpx.AsyncClient, agent_id: str, prompt: str):
    url = "http://127.0.0.1:8080/v1/chat/completions"
    headers = {"X-Agent-ID": agent_id}
    payload = {
        "model": "mlx-community/Llama-3.2-3B-Instruct-4bit",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 100,
        "temperature": 0.0 # Deterministic for benchmark
    }
    
    start_time = time.monotonic()
    try:
        response = await client.post(url, json=payload, headers=headers, timeout=300.0)
        duration = time.monotonic() - start_time
        if response.status_code == 200:
            print(f"[+] Agent {agent_id} completed in {duration:.2f}s")
            return duration
        else:
            print(f"[-] Agent {agent_id} failed: {response.text}")
            return None
    except Exception as e:
        print(f"[-] Agent {agent_id} error: {e}")
        return None

async def run_benchmark(num_agents: int = 3):
    print(f"[*] Starting Native Server Benchmark with {num_agents} agents...")
    prompt = "Write a 50-word story about a rogue AI on an M5 Mac."
    
    async with httpx.AsyncClient() as client:
        tasks = [fetch_completion(client, f"agent_{i}", prompt) for i in range(num_agents)]
        results = await asyncio.gather(*tasks)
        
    valid_results = [r for r in results if r is not None]
    if valid_results:
        avg = sum(valid_results) / len(valid_results)
        print(f"\n[SUMMARY] Avg Latency: {avg:.2f}s | Success: {len(valid_results)}/{num_agents}")
        return avg
    return None

if __name__ == "__main__":
    asyncio.run(run_benchmark())
