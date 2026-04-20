import argparse
import json
import os
import urllib.request
import urllib.error
from dotenv import load_dotenv

def get_metrics(admin_token):
    req = urllib.request.Request("http://127.0.0.1:8000/metrics/agents")
    req.add_header("X-EHC-Admin-Token", admin_token)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.URLError as e:
        print(f"Error fetching metrics: {e}")
        return None

def calc_goodness(metrics, reasoning_score):
    # Retrieve metrics safely
    tps = metrics.get('avg_tps', 0)
    ttft = metrics.get('avg_ttft_ms', 0)

    # Weights
    W_reasoning = 0.50
    W_tps = 0.30
    
    # Normalize TPS (Assume 50 TPS is perfect score of 100)
    Target_Max_TPS = 50.0
    tps_normalized = min((tps / Target_Max_TPS) * 100, 100)

    # Penalty for TTFT (> 800ms)
    Tolerance_Gap = 800
    Penalty_Weight = 0.05
    ttft_penalty = max(0, (ttft - Tolerance_Gap) * Penalty_Weight)

    # Base formula
    gs = (reasoning_score * W_reasoning) + (tps_normalized * W_tps) - ttft_penalty

    return {
        "score": max(0, min(100, gs)),  # Clamp 0-100
        "reasoning": reasoning_score,
        "tps": tps,
        "tps_normalized": tps_normalized,
        "ttft": ttft,
        "ttft_penalty": ttft_penalty
    }

def main():
    load_dotenv()
    admin_token = os.environ.get("EHC_ADMIN_TOKEN", "")
    
    if not admin_token:
        print("Error: EHC_ADMIN_TOKEN environment variable not set. Please set it in .env or your environment.")
        return

    parser = argparse.ArgumentParser(description="Calculate Event Horizon Component Goodness Profiles.")
    parser.add_argument("--score", type=float, help="Subjective Reasoning/Quality Score (1-100).", default=None)
    parser.add_argument("--agent", type=str, help="Specifically fetch telemetry for an individual agent.", default=None)
    args = parser.parse_args()

    scoring = args.score
    if scoring is None:
        try:
            val = input("Enter Qualitative Reasoning Score (1-100) for this benchmarking run: ")
            scoring = float(val)
        except ValueError:
            print("Invalid score provided. Terminating.")
            return

    data = get_metrics(admin_token)
    if not data:
        print("No robust telemetry found from EHC. Is the core running on Port 8000?")
        return
        
    agents_to_run = [args.agent] if args.agent else data.keys()

    print("\n" + "="*50)
    print(" 🌟 EVENT HORIZON GOODNESS METRICS")
    print("="*50)
    for agent in agents_to_run:
        if agent not in data:
            print(f"Skipping '{agent}': No telemetry currently isolated for this agent.")
            continue
            
        res = calc_goodness(data[agent], scoring)
        print(f"\n[ Agent: {agent} ]")
        print(f"  Reasoning Input: {res['reasoning']:.1f}/100")
        print(f"  Empirical TPS:   {res['tps']:.1f} (Norm: {res['tps_normalized']:.1f}/100)")
        print(f"  Empirical TTFT:  {res['ttft']}ms (Penalty: -{res['ttft_penalty']:.1f})")
        print(f"  -------------------------------------------")
        print(f"  FINAL GOODNESS SCORE: {res['score']:.2f} / 100")

    print("\n" + "="*50)

if __name__ == "__main__":
    main()
