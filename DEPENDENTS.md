# Event Horizon Core — External Dependents

**[📍 Back to Map](../CONTENTS.md)**

This document tracks projects that depend on EHC as an inference substrate and that may need to coordinate with it at runtime. Any agent working on EHC must be aware of these dependents before making changes to the API surface, startup behavior, or VRAM management.

---

## Active Dependents

### `llm-proving-ground` — LLM Evaluation Pipeline
- **Repo**: `~/antigravity/llm-proving-ground`
- **Relationship**: Uses EHC as the evaluation runtime. Before benchmarking a candidate model, it acquires the maintenance lock, swaps in the candidate, runs the full evaluation suite, then signals EHC to either promote or revert.
- **API surface used**:
    - `POST /system/maintenance` — lock EHC before evaluation
    - `POST /v1/model/swap` — load candidate model
    - `POST /system/maintenance/release` — unlock and optionally promote
    - `GET /system/maintenance/status` — poll lock state
    - `GET /status` — health check
    - `POST /v1/chat/completions` — inference during evaluation
- **VRAM contention**: Proving ground loads models up to 15B (4-bit). EHC must be in maintenance mode; station agents must not be running concurrently.
- **See also**: `llm-proving-ground/COEXISTENCE.md`

### `llm-factory` — LLM Fine-Tuning & Optimization Pipeline
- **Repo**: `~/antigravity/llm-factory`
- **Relationship**: Uses EHC's maintenance lock to claim exclusive VRAM during fine-tuning runs (MLX LoRA). After fine-tuning, publishes the resulting model to a local or HuggingFace repository, then may hand the model off to `llm-proving-ground` for evaluation before EHC promotion.
- **API surface used**:
    - `POST /system/maintenance` — lock EHC before fine-tuning
    - `POST /system/maintenance/release` — unlock when complete
    - `GET /system/maintenance/status` — poll lock state
- **VRAM contention**: Fine-tuning is the most VRAM-intensive operation in the station. EHC must be fully quiesced; no concurrent inference workloads.
- **See also**: `llm-factory/COEXISTENCE.md`

---

## Required EHC Work (Phase 18)

Neither dependent can fully integrate until **Phase 18: External Orchestration API** is complete. See `TASKS.md` Phase 18 for the full task list. The minimum viable surface is:
1. `POST /system/maintenance` with drain + 503 behavior
2. `POST /system/maintenance/release` with optional model promotion
3. `GET /system/maintenance/status`
4. Admin token auth on all `/system/*` endpoints

---

## Coordination Protocol

Only one external process may hold the maintenance lock at a time. The intended workflow is:

```
llm-proving-ground (or llm-factory)
  → POST /system/maintenance          # Acquire lock
  → Poll GET /system/maintenance/status until {"in_maintenance": true}
  → Do work (evaluation or fine-tuning)
  → POST /system/maintenance/release  # Release lock (optionally promote model)
  → Verify GET /status shows operational
```

If a process crashes while holding the lock, EHC should expose a manual override:
```bash
curl -X POST http://127.0.0.1:8000/system/maintenance/release \
  -H "X-EHC-Admin-Token: $EHC_ADMIN_TOKEN" \
  -d '{"force": true}'
```

This is to be implemented as part of Phase 18.

---

*Last updated: 2026-04-05*
