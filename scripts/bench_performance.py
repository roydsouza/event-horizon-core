import asyncio
import time
import requests
import json
import argparse
from datetime import datetime

# EH Core Performance Benchmarker (Streamlined for MLX & OpenRouter)
BENCHMARK_PROMPT = "Write a 100-word story about a robot discovering a soul."
BASE_URL = "http://127.0.0.1:8000"

async def run_benchmark(model: str):
    print(f"[*] Benchmarking Model: {model}...")
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": BENCHMARK_PROMPT}],
        "max_tokens": 100,
        "temperature": 0.7
    }

    try:
        start_time = time.time()
        resp = requests.post(f"{BASE_URL}/v1/chat/completions", json=payload, timeout=300)
        resp.raise_for_status()
        total_time = time.time() - start_time
        
        data = resp.json()
        usage = data.get("usage", {})
        total_tokens = usage.get("total_tokens", 0)
        tps = total_tokens / total_time if total_time > 0 else 0
        
        print(f"    [+] Response Received.")
        print(f"    [+] Tokens: {total_tokens}")
        print(f"    [+] total_time: {total_time:.2f}s")
        print(f"    [+] Speed: {tps:.2f} tok/s (End-to-End)")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "tokens": total_tokens,
            "latency": f"{total_time:.4f}",
            "tps": f"{tps:.2f}"
        }
    except Exception as e:
        print(f"    [!] Error benchmarking {model}: {e}")
        return None

async def main():
    parser = argparse.ArgumentParser(description="EH Core Performance Benchmarker")
    parser.add_argument("--model", help="Specific model to benchmark (Local Path or Alias)")
    parser.add_argument("--all", action="store_true", help="Benchmark default suite")
    args = parser.parse_args()

    results = []
    if args.all:
        # Default representative suite
        models = ["mlx-community/Llama-3.2-1B-Instruct-4bit", "free", "best"]
        for m in models:
            res = await run_benchmark(m)
            results.append(res)
    elif args.model:
        res = await run_benchmark(args.model)
        results.append(res)
    else:
        # Default to Current MLX
        res = await run_benchmark("default")
        results.append(res)

    print("\n--- Summary ---")
    for r in results:
        if r:
            print(f"Model: {r['model']} | Speed: {r['tps']} tok/s | Latency: {r['latency']}s")

if __name__ == "__main__":
    asyncio.run(main())
