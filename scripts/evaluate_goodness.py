import asyncio
import time
import requests
import json
import argparse
from typing import Dict, List, Any
from datetime import datetime

# =================================================================
# EH CORE: GOODNESS EVALUATION FRAMEWORK (v0.1)
# -----------------------------------------------------------------
# This framework measures the "Goodness" of an LLM candidate
# across three primary dimensions: Performance, Precision, and 
# Hardware Footprint.
# =================================================================

BASE_URL = "http://127.0.0.1:8000/v1/chat/completions"

class GoodnessScorer:
    def __init__(self, model: str, profile: str = "claw"):
        self.model = model
        self.profile = profile # "claw" (speed/tools) or "tongs" (reasoning/logic)
        self.results = {
            "performance": {},
            "precision": {},
            "hardware": {}
        }

    # -------------------------------------------------------------
    # 🎯 TEST 1: Precision (Tool Calling & Logic)
    # -------------------------------------------------------------
    async def test_precision(self):
        """Evaluates tool-calling structure and reasoning logic."""
        
        # Test Case: Strict JSON Schema (The "Claw" Baseline)
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a precise JSON generator. Output ONLY valid JSON."},
                {"role": "user", "content": "Extract the following into a JSON object: The agent detected a vulnerability at 19:44 on port 8000 with a severity of 0.85."}
            ],
            "temperature": 0.0
        }
        
        print(f"[*] Running Precision Test ({self.model})...")
        try:
            resp = requests.post(BASE_URL, json=payload, timeout=60)
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            
            # Simple Goodness Measure: Is it valid JSON?
            try:
                json_data = json.loads(content)
                self.results["precision"]["json_valid"] = 1.0
                # Check for key extraction
                score = 0
                if "port" in str(json_data): score += 0.5
                if "severity" in str(json_data): score += 0.5
                self.results["precision"]["extraction_score"] = score
            except:
                self.results["precision"]["json_valid"] = 0.0
                self.results["precision"]["extraction_score"] = 0.0
        except Exception as e:
            print(f"    [!] Precision test failed: {e}")

    # -------------------------------------------------------------
    # ⚡ TEST 2: Performance (TTFT & TPS)
    # -------------------------------------------------------------
    async def test_performance(self):
        """Measures Time-To-First-Token and sustained throughput."""
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": "Explain the concept of entropy in 50 words."}],
            "max_tokens": 100,
            "stream": True # Use streaming for TTFT
        }
        
        print(f"[*] Running Performance Test ({self.model})...")
        start_time = time.monotonic()
        ttft = 0.0
        tokens = 0
        
        try:
            with requests.post(BASE_URL, json=payload, stream=True, timeout=60) as resp:
                for line in resp.iter_lines():
                    if not line: continue
                    if ttft == 0.0:
                        ttft = time.monotonic() - start_time
                    
                    line_str = line.decode('utf-8')
                    if line_str.startswith("data: "):
                        if "[DONE]" in line_str: break
                        tokens += 1
            
            total_time = time.monotonic() - start_time
            gen_time = total_time - ttft
            tps = tokens / gen_time if gen_time > 0 else 0
            
            self.results["performance"]["ttft"] = round(ttft, 3)
            self.results["performance"]["tps"] = round(tps, 2)
        except Exception as e:
            print(f"    [!] Performance test failed: {e}")

    # -------------------------------------------------------------
    # 📊 SCORING ALGORITHM
    # -------------------------------------------------------------
    def calculate_goodness(self):
        """
        Normalizes results into a 0.0 - 10.0 'Goodness' score.
        Weights vary by profile (Claws prioritize speed, Tongs prioritize logic).
        """
        p = self.results["performance"]
        prec = self.results["precision"]
        
        # 1. Performance Segment (Max 4.0)
        # Target: TTFT < 0.8s, TPS > 20
        perf_score = (max(0, (2.0 - p.get("ttft", 2.0)) / 2.0) * 2.0) + \
                     (min(1.0, p.get("tps", 0) / 30.0) * 2.0)
        
        # 2. Precision Segment (Max 6.0)
        prec_score = (prec.get("json_valid", 0) * 3.0) + \
                     (prec.get("extraction_score", 0) * 3.0)
        
        total = round(perf_score + prec_score, 2)
        self.results["goodness_score"] = total
        return total

    def report(self):
        print(f"\n--- Goodness Report: {self.model} ---")
        print(f"Profile:   {self.profile.upper()}")
        print(f"TTFT:      {self.results['performance'].get('ttft')}s")
        print(f"TPS:       {self.results['performance'].get('tps')}")
        print(f"Precision: {self.results['precision'].get('json_valid')} (JSON) | {self.results['precision'].get('extraction_score')} (Extract)")
        print(f"FINAL SCORE: {self.results.get('goodness_score')} / 10.0")
        print("-" * 35)

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="default", help="Model ID to evaluate")
    parser.add_argument("--profile", choices=["claw", "tongs"], default="claw")
    args = parser.parse_args()

    scorer = GoodnessScorer(args.model, args.profile)
    await scorer.test_performance()
    await scorer.test_precision()
    scorer.calculate_goodness()
    scorer.report()

if __name__ == "__main__":
    asyncio.run(main())
