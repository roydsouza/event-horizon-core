# Event Horizon Core — Context for Claude

**[📍 Back to Map](../CLAUDE.md)**

## 1. Project Overview

**Event Horizon Core** is the primary LLM inference orchestration layer for the AntiGravity ecosystem. It is a high-performance, local-only Go daemon that manages Apple Silicon M5 Metal VRAM, coordinates multi-agent workflows, and exposes a Python thin-client CLI — with zero external dependencies.

This is a **primary, actively developed project**. It is the shared infrastructure backbone for all upcoming agentic projects (`hermes_agent`, `open_claw`, `open_fang`).

## 2. Technical Stack

- **Language:** Go (daemon/substrate) + Python (thin-client via `uv`)
- **Target:** Apple Silicon M5, 24GB Unified Memory, Metal GPU
- **Inference:** MLX (local, Metal-accelerated) + OpenRouter (cloud fallback)
- **Transport:** Local HTTP (Port 8000), `launchd` managed service
- **Build:** `go build`, `uv run`

## 3. Architecture

```
cmd/event-horizon/      — Go daemon entry point
internal/supervisor/    — Process lifecycle, anti-zombie mutex, process group isolation
internal/server/        — HTTP routing, hot-swap middleware, VRAM guard
event_horizon_core/     — Python thin-client (proxies to Go daemon)
tests/                  — Hardware benchmark suite, regression tests
```

**Key invariants:**
- VRAM hard cap: 22GB (prevents OS swapping)
- Anti-Zombie Mutex: process groups ensure zero orphan servers after model swap
- Hot-swap latency SLO: < 3.0s
- Throughput SLO: > 20 tok/s under 10-client concurrent load

## 4. Current Development Focus

**Concurrent access** — ensuring the Go substrate correctly handles simultaneous requests from multiple downstream agents (`hermes_agent`, `open_claw`, `open_fang`) without VRAM leaks, lock contention, or zombie processes.

Always check `TASKS.md` (and `tasks/` subdirectory if present) on session open to identify the highest-priority work item, then confirm with the operator before starting.

## 5. Workflows & Agent Expectations

- **Opening ritual:** `git pull` → read `SYNC_LOG.md` → **check `🔁 Recurring Tasks` table** (surface any item with Next Due ≤ today to the operator before starting other work)
- **TASKS.md contract:** Mark in-progress with `/`, complete with full checkmark, update `SYNC_LOG.md` after each task
- **Testing:** Run `uv run python3 tests/hardware_benchmark.py` and all regression tests before marking done
- **Documentation:** Keep `README.md`, `SYNC_LOG.md`, and inline docs in sync with implementation at all times
- **Tier:** Standard (tests required, conventional commits)

## 6. Downstream Consumers

The following projects depend on Event Horizon Core and must be considered when making breaking changes:

- `penumbra/` — Agent framework using EHC for inference
- `hermes_agent/` (upcoming)
- `open_claw/` (upcoming)
- `open_fang/` (upcoming)
- `Darwin-Godel-Machine/` — Uses local MLX directly, but may integrate
