# Event Horizon Core — Status

This log provides an executive summary and technical pulse-check of `event-horizon-core`.
Update this file whenever phase status changes or system health changes materially.

---

## 2026-04-18: Governance Layer Added — Active Development

### Executive Summary
EHC is **production-ready** on Apple Silicon M5 24 GB. The Go daemon is stable on Port 8000,
serving MLX-accelerated inference via the `Hermes-3-Llama-3.1-8B-4bit` model (4.2 GB). The
station has adopted a structured Forge+Crucible+Auditor governance process (see `../sync/`).

### Active Phases
| Phase | Description | Status |
|-------|-------------|--------|
| 13 | Gemma 4 default model evaluation | **ACTIVE** — awaiting `mlx-lm >= 0.32.0` upgrade |
| 27 | Google AI Studio free-tier integration | **ACTIVE** — not started |
| 28 | Integrated proving ground workflow (EHC + LPG coexistence exercise) | **ACTIVE** — not started |

### System Health
| Component | Status | Notes |
|-----------|--------|-------|
| Default model | `Hermes-3-Llama-3.1-8B-4bit` (4.2 GB) | Stable |
| VRAM guard | Active | 22 GB hard cap |
| Idle unload | Active | `EHC_IDLE_TIMEOUT_SECONDS` |
| Anti-zombie mutex | Active | Process group isolation |
| Structured logging | Active | slog JSON format |
| Hot-swap | Deferred | Single-model strategy; revisit on monthly MLX review |

### Recurring Tasks
| Task | Due | Status |
|------|-----|--------|
| Model cache audit | 2026-04-12 | **OVERDUE** |
| Default model evaluation (Gemma 4 readiness) | 2026-04-12 | **OVERDUE** |
| MLX multiplexing options re-evaluation | 2026-05-07 | Pending |

### Model Cache (last audited 2026-04-07, 11.6 GB total)
| Model | Size | Status |
|-------|------|--------|
| `Hermes-3-Llama-3.1-8B-4bit` | 4.2 GB | **Active — EHC default** |
| `gemma-4-e4b-it-4bit` | 4.9 GB | Cached — firewall profile candidate |
| `Llama-3.2-3B-Instruct-4bit` | 1.7 GB | Cached — draft candidate |
| `Llama-3.2-1B-Instruct-4bit` | 680 MB | Cached — draft candidate |

### Downstream Consumers
`penumbra/` (active) · `hermes_agent/` (upcoming) · `open_claw/` (upcoming) · `open_fang/` (upcoming) · `llm-proving-ground/` (evaluation partner)
