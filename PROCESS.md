# EHC: Agent Process Cheat Sheet

This project follows the **Forge/Crucible/Auditor** model.

## 🛠️ Forge (Building & Fixing)
1. **Sync**: Check `sync/SYNC_LOG.md` (YAML) first.
2. **Priority**: `DEFECTS.md` -> `TASKS.md`.
3. **Verify**: `go build ./...` must exit 0.
4. **Brief**:
   - Write full stdout to `sync/build-artifacts/`.
   - File briefing to `sync/auditor-inbox/`.
   - Embed `go build` output and `curl /status` (if daemon touched).
   - Use `DEF-XXX` or `TASK-XXX` IDs.

## ⚖️ Crucible (Reviewing)
1. **Ground Truth**: Do NOT trust Forge's briefing prose. Read files from disk.
2. **Verify**: Re-run `go build ./...` yourself.
3. **Compare**: Compare your stdout to Forge's line-by-line.
4. **Verdict**: File to `sync/crucible-verdicts/`.
   - Include `git show <hash> --stat` verbatim.
   - Status: CLEARED, VETOED, or CONDITIONAL.

## 🛑 Audit Triggers (Claude Code)
File to `sync/auditor-inbox/` for:
- VRAM hard cap changes (22 GB).
- Anti-zombie mutex / process cycle changes.
- New API endpoints.
- Model promotion (LPG -> EHC).

---
**Canonical reference:** [sync/PROCESS.md](../sync/PROCESS.md)
