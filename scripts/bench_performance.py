import asyncio
import time
import csv
import os
import argparse
from datetime import datetime
from event_horizon_core.factory import LLMFactory
from event_horizon_core.orchestrator import Orchestrator, LocalInferenceQueue

# Configure Orchestrator
ORCHESTRATOR = Orchestrator(LocalInferenceQueue(max_concurrent=1))

BENCHMARK_PROMPT = "Write a 100-word story about a robot discovering a soul."
CSV_FILE = "benchmarks.csv"

async def run_benchmark(provider_name: str, model: str = None):
    print(f"[*] Benchmarking {provider_name.upper()}...")
    
    kwargs = {"max_tokens": 300}
    if model:
        if provider_name == "mlx":
            kwargs["model_path"] = model
        else:
            kwargs["model"] = model

    try:
        engine = LLMFactory.get_provider(provider_name, **kwargs)
        if not engine.is_healthy():
            print(f"[!] {provider_name} is unhealthy/offline. Skipping.")
            return None

        # Measure
        start_time = time.time()
        response = await ORCHESTRATOR.generate_with_fallback(engine, BENCHMARK_PROMPT)
        total_time = time.time() - start_time
        
        usage = response.usage
        tps = usage.tokens_per_second
        
        print(f"    [+] Model: {response.model}")
        print(f"    [+] Tokens: {usage.total_tokens}")
        print(f"    [+] Speed: {tps:.2f} tok/s")
        print(f"    [+] Latency: {usage.generation_time:.2f}s")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "provider": provider_name,
            "model": response.model,
            "tokens": usage.total_tokens,
            "latency": f"{usage.generation_time:.4f}",
            "tps": f"{tps:.2f}"
        }
    except Exception as e:
        print(f"    [!] Error benchmarking {provider_name}: {e}")
        return None

def save_results(results):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode='a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "provider", "model", "tokens", "latency", "tps"])
        if not file_exists:
            writer.writeheader()
        for r in results:
            if r:
                writer.writerow(r)
    print(f"\n[!] Results saved to {CSV_FILE}")

async def main():
    parser = argparse.ArgumentParser(description="EH Core Performance Benchmarker")
    parser.add_argument("--provider", help="Specific provider to benchmark (mlx, ollama, openrouter)")
    parser.add_argument("--all", action="store_true", help="Benchmark all healthy providers")
    args = parser.parse_args()

    results = []
    if args.all:
        for p in ["mlx", "llamacpp", "ollama", "openrouter"]:
            res = await run_benchmark(p)
            results.append(res)
    elif args.provider:
        res = await run_benchmark(args.provider)
        results.append(res)
    else:
        # Default to MLX
        res = await run_benchmark("mlx")
        results.append(res)

    save_results([r for r in results if r])

if __name__ == "__main__":
    asyncio.run(main())
