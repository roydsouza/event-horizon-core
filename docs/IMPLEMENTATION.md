# Event Horizon Core: Implementation Detail

This document provides a deep technical breakdown of the Event Horizon Core (EHC) architecture, its operational mechanics on Apple Silicon, and the rationale behind its design choices.

---

## 1. System Architecture Overview

EHC utilizes a **Split-Substrate Architecture** to decouple model orchestration from high-performance inference.

### 1.1 The Go Substrate (Daemon)
The "brain" of the system is a zero-dependency Go binary. It acts as a long-running daemon (`event-horizon`) that exposes an OpenAI-compatible HTTP interface on **Port 8000**.
- **Role**: State management, request routing, local VRAM orchestration, and memory pressure monitoring.
- **Library Footprint**: Zero external Go modules. Built entirely on the Go Standard Library (`net/http`, `os/exec`, `sync/atomic`) for maximum portability and minimal overhead.

### 1.2 The Inference Engine (Supervised MLX)
Inference is handled by `mlx_lm.server`, a Python process group managed directly by the Go substrate.
- **Role**: Token generation and Metal-accelerated compute.
- **Library Footprint**: Native Apple MLX bindings via the `mlx-lm` package.
- **Communication**: The Go substrate proxies HTTP/JSON requests to the internal inference server on **Port 8080**.

---

## 2. Model Lifecycle & Process Management

EHC solves the "Zombie VRAM" problem (where crashed orchestrators leave multi-gigabyte models resident in memory) using native Unix process groups.

### 2.1 Supervision Strategy
When the Go daemon starts the inference engine, it uses the `Setpgid: true` attribute. 
- **SIGKILL Propagation**: By targeting the Negative PID (`-cmd.Process.Pid`), the daemon can kill the entire process tree (Python, uv, and the server) in a single syscall.
- **Port Health Checks**: The Go supervisor does not release requests to the engine until it passes a 200ms-latency HTTP health check on Port 8080.

### 2.2 Hot-Swapping Logic
If a request specifies a model different from the one currently resident in VRAM:
1.  **Draining**: The daemon enters a temporary "Swap State."
2.  **Termination**: The active engine is killed via SIGKILL to ensure immediate Metal resource release.
3.  **Initialization**: The new engine is spawned via `uv run mlx_lm.server`.
4.  **Forwarding**: The original client request is released from the Go wait-queue and proxied to the new engine once it is healthy.

---

## 3. Memory & Performance Guardrails

Operating on a 24 GB M5 MacBook Pro requires aggressive VRAM management to prevent kernel UI freezes.

### 3.1 Unified Memory Monitoring
The Go substrate polls `vm_stat` every 30 seconds to track **Unified Memory Pressure**.
- **Thresholds**: 
    - `Warn (< 2048 MB free)`: Logs a warning and alerts the operator.
    - `Critical (< 1024 MB free)`: Immediately aborts any model swap requests to prevent the OS from locking up during Metal buffer allocation.

### 3.2 Idle Unloading (Phase 26)
To allow the Mac to reclaim memory for other tasks (e.g., browser sessions), EHC implements an **Idle Monitor**. If no requests are received within the `EHC_IDLE_TIMEOUT_SECONDS` window, the supervisor terminates the model server. The first subsequent request triggers a "Cold Start" restart (~1.9s - 3.8s latency).

### 3.3 Streaming Proxy (SSE)
EHC uses a line-buffered proxy to handle **Server-Sent Events (SSE)**.
- **Technique**: Instead of buffering the full response, the Go handler reads the response from Port 8080 line-by-line using `bufio`, flushing each line to the client immediately. This ensures that the Time to First Token (TTFT) is not masked by the proxy layer.

---

## 4. Performance Metrics (M5 Baseline)

| Metric | Target (Hermes-3-8B) | Actual (April 2026) |
|:---|:---|:---|
| **Hot Swapping** | < 5.0s | **1.2s - 1.4s** |
| **Warm TTFT** | < 200ms | **161ms** |
| **Inference Throughput** | > 40 tok/s | **52 tok/s** |
| **Python Overhead** | < 20% | **5% - 11%** (Cold Cache) |

---

## 5. Rejected Alternatives & Rationale

| Alternative | Rationale for Rejection |
|:---|:---|
| **Ollama** | **Abstraction Bloat.** Ollama's Go wrapper introduces unnecessary memory management and process abstraction that complicates the "pure" supervision needed for aggressive M5 VRAM packing. |
| **Llama.cpp / GGUF** | **Performance Gap.** While highly compatible, `llama.cpp` performance on Apple Silicon (Metal/ANE) lagged significantly behind MLX native performance during April 2026 benchmarking sessions. |
| **OpenRouter / Remote** | **Data Sovereignty.** Remote fallbacks were purged in Phase 10 to ensure the project remains 100% "Dark Factory" compatible—guaranteeing that no agent data ever leaves the local hardware. |
| **vLLM-mlx** | **Immature Ecosystem.** vLLM-mlx offers superior batching but lacks the stability and simplified SSE streaming support of the official `mlx_lm.server` for single-user laptop workloads. |
| **MLX-Swift (Phase 16)** | **Diminishing Returns.** Experiment E1 confirmed that the cold-start bottleneck is **Weight Loading** (Physical I/O), not Python startup. Migrating to Swift would save only ~200ms at the cost of massive code reimplementation. |

---

> **Contractual Note:** This implementation is designed to survive the "Heartbeat" frequency of multi-agent sessions (Claws, Firewall, Monitoring) while protecting the host OS from OOM-induced failures.
