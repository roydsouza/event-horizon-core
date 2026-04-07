# EHC Memory Runbook

> **Audience:** Station operator (Roy). Reference this when the Mac is sluggish, before
> running model swaps or benchmarks, and when deciding whether to enable Phase 26 idle
> unloading.

---

## Why the Mac Freezes

The MLX model server (`mlx_lm.server`) allocates model weights as **Metal pinned buffers**.
On Apple Silicon unified memory, these are the same physical RAM as "VRAM". macOS cannot
compress or page them out — the kernel memory compressor ignores them.

**Current steady-state (Hermes-3-8B-4bit loaded):**

| Allocation | Size |
|:-----------|:-----|
| MLX Metal pinned (Hermes-3-8B-4bit) | ~4.6 GB |
| Effective free RAM (browser closed) | ~4–6 GB |
| Effective free RAM (browser open) | ~1–2 GB |

When total committed memory approaches 24 GB, the kernel compressor overloads and the
UI thread stalls — visible as the entire desktop freezing for 5–30 seconds.

---

## Pressure States

EHC monitors memory every 30 seconds and logs transitions to `daemon.log`. You can also
query the current state:

```bash
curl http://127.0.0.1:8000/system/memory
```

```json
{
  "free_mb": 1842,
  "speculative_mb": 312,
  "inactive_mb": 8640,
  "active_mb": 6210,
  "wired_mb": 3120,
  "compressed_mb": 1900,
  "total_free_mb": 2154,
  "pressure": "normal"
}
```

| State | `total_free_mb` | Meaning | Action |
|:------|:----------------|:--------|:-------|
| `normal` | ≥ 2048 MB | Safe to swap models | Proceed normally |
| `warn` | 1024–2047 MB | Pressure elevated | Close browser tabs; avoid swaps |
| `critical` | < 1024 MB | EHC will abort model swaps | Close browser + other apps immediately |

`total_free_mb` = `free_mb` + `speculative_mb` (speculative pages are immediately
reclaimable by the OS, so they count as effectively free).

---

## Log Indicators

Watch for these in `daemon.log` (or `launchctl log show` if using launchd):

```
[WARN memory-pressure] Elevated: 1640 MB free ...
[WARN memory-pressure] CRITICAL: 890 MB free ...
[INFO memory-pressure] Returned to normal: 3200 MB free.
[WARN] High memory pressure detected (1640 MB free). Proceeding, but system may lag
ABORTING SWAP: Critical memory pressure (890 MB free). Close other apps ...
```

---

## Runbook: Mac Is Sluggish / Freezing

1. **Check pressure:**
   ```bash
   curl http://127.0.0.1:8000/system/memory | python3 -m json.tool
   ```

2. **If `warn` or `critical`:** Close browser tabs. Switch to Safari if using Chrome
   (Chrome's renderer processes don't participate in macOS memory compressor — each tab
   holds its RSS non-compressibly). Safari pages out aggressively under pressure.

3. **If still `critical` after closing tabs:** Restart EHC to release the Metal
   allocation and then re-launch:
   ```bash
   # Find and kill the Go daemon
   pkill -f "event-horizon"
   # Restart
   cd ~/antigravity/event-horizon-core && ./event-horizon &
   ```
   After restart, `vm_stat` should show ~4.6 GB more free pages.

4. **If the model is not needed right now:** Enable idle unloading temporarily (see
   Phase 26 section below) or just kill the EHC process.

---

## Runbook: Before Running Model Swaps or Benchmarks

Especially relevant for **Phase 22 controlled cold-cache measurements**.

**Safety rule (mandatory):** `sudo purge` while EHC is running caused a kernel OOM
crash on 2026-04-07. The purge forces the OS to evict disk caches while the MLX weight
loader simultaneously demands high-throughput disk access — the two operations contend
and can stall the UI thread past the point of recovery.

**Pre-measurement checklist:**
- [ ] Stop EHC: `pkill -f event-horizon`
- [ ] Close browser completely (not just tabs — quit the app)
- [ ] Verify pressure is `normal`: `curl http://127.0.0.1:8000/system/memory` (restart
  EHC briefly to check, then stop again before purging)
- [ ] Run `sync && sudo purge`
- [ ] Verify `vm_stat | grep "Pages free"` shows ≥ 500,000 pages (~8 GB)
- [ ] Start EHC fresh: `./event-horizon &`
- [ ] Run measurement

---

## Phase 26: Idle Unloading

When enabled, EHC automatically unloads the model after N seconds of inactivity,
releasing the full ~4.6 GB Metal allocation. On the next inference request the model
cold-starts (1.9–3.8s per E1 data). Suitable for development sessions where you
alternate between inference and other work.

**Enable:**
```bash
export EHC_IDLE_TIMEOUT_SECONDS=300   # 5 minutes
./event-horizon &
```

**Confirm unload occurred:**
```bash
# idle_since will be non-null in the status response
curl http://127.0.0.1:8000/status | python3 -m json.tool
# free memory should be ~4.6 GB higher
curl http://127.0.0.1:8000/system/memory | python3 -m json.tool
```

**Trade-off:**

| | Always-Hot (default) | Idle Unloading (Phase 26) |
|:--|:--|:--|
| First token after idle | Instant | +1.9–3.8s (cold start) |
| RAM held by Metal | ~4.6 GB always | 0 GB when idle |
| Freeze risk (browser open) | High (only ~1–2 GB free) | Low (4.6 GB reclaimed) |
| Recommended for | Active multi-agent sessions | Dev / infrequent use |

---

## Pressure Threshold Rationale

Thresholds chosen for the 24 GB M5 with Hermes-3-8B-4bit (4.6 GB Metal):

- **Warn (< 2048 MB):** A new browser tab or Electron window can consume 200–800 MB.
  At < 2 GB free, a single new tab may push us into critical territory mid-swap.
- **Critical (< 1024 MB):** Below this point the kernel compressor is already under
  load. Initiating a model swap (which SIGKILLs the current MLX process and loads
  4.2–4.6 GB of new weights) will cause a freeze.

To adjust thresholds, modify the constants in `internal/supervisor/manager.go`:
```go
if stats.TotalFreeMB < 1024 {   // critical
if stats.TotalFreeMB < 2048 {   // warn
```
