# 🚀 EHC Enhancements Roadmap

This document outlines the planned technical expansions for **Event Horizon Core (EHC)** to ensure high-concurrency autonomy for the "Claw" agent family (ZeroClaw, OpenClaw, NanoClaw, etc.) and OpenFang.

---

## 🏗️ Priority 1: Embeddings API (`/v1/embeddings`)
**Goal**: Provide a zero-cost, local endpoint for text vectorization to support RAG and agentic memory.

- **Objective**: Standardize on a high-performance, small-footprint embedding model (e.g., `sentence-transformers/all-MiniLM-L6-v2` or `BGE-Small`).
- **Implementation**: 
    - Expose `/v1/embeddings` on Port 8000.
    - Leverage **MLX** or a dedicated **Go-based CGO** binding for BERT/MiniLM to keep overhead minimal.
    - **Agent Impact**: Enables **ZeroClaw** to maintain a persistent memory buffer without external API dependencies.

## 🛠️ Priority 2: Hardened Tool-Calling Schema
**Goal**: Guarantee reliable function-calling for reasoning agents.

- **Objective**: Ensure MLX output is strictly validated against the `tools` schema provided in the request.
- **Implementation**: 
    - Middleware validation for `tool_calls` in the response stream.
    - **Expert Mapping**: Create a global alias for a "tooling-expert" model (e.g., `Mistral-7B-Instruct-v0.3`) optimized for JSON-RPC extraction.
    - **Agent Impact**: Drastically reduces "hallucination" in **OpenClaw** and **Hermes Agent** during complex multi-step tasks.

## 🖼️ Priority 3: Multimodal/Vision Support (`/v1/chat/completions` + Images)
**Goal**: Allow agents to "see" screenshots and local visual data.

- **Objective**: Support `base64` image inputs in the OpenAI-compatible message array.
- **Implementation**: 
    - Integrate supervised support for **MLX-V** (Vision) models (e.g., `Gemma-2-2B-V` or `Llama-3.2-Vision`).
    - **Agent Impact**: Essential for **OpenFang** and **Picoclaw**OS-level control tasks.

---

## 📈 Long-Term Research
- **Dynamic KV Cache Swapping**: Researching the ability to save/load specific agent contexts to SSD on-the-fly to exceed the 24GB M5 VRAM limitation.
- **Speculative Decoding Expansion**: Investigating the use of a 1B "draft" model (Small) to accelerate a 15B "reasoning" model (Large) via the Go supervisor.
