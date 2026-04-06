# EHC Solution Architectures

> **Purpose:** Volatile, open-ended research catalog. Records all proposed, prototyped, 
> and historical technical designs for Event Horizon Core and its neighbors. 
> This is a living document for brainstorming and deep-diving into individual 
> candidate architectures.
>
> **Cross-references:** [LIMITATIONS.md](LIMITATIONS.md) (diagnosis) · [ROADMAP.md](ROADMAP.md) (selection) · [TASKS.md](TASKS.md) (execution)

---

## 🏗️ Core Orchestration Backends

### S1: MLX-Swift Native Inference Library `[PROPOSED]`
*Proposed to solve: L1 (Cold-Start Latency), L6 (Python Dependency)*

| Property | Details |
|:---|:---|
| **Concept** | Re-implement the inference core as a Swift library/binary using the Apple MLX-Swift bindings. |
| **Pros** | Eliminates 3-5s of Python/uv overhead; allows fine-grained VRAM management via Swift actors; potentially sub-second TTL. |
| **Cons** | Extremely high engineering cost; MLX-Swift lacks parity with `mlx-lm` for some quantization types and serving features. |
| **Alternatives** | S2 (Dual-Process Python), S3 (mmap Weights). |
| **Experiment Link** | [E3 (48-Hour Spike)](LIMITATIONS.md#e3-mlx-swift-48-hour-spike) |

### S2: Dual-Process Python Pre-warming `[PROPOSED]`
*Proposed to solve: L1 (Cold-Start Latency)*

| Property | Details |
|:---|:---|
| **Concept** | Launch a second `mlx_lm.server` in the background on a new port; cut over once healthy. |
| **Pros** | Zero-downtime swaps with zero new language dependencies. |
| **Cons** | Double VRAM pressure during warm-up; complex state management in the Go supervisor. |
| **Incompatibility** | Cannot be used for models larger than 10GB total (due to 24GB M5 limit). |

### S3: Memory-Mapped Weight Persistence `[RESEARCHING]`
*Proposed to solve: L1 (Cold-Start Latency)*

| Property | Details |
|:---|:---|
| **Concept** | Keep weights in a resident shared memory block (shm) or `mmap`'d file so new processes can "attach" to them instantly. |
| **Pros** | ~1s restart time without language migration. |
| **Cons** | Depends on `mlx-lm` supporting shared weight buffers; complex to implement correctly on macOS unified memory. |

---

## 🧠 Multi-Tenancy & Memory Strategies

### S4: LoRA-Based Multi-Tenancy `[PROPOSED]`
*Proposed to solve: L2 (Single-Model Residency)*

| Property | Details |
|:---|:---|
| **Concept** | Standardize on a single base model (e.g., Hermes-3-8B) and swap low-rank adapters (<200MB) for different tasks. |
| **Pros** | No model unloading; near-zero latency switching; multiple "agents" share 95% of VRAM. |
| **Cons** | Requires tuning LoRAs for every specialty; potential quality drop vs. custom-built models. |
| **Experiment Link** | [E2 (LoRA Pilot)](LIMITATIONS.md#e2-lora-multi-tenancy-pilot) |

### S5: Metal Heap (`MTLHeap`) Virtualization `[REJECTED]`
*Proposed to solve: L5 (VRAM Fragmentation)*

| Property | Details |
|:---|:---|
| **Concept** | Manually manage Metal allocation heaps to pack multiple models into non-continuous VRAM. |
| **Pros** | Optimal physical memory utilization. |
| **Cons** | Obsoleted by MLX's internal allocator improvements; extremely brittle and maintenance-heavy. |
| **Decision ADR** | Rejected 2026-04-06: High complexity, low perceived ROI vs. S4. |

---

## 📊 Observability & Maintenance

### S6: Subprocess Metrics Caching `[PROPOSED]`
*Proposed to solve: L3 (Metrics Overhead)*

| Property | Details |
|:---|:---|
| **Concept** | Implement a simple TTL cache (5s) in Go around the `uv run python` metrics call. |
| **Pros** | Instant implementation; stops subprocess churn. |
| **Cons** | Doesn't remove the root Python dependency. |

### S7: SSE-Aware Line-Buffered Proxy `[PROPOSED]`
*Proposed to solve: L4 (Streaming Proxy Buffering)*

| Property | Details |
|:---|:---|
| **Concept** | Replace `io.Copy` with a manual loop that flushes on `\n\n` for SSE events. |
| **Pros** | Fixes OpenFang/Tachyon Tongs streaming latency immediately. |
| **Cons** | None. |

---

## 🔗 Cross-Project Solutions (Dependency Oriented)

### S8: `llm-proving-ground` Automated Regression `[PROPOSED]`
*Oriented toward: llm-proving-ground*

| Property | Details |
|:---|:---|
| **Concept** | Proving ground uses EHC's Maintenance API to automatically test new backend solutions (like S1) against production SLOs before cutover. |
| **Benefit** | Proactive validation of architectural changes. |

### S9: `llm-factory` LoRA Pipeline Integration `[PROPOSED]`
*Oriented toward: llm-factory*

| Property | Details |
|:---|:---|
| **Concept** | Factory exports specialized adapters specifically for EHC's S4 Multi-Tenancy strategy. |
| **Benefit** | Creates a closed-loop tuning feedback system. |

---

## 📝 Archives & Histograph

> *Design decisions and retired solutions.*

| Date | ID | Status | Note |
|:---|:---|:---|:---|
| 2026-04-01 | S10 | `[RETIRED]` | Removed Ollama/Llama.cpp providers to focus on MLX performance. |
| 2026-03-31 | S11 | `[RETIRED]` | Python-only orchestrator (replaced by Go daemon). |
