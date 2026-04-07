# Event Horizon Core

**Local LLM inference orchestration for Apple Silicon M5.**  
A Go daemon that manages `mlx_lm.server`, exposes an OpenAI-compatible HTTP API on port 8000, and coordinates multi-agent access with maintenance mode, model swapping, and memory telemetry.

> **Cross-references:** [INTEGRATION.md](INTEGRATION.md) · [LIMITATIONS.md](LIMITATIONS.md) · [ROADMAP.md](ROADMAP.md) · [TASKS.md](TASKS.md)

---

## Architecture

```
Station agents (Claws, firewall…)
        ↓  HTTP :8000  (X-Agent-Name header required)
┌─────────────────────────────────┐
│   Go Orchestrator (EHC)         │
│   /v1/chat/completions (proxy)  │
│   /system/maintenance API       │
│   /v1/model/swap                │
│   /metrics  (TTL-cached 5s)     │
└──────────────┬──────────────────┘
               ↓  HTTP :8080
       mlx_lm.server (Python/MLX)
       Hermes-3-8B-4bit · Metal
       --prompt-cache-size 512
```

**Default model:** `mlx-community/Hermes-3-Llama-3.1-8B-4bit`  
**Hardware target:** Apple M5, 24 GB unified memory

---

## Quick Start

```bash
# Build
go build -o event-horizon ./cmd/event-horizon/

# Run (managed by launchd in production)
./event-horizon

# Check status
curl http://127.0.0.1:8000/status

# Send a completion (X-Agent-Name is required)
curl http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-Agent-Name: my-agent" \
  -d '{"messages": [{"role": "user", "content": "Hello"}]}'
```

---

## Endpoints

### Agent endpoints (no auth)

| Method | Path | Notes |
|:-------|:-----|:------|
| `POST` | `/v1/chat/completions` | OpenAI-compatible. SSE streaming supported. **Send `X-Agent-Name` header.** |
| `GET`  | `/status` | Daemon health, active model, maintenance state. |

### Admin endpoints (`X-EHC-Admin-Token` required)

| Method | Path | Notes |
|:-------|:-----|:------|
| `POST` | `/system/maintenance` | Enter maintenance mode; in-flight requests drain (10s max). |
| `POST` | `/system/maintenance/release` | Exit maintenance; optional `promote_model` field. |
| `GET`  | `/system/maintenance/status` | Poll state: `in_maintenance`, `requested_by`, `since`. |
| `POST` | `/v1/model/swap` | Explicit swap. Returns 409 if already in progress. |
| `GET`  | `/metrics` | MLX Metal memory: `active_mb`, `peak_mb`. Cached 5s. |

Admin token is read from `EHC_ADMIN_TOKEN` env var (`.env`, never committed).

---

## Model Inventory (as of 2026-04-07)

| Model | Size | Role |
|:------|:-----|:-----|
| `Hermes-3-Llama-3.1-8B-4bit` | 4.2 GB | **Active default** — primary reasoning model |
| `Llama-3.2-3B-Instruct-4bit` | 1.7 GB | E1 swap test; draft model candidate |
| `Llama-3.2-1B-Instruct-4bit` | 680 MB | Draft model candidate |
| `gemma-4-e4b-it-4bit` | 4.9 GB | Cached — firewall profile candidate |

> **Do not request models > ~14B at 4-bit.** They OOM during generation on 24 GB M5.

---

## Service Level Objectives

| Metric | Target | Measured | Notes |
|:-------|:-------|:---------|:------|
| TTFT (warm prompt cache) | < 1.0s | 0.74s P95 | Prefix cache active |
| Hot-swap (filesystem cache warm) | < 500ms | 258–357ms | Python overhead ~200ms |
| Hot-swap (filesystem cache cold) | < 5.0s | 1.9–3.8s | Weight loading dominates |
| Throughput | > 20 tok/s | 21.8 tok/s | 10-client concurrent load |

> **Cold-swap note:** On the 24 GB M5 with ~2 GB free RAM, the filesystem cache is frequently evicted by browser tabs and other apps, making cold swaps the norm. Hot-swap SLO assumes a quiet system.

---

## Memory Constraints & Freeze Prevention

The active model holds **~4.6 GB of non-compressible Metal-backed memory** that macOS cannot page out or compress. On a 24 GB system this leaves limited headroom.

**Practical guidance:**
- Use Safari instead of Chromium-based browsers (~1–2 GB savings)
- Close Electron apps (VS Code, Slack) during inference sessions
- Monitor: `vm_stat | grep "Pages free"` — below 60,000 pages (~1 GB) means pressure is severe
- Full analysis: see [LIMITATIONS.md L10](LIMITATIONS.md#l10-unified-memory-pressure--non-compressible-metal-allocations--high-mac-freeze-risk)

---

## Key Invariants

- **VRAM guardrail:** Model loading is rejected above the 22 GB budget
- **Anti-zombie mutex:** `Setpgid: true` — SIGKILL to entire process group on swap; no orphaned MLX servers
- **Maintenance drain:** In-flight requests tracked atomically; drain completes before maintenance proceeds
- **Hot-swap contention:** `/v1/model/swap` returns 409 immediately if a swap is already running

---

## Monitoring

```bash
# Real-time Apple Silicon memory / GPU / NPU dashboard
uv tool install asitop
sudo asitop

# Memory pressure
vm_stat | grep "Pages free"

# MLX Metal allocation
curl -H "X-EHC-Admin-Token: $EHC_ADMIN_TOKEN" http://127.0.0.1:8000/metrics
```

---

## Development

```bash
# Build
go build -o event-horizon ./cmd/event-horizon/

# Run benchmarks
uv run python3 tests/hardware_benchmark.py

# View swap timing data (Experiment E1)
cat benchmarks/swap_latency.csv
```

See [DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) for full development setup.
