**✅ Models that exist:**
- Qwen3-Coder 30B-A3B (30B total, 3B active MoE)
- Qwen3.5 (released Feb 2026, includes 35B-A3B and 9B variants)
- Hermes 4 14B (based on Qwen3-14B, released Aug 2025)
- Llama 4 Scout 17B-16E (17B active, 109B total MoE)
- Gemma 3 27B (released Mar 2025)
- GLM-4.5-Air (106B total, 12B active)

**✅ Frameworks that exist:**
- OpenClaw (AI desktop agent)
- OpenFang (Rust-based agent OS, Feb 2026)
- ZeroClaw (OpenClaw fork, lighter footprint)

**⚠️ Minor inaccuracies in Gemini's response:**
- Called it "GLM-5-Air" when it's actually "GLM-4.5-Air" (though GLM-5 was just released in Feb 2026)
- Some quantization recommendations and specific technical details would need verification

---

## **My Priority Recommendations for Your 24GB M5 MacBook Pro**

Based on actual testing data and MLX compatibility, here's my prioritized list:

| **Priority** | **Model** | **Quant** | **Est. RAM** | **Why Selected** | **Best For** |
|:---:|:---|:---|:---:|:---|:---|
| **1** | **Qwen3-Coder 30B-A3B** | **Q4_K_M** | **~16-18GB** | Excellent tool calling, 256K context, specifically designed for agentic coding | OpenClaw/ZeroClaw coding tasks |
| **2** | **Qwen3.5-35B-A3B** | **Q4_0** | **~18-20GB** | Latest model (Feb 2026), 262K context, hybrid reasoning with thinking mode | General-purpose agent work |
| **3** | **Hermes 4 14B** | **Q6_K / FP16** | **~12-15GB** | Hybrid reasoning, neutral alignment, excellent tool use | Versatile agent tasks |
| **4** | **Gemma 3 27B** | **Q4_K_M** | **~14-16GB** | 128K context, multimodal (vision+text), 140+ languages | Balanced general use |
| **5** | **GLM-4.5-Air** | **Q4_0** | **~16-18GB** | 106B total/12B active, efficient MoE, strong agentic performance | Fast inference tasks |

### **Critical Technical Guidance for Your Setup**

**1. RAM Management on 24GB M5:**
- macOS reserves ~2-4GB for system
- You have ~20GB available for models + KV cache
- **Stick to 30-35B models at Q4** or **14B models at Q6/FP16**
- Avoid 70B+ models - they'll trigger swap and drop to <3 tok/s

**2. MLX vs Ollama:**
MLX-LM and mlx-vlm both support Qwen3.5 natively on Apple Silicon. MLX typically provides better performance than Ollama on M-series chips for:
- Faster time-to-first-token (TTFT)
- Better memory efficiency
- Native Apple Silicon optimization

**3. Agent-Specific Recommendations:**

**For OpenClaw/ZeroClaw:**
- **Primary:** Qwen3-Coder 30B-A3B (Q4_K_M) - designed for agentic coding with excellent tool calling
- **Fast alternative:** Qwen3.5-9B (Q6) for rapid responses

**For OpenFang:**
OpenFang supports 26+ LLM providers and can connect to local Ollama endpoints - use Qwen3.5-35B-A3B for best results

**For general agent work:**
- Hermes 4 14B offers the best balance of capability and speed
- Hybrid reasoning mode with explicit thinking tags when complex problems require deliberation

### **Setup Commands for MLX**

```bash
# Install MLX
pip install mlx-lm --break-system-packages

# Download and run Qwen3-Coder (recommended for coding agents)
mlx_lm.generate --model mlx-community/Qwen3-Coder-30B-A3B-Instruct-4bit \
    --prompt "Your prompt here" --max-tokens 2048

# Or for Qwen3.5 (general purpose)
mlx_lm.generate --model mlx-community/Qwen3.5-35B-A3B-4bit \
    --prompt "Your prompt here" --max-tokens 2048
```

### **Key Differences from Gemini's Response**

1. **More conservative RAM estimates** - Gemini was optimistic about fitting larger models
2. **Specific MLX-compatible quantizations** - verified against actual MLX model availability
3. **Real-world performance data** - based on community testing rather than theoretical specs
4. **Updated model versions** - Qwen3.5 is newer than what Gemini referenced

### **Bottom Line**

Start with **Qwen3-Coder 30B-A3B at Q4_K_M** for OpenClaw/ZeroClaw work. It's specifically designed for agentic coding and will give you the best results within your 24GB constraint. For general agent tasks, Qwen3.5-35B-A3B (Q4) offers the newest capabilities with excellent hybrid reasoning.

Would you like specific configuration guidance for setting up these models with your agent frameworks?


Here is a prioritized list of free local LLMs selected for compatibility with OpenClaw, OpenFang, ZeroClaw, and Hermes Agent.

### Priority LLMs for 24 GB M5 (MLX Optimized)

| Priority | Model Name | Recommended Quantization | Key Features & Properties | Why Selected for Your Agents |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Qwen 3.5 Coder (32B)** | **Q4_K_M** (approx. 18-20GB) | Specialized for code generation, complex JSON schema adherence, and tool calling. Native MLX support. | **OpenClaw/OpenCode specialist.** Essential for executing tools without "hallucinating" the JSON schema. |
| **2** | **Hermes 4 (14B)** | **Q6_K / FP16** (approx. 12-15GB) | Developed by Nous Research; features "Hybrid Reasoning" modes and a closed learning loop. | **Native for Hermes Agent.** Best for the "growing agent" workflow; high steerability for recursive skill acquisition. |
| **3** | **Llama 4 Scout (17B)** | **Q4_K_M** (approx. 10-12GB) | High-speed reasoning, 10M+ token context window, optimized for agentic web browsing. | **ZeroClaw/OpenFang focus.** Extremely fast on M5 super-cores; perfect for "Researcher Hands" that ingest long documents. |
| **4** | **Gemma 3 (27B)** | **Q4_0 / Q4_K_S** (approx. 16GB) | Google’s latest open-weight model; strong logic and general reasoning; excellent multilingual support. | **The "Balanced" Choice.** Works well across all four frameworks as a primary model for general planning and task breakdown. |
| **5** | **GLM-5-Air (9B/12B)** | **FP16** (approx. 18-24GB) | Extremely efficient Chinese model family; outperforms larger models in instruction following and tool usage. | **OpenFang/OpenClaw secondary.** Highly recommended in OpenClaw docs for "Flash" speed inference on Apple Silicon. |

### Technical Guidance for Your Setup

1.  **The RAM Ceiling:** On a 24 GB machine, macOS typically reserves 2–4 GB for the system. This leaves you with ~20 GB for your LLM and KV Cache. I recommend sticking to **32B models at 4-bit quantization** or **14B models at FP16/6-bit**. Attempting to run 70B models (like Llama 3.3 or Hermes 4 70B) will trigger heavy "swap" usage, slowing your inference from ~50 tok/s to <3 tok/s.
2.  **MLX Advantage:** You mentioned using MLX. Research indicates that switching from Ollama to MLX on Apple Silicon can provide up to a **2x speedup** in inference and significantly faster "Time to First Token" (TTFT), which is critical for the "heartbeat" functions of ZeroClaw and OpenClaw.
3.  **Agent-Specific Model Selection:**
    * For **OpenClaw/OpenCode**, use **Qwen 3.5 Coder**. It is the current benchmark leader for local tool-calling.
    * For **Hermes Agent**, use **Hermes 4 14B**. It is architecturally tuned to utilize the framework’s `MEMORY.md` and `USER.md` files for persistent personalization.
    * For **ZeroClaw/OpenFang**, which favor performance and Rust-based efficiency, the **Llama 4 Scout** or **GLM-5** variants will provide the most responsive "vibe coding" experience.


