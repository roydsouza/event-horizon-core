# 🛡️ Physical Constraints & Hardware Safety

This document defines the **immutable rules** for interacting with the M5 Apple Silicon hardware to prevent system instability, memory exhaustion, and thermal issues.

## 🚫 CRITICAL: Model Downloads & Execution
- **NO AUTOMATIC DOWNLOADS**: You MUST NOT initiate an LLM download (e.g., via `mlx_lm.server` or `huggingface-cli`) without explicit, per-model approval from the USER.
- **VRAM CAP**: Never suggest or attempt to load any model with a total parameter count exceeding **15B** (quantized) on this 24GB M5.
- **INVENTORY FIRST**: Before running any inference command, check the local cache (`~/.cache/huggingface/hub`) to see if the model is already present. Use `ls -R` if necessary.

## ⚠️ Memory Pressure Management
- **OS FLUIDITY**: The primary objective is to maintain a responsive macOS UI. If `free_mb` drops below **2048MB**, you must immediately stop any background inference research.
- **PROCESS HYGIENE**: Always ensure that previous `mlx_lm.server` processes are terminated before starting a new one. Never leave orphan processes on Port 8080.

## 🛑 Research Protocol
- When investigating new libraries (e.g., `mlx-openai-server`), you must perform a `--dry-run` or check the dependency list before installing. 
- You MUST NOT install packages that trigger heavy compilation or massive blob downloads without asking.

## ⚖️ Forge/Crucible Governance
- **COORDINATION LAYER**: This project is governed by `ehc-lpg/`. Read `ehc-lpg/ANTIGRAVITY_RULES.md` at session start.
- **BUILD MANDATE**: `go build ./...` must exit 0 before ANY briefing is submitted. Verbatim stdout must be recorded.
- **VRAM GUARD**: Do not modify VRAM hard caps or the anti-zombie mutex without explicit Audit Clearance from Claude Code.
- **COEXISTENCE**: Respect the maintenance lock protocol when coordinating with `llm-proving-ground`.

---

> [!CAUTION]
> Violating these rules may cause the host machine to hang or crash, or lead to architectural "slop." Always prioritize physical safety and process integrity over speed.
