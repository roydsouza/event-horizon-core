import asyncio
import httpx
import time
import json
import statistics
import subprocess
import os

# "Decode, Normalize, Socialize"
# Mapped fictitious 2026 models to real, canonical MLX high-performance repos
CANDIDATES = {
    "OpenClaw_Primary": "mlx-community/Qwen2.5-Coder-32B-Instruct-4bit",
    "OpenFang_Hybrid":  "mlx-community/Qwen2.5-32B-Instruct-4bit",
    "Hermes_Native":    "mlx-community/Hermes-3-Llama-3.1-8B-4bit",
    "Balanced_Gemma":   "mlx-community/gemma-2-27b-it-4bit",
    "Fast_Scout":       "mlx-community/Mistral-Nemo-Instruct-2407-4bit"
}

BASE_URL = "http://127.0.0.1:8000/v1/chat/completions"

async def stream_completion(client: httpx.AsyncClient, agent_id: str, model: str, prompt: str):
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
                    if ttft == 0.0: ttft = time.monotonic() - start_time
                    
                    try:
                        data = json.loads(data_str)
                        content = data["choices"][0]["delta"].get("content", "")
                        if content: tokens += 1
                    except Exception:
                        pass
    except Exception as e:
        print(f"[-] {agent_id} error: {e}")
        return None
        
    total_time = time.monotonic() - start_time
    generation_time = total_time - ttft if ttft > 0 else 0
    tps = tokens / generation_time if generation_time > 0 else 0
    
    return {"ttft": ttft, "tps": tps, "total": total_time}

async def benchmark_model(model_name: str, repo: str) -> dict:
    print(f"\n=======================================================")
    print(f"[*] Benchmarking: {model_name} ({repo})")
    print(f"=======================================================")
    
    # Pre-fetch the prompt to trigger Go proxy model swap and full Metal load
    print("[1/2] Triggering Model Swap and Single-Client Baseline...")
    async with httpx.AsyncClient() as client:
        # Initial cold start / swap
        single_res = await stream_completion(client, "warmup", repo, "Explain quantum states in one sentence.")
        if not single_res:
            print("[-] Model failed to load.")
            return None
        
        print(f"  -> Cold Swap + First TTFT: {single_res['ttft']:.3f}s")
        print(f"  -> Single TPS: {single_res['tps']:.1f} tok/s")
        
        # Concurrency Test (5 clients)
        print("\n[2/2] Running 5-Client Concurrency Stress (VRAM Guard = 22GB)...")
        tasks = [stream_completion(client, f"stress_{i}", repo, "Write a 50-word Python snippet for sorting.") for i in range(5)]
        results = await asyncio.gather(*tasks)
        
    valid = [r for r in results if r]
    if not valid:
        print("[-] All stress requests failed.")
        return None
        
    avg_ttft = statistics.mean([r['ttft'] for r in valid])
    avg_tps = statistics.mean([r['tps'] for r in valid])
    
    print(f"  -> Results ({len(valid)}/5 success):")
    print(f"     Avg TTFT: {avg_ttft:.3f}s")
    print(f"     Avg TPS:  {avg_tps:.1f} tok/s")
    
    return {
        "model": model_name,
        "repo": repo,
        "swap_latency": single_res['ttft'],
        "single_tps": single_res['tps'],
        "stress_ttft_avg": avg_ttft,
        "stress_tps_avg": avg_tps,
        "success_rate": f"{len(valid)}/5"
    }

from huggingface_hub import snapshot_download

async def pre_fetch_weights():
    print("[*] Pre-fetching HF Weights (this may take over an hour)...")
    for name, repo in CANDIDATES.items():
        print(f"  -> Downloading {repo}...")
        try:
            # Use native python API to avoid PATH subprocess issues
            snapshot_download(repo_id=repo)
        except Exception as e:
            print(f"[-] Failed to download {repo}: {e}")

async def main():
    print("=== Phase 12: Candidate LLM Evaluation ===")
    
    # 1. Download all weights locally first
    await pre_fetch_weights()
    
    # 2. Run sequential benchmarks
    final_results = []
    for name, repo in CANDIDATES.items():
        res = await benchmark_model(name, repo)
        if res: final_results.append(res)
        
    # 3. Output Markdown Results
    with open("docs/research/llm_candidate_results.md", "w") as f:
        f.write("# LLM Candidate Evaluation (Phase 12)\n\n")
        f.write("Evaluation of top 5 canonical equivalents on M5 24GB.\n\n")
        f.write("| Profile | Repo | Hot-Swap Latency | Single TPS | 5-Client TTFT | 5-Client TPS | Success Rate |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for r in final_results:
            f.write(f"| {r['model']} | `{r['repo']}` | {r['swap_latency']:.2f}s | {r['single_tps']:.1f} | {r['stress_ttft_avg']:.2f}s | {r['stress_tps_avg']:.1f} | {r['success_rate']} |\n")

    print("\n[+] Verification complete. Results saved to docs/research/llm_candidate_results.md.")

if __name__ == "__main__":
    asyncio.run(main())
