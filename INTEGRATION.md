# Event Horizon Core — Integration Guide

> **Cross-references:** [ROADMAP.md](ROADMAP.md) · [LIMITATIONS.md](LIMITATIONS.md) · [SOLUTIONS.md](SOLUTIONS.md) · [docs/clients/](docs/clients/)

EHC exposes a local HTTP server on **port 8000** that is drop-in compatible with the OpenAI Chat Completions API. It manages multiple inference engines (**MLX-LM**, **Bodega**, **vLLM**) and provides a unified interface for all station agents (Claws, firewall, monitoring daemons).

---

## Required: Agent Identity Header

**Every client MUST send `X-Agent-Name` on every request to `/v1/chat/completions`.**

```
X-Agent-Name: <your-agent-slug>   # e.g. zeroclaw, shapeshifter-firewall, penumbra
```

This header is EHC's identity primitive. It enables:
- Per-agent metrics (`GET /metrics/agents`, Phase 24)
- Config-driven model routing — EHC assigns the right model automatically (Phase 24)
- Firewall interception — EHC calls Shapeshifter-Airlock before proxying (ROADMAP R8)

Omitting it is accepted today (request is processed, warning logged) but will become a hard requirement once Phase 24 lands.

---

## Endpoints

### Station Agent Endpoints (no auth required)

| Method | Path | Description |
|:-------|:-----|:------------|
| `POST` | `/v1/chat/completions` | OpenAI-compatible chat completions. Streaming supported (SSE). |
| `GET`  | `/status` | Daemon health: current model, maintenance mode, engine. |

### Infrastructure / Admin Endpoints (require `X-EHC-Admin-Token` header)

| Method | Path | Description |
|:-------|:-----|:------------|
| `POST` | `/system/maintenance` | Enter maintenance mode — new completions get 503. |
| `POST` | `/system/maintenance/release` | Exit maintenance mode. Optional `promote_model` field. |
| `GET`  | `/system/maintenance/status` | Poll maintenance state and active model. |
| `POST` | `/v1/model/swap` | Explicit model/engine swap. Returns 409 if swap already in progress. |
| `GET`  | `/metrics` | MLX Metal memory telemetry (`active_mb`, `peak_mb`). TTL-cached 5s. |
| `GET`  | `/metrics/agents` | Per-agent usage metrics (TTFT, TPS, Token counts). |
| `GET`  | `/system/memory` | Host memory pressure (free, speculative, wired, etc.). |
| `GET`  | `/debug/events` | In-memory ring buffer of recent daemon events (JSON). |

Admin token is read from the `EHC_ADMIN_TOKEN` environment variable (set in `.env`, never committed). All `/system/*` and `/metrics` calls are rejected with HTTP 401 if the token is absent or wrong.

---

## Station Agent Integration

Station agents (Claws, firewall, monitoring) use the completions endpoint directly. They do **not** need to know which model is loaded — EHC's routing table resolves the model by agent name.

```bash
curl http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-Agent-Name: zeroclaw" \
  -d '{
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

**Do not send a `model` field** unless you have a specific reason. Station agents should let EHC choose the model. Once Phase 24 (routing table) is live, the pin for your agent slug will determine the model automatically.

**Environment variables** for OpenAI-compatible clients:
```bash
OPENAI_BASE_URL="http://127.0.0.1:8000/v1"
OPENAI_API_KEY="sk-local"   # any non-empty string — no remote auth needed
```

See `docs/clients/` for per-agent setup guides.

---

## Infrastructure Caller Integration (llm-proving-ground, llm-factory)

Infrastructure callers need to take exclusive control of EHC before running evaluations or training. They use the maintenance API:

```python
import httpx

ADMIN_HEADERS = {
    "X-EHC-Admin-Token": os.environ["EHC_ADMIN_TOKEN"],
    "X-Agent-Name": "llm-proving-ground",
    "Content-Type": "application/json",
}

# 1. Enter maintenance mode — existing inference drains (up to 10s)
r = httpx.post("http://127.0.0.1:8000/system/maintenance",
               headers=ADMIN_HEADERS,
               json={"reason": "evaluation run", "requested_by": "llm-proving-ground"})

# 2. Swap to the model under evaluation
r = httpx.post("http://127.0.0.1:8000/v1/model/swap",
               headers=ADMIN_HEADERS,
               json={"model": "mlx-community/Qwen2.5-Coder-14B-Instruct-4bit"})

# 3. Run evaluation (completions work even in maintenance mode for admin callers — implement this in Phase 24)
# For now: release maintenance first, then run, then re-enter for cleanup.

# 4. Release — optionally promote the tested model as new default
r = httpx.post("http://127.0.0.1:8000/system/maintenance/release",
               headers=ADMIN_HEADERS,
               json={"promote_model": "mlx-community/Qwen2.5-Coder-14B-Instruct-4bit"})
```

See `COEXISTENCE.md` in `llm-proving-ground/` and `llm-factory/` for full protocol.

---

## Model Selection Logic

| Caller type | How model is chosen |
|:------------|:-------------------|
| Station agent, no `model` field | Routing table pin for agent name; falls back to station default (`Hermes-3-8B`) |
| Station agent, explicit `model` field | Triggers implicit hot-swap to the requested model — **avoid unless intentional** |
| Infrastructure caller, explicit `model` field + admin token | Full control; use `/v1/model/swap` via maintenance API |

**Current station default:** `mlx-community/Hermes-3-Llama-3.1-8B-4bit`

Routing table pins are configured in `config.toml` (Phase 24 — not yet implemented; all agents currently use the default).

---

## Streaming

EHC supports Server-Sent Events (SSE) streaming. Set `"stream": true` in the request body. The proxy flushes each SSE line to the client immediately rather than buffering.

```bash
curl -N http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-Agent-Name: zeroclaw" \
  -d '{"messages": [{"role": "user", "content": "Count to 5"}], "stream": true}'
```

---

## Memory Constraints

EHC runs on a 24 GB unified memory M5. The active model (~4.6 GB for Hermes-3-8B) occupies non-compressible Metal-backed memory. This leaves ~19 GB for the OS, other apps, and KV cache.

- **Do not request models larger than ~14B parameters at 4-bit** — they will OOM during generation.
- **Do not run llm-factory training while other agents are active** — training is the most VRAM-intensive operation on the station; it requires exclusive maintenance mode.
- **Monitor memory pressure** with `vm_stat | grep "Pages free"` — if free pages < 60,000 (~1 GB), close other apps before sending long prompts.
- **Future:** Phase 23 will add a `/system/memory` endpoint that exposes pressure level (normal/warn/critical) so clients can back off proactively.

---

## Deployment Checklist (new agent)

1. Set `OPENAI_BASE_URL=http://127.0.0.1:8000/v1` and `OPENAI_API_KEY=sk-local` in the agent's `.env`.
2. Add `X-Agent-Name: <slug>` to every completions request. Document in the agent's setup guide.
3. Verify EHC is running: `curl http://127.0.0.1:8000/status`.
4. Do **not** hardcode a `model` field — let EHC resolve it from the routing table (once Phase 24 lands).
5. Use `--dry-run` mode in any script that touches the maintenance API before running live.

---

## Universal Interface Rationale

EHC has standardized on the **OpenAI Chat Completions API (`/v1/chat/completions`)** as its primary integration surface. 

### Why OpenAI Format?
- **De Facto Industry Standard**: As of 2026, the OpenAI format is the "lingua franca" of LLM tools. Almost every modern agent (OpenRouter, LiteLLM, LangChain), model aggregator, and IDE integration (Doom Emacs, Cursor) supports it out-of-the-box.
- **Zero Vendor Lock-in**: By using this format, we can swap between **MLX-LM**, **Bodega**, and **vLLM** backends without changing a single line of code in our station agents.
- **OpenRouter Compatibility**: Since OpenRouter itself uses the OpenAI format as its gateway interface, EHC acts as a local "OpenRouter node" for your M5, allowing you to use OpenRouter-compatible tools locally.

### Why not native Anthropic/Google/AWS Bedrock?
While native APIs for Claude (Anthropic) or Gemini (Google) have specific benefits (like massive context windows or native multimodal tokens), their schemas are highly divergent. Adopting them would require writing per-agent translation layers. 

**EHC handles this by acting as the Translator.** It accepts a standardized OpenAI-formatted request and performs the necessary internal routing and hardware orchestration to satisfy it on the best available local engine.
