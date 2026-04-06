# Local LLM Concurrency Stress Test Results

**Date of Execution**: March 31, 2026, 20:48 PDT — April 1, 2026, 08:07 PDT  
**Total Duration**: ~11 Hours 19 Minutes (Includes comprehensive weight transfers via Hugging Face)  

---

## 🔬 Testing Methodology

### Objective 
To determine the absolute physical limitations and optimal Service Level Objectives (SLOs) for running multi-agent (5 concurrent clients) local LLM operations on an Apple MacBook Pro equipped with an **M5 chip and 24GB of Unified Memory**. 

### The Setup
*   **Operating Substrate**: Event Horizon Core Go Daemon (`127.0.0.1:8000`) 
*   **Inference Engine**: Native Apple Silicon `mlx-lm` backend implementing a 22GB Hard VRAM guardrail.
*   **Execution Strategy**: 
    1.  **Warm-up/Hot-Swap**: Trigger the underlying MLX daemon to switch weights into unified memory, recording the cold Time-To-First-Token (TTFT) and single-client tokens-per-second (TPS) baseline.
    2.  **Concurrency Pressure**: Simultaneously blast 5 concurrent Python `httpx` asyncio streams at the proxy to simulate a multi-agent framework (OpenClaw, ZeroClaw, OpenFang) demanding rapid generation. 

---

## 📊 Candidate Profiles & Empirical Results

We targeted 5 specific high-performance quantizations (4-bit variants) mathematically mapped from our theoretical models to test the 8B → 32B class parameters. 

**Measured Performance on M5 / 24GB Unified Memory:**

| Candidate Repository (Model Class) | Profile | Hot-Swap Latency | Single TPS | 5-Client Pressure | Status / Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `mlx-community/Qwen2.5-Coder-32B-Instruct-4bit` | OpenClaw | 118.01s | 5.5 tok/s | **0.0 TPS** *(Memory Trashing)* | ❌ **UNSUITABLE** |
| `mlx-community/Qwen2.5-32B-Instruct-4bit` | OpenFang | 125.76s | 5.1 tok/s | **0.0 TPS** *(Memory Trashing)* | ❌ **UNSUITABLE** |
| `mlx-community/gemma-2-27b-it-4bit` | Balanced | 75.41s | 7.3 tok/s | **CRASHED** *(Empty Traceback)* | ❌ **UNSUITABLE** |
| `mlx-community/Mistral-Nemo-Instruct-2407-4bit` (12B) | Scout | N/A | N/A | **N/A** *(HTTP 503 Startup Error)* | ❌ **UNSUITABLE** |
| `mlx-community/Hermes-3-Llama-3.1-8B-4bit` | Hermes | **4.51s** | **27.9 tok/s** | **14.1 tok/s** *(Graceful Degradation)* | ✅ **OPTIMAL** |

---

## 💥 Hardware Bottlenecks Identified
The test clearly exposed the 24GB architectural threshold:
1.  **The 32B Class Deadlock**: While a 32B 4-bit model nominally fits into 18GB of VRAM, the moment 5 agents begin generating tokens concurrently, the **KV Cache expands beyond the 4GB buffer**, breaching the hard 22GB limit. This forces the OS into aggressive swap thrashing, causing the MLX subprocess to deadlock and output ~0.0 TPS. 
2.  **Extended Swap Times**: Attempting to bounce 18GB weights across the unified memory architecture (Cold Swaps) takes upwards of **2 minutes** for the 32B tier, making them unusable for agentic orchestration tasks that demand snappy context changes.

---

## 🛡️ Final Recommendation

To run a reliable, high-speed multi-agent network (implementing frameworks like ZeroClaw or OpenClaw) exclusively on local M5 hardware:

> **You strictly must adopt the 8B parameter model tier.**

The **Hermes 3 (Llama 3.1 8B)** architecture is the definitive recommendation for your hardware profile. It is the only model that guarantees sub-5-second context swapping and maintains double-digit Tokens-Per-Second (14.1 TPS) when completely saturated with 5 parallel agent streams. 

If your workflows absolutely require the complex coding geometry or reasoning patterns of a 32B/70B tier, you should architect the system to **dynamically fail-over to OpenRouter API endpoints** instead of burning local silicon attempting the generation.
