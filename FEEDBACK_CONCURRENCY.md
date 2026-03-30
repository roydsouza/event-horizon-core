# Question:

I am building some scaffolding that will let multiple disparate agents (ex: my agentic firewall, or opencode, or openclaw) to "concurrently" use a local LLM using MLX. So I'm exploring using locking and/or queueing. I want to explore techniques that will save/swap context as well, as part of switching context. Any thoughts on OSS code I can reuse, etc?


# Gemini:

For a 24 GB M5 MacBook Pro, the primary bottleneck in a multi-agent environment is the **KV Cache** memory explosion. When multiple agents (like your firewall and coding tools) call the model simultaneously, each session competes for the same limited unified memory. 

In the 2026 local LLM landscape, several OSS projects have moved beyond simple serial queueing to implement sophisticated "context-aware" scheduling natively for MLX.

### Recommended OSS Scaffolding to Reuse

Instead of building a locking mechanism from scratch, you can leverage or fork these projects which already handle the MLX-specific memory management:

* **vllm-mlx:** This is a native Apple Silicon port of the vLLM engine. It implements **Continuous Batching**, which allows multiple agent requests to be processed in the same GPU pass rather than waiting in a serial queue. It also supports **Paged KV Cache**, which prevents memory fragmentation when multiple agents have long, diverging conversations.
* **oMLX (Open-Source MLX Server):** This is perhaps the most relevant for your "saving/swapping" requirement. It features a **Two-Tier KV Cache** (RAM hot + SSD cold). When an agent becomes inactive, its KV cache blocks are persisted to your Mac’s fast internal SSD. When that agent triggers again, the context is restored from SSD in roughly 1–3 seconds, bypassing a full re-prefill.
* **Sluice-LLM:** If you prefer to keep your existing `mlx-lm` setup and just need a "traffic cop," this is a lightweight (~600 lines of Python) priority-queue proxy. It serializes GPU access so that a critical "firewall" agent can jump the line ahead of a background "OpenCode" task.

---

### Techniques for Context Management

To efficiently "swap" context between your agents, you should focus on these three architectural patterns:

#### 1. Prefix Caching (Shared Scaffolding)
Most of your agents likely share a massive system prompt (tool definitions, DeFi ontologies, etc.).
* **Implementation:** Use a **Prefix Cache Manager** (found in `vllm-mlx`).
* **Benefit:** The model computes the "static" part of the prompt once and shares those KV blocks across all concurrent agent requests. For a 10K token system prompt, this can save ~1–2 GB of RAM per agent and drop latency from minutes to milliseconds.

#### 2. SSD-Tiered Offloading
Since you have 24 GB of RAM, running a 30B model (which takes ~16.5 GB at 4-bit) leaves only ~7.5 GB for all agent contexts.
* **Technique:** Use **Copy-on-Write (CoW)** KV blocks. 
* **Mechanism:** When the "OpenCode" agent finishes a turn, the server marks its KV blocks as "evictable" and writes them to a `safetensors` file on disk. The memory is immediately freed for the "Firewall" agent.

#### 3. Context "Quarantine" & Pruning
For agentic workflows, context often bloats with redundant tool-call logs.
* **Technique:** Implement **Dynamic Tool Loadout**.
* **OSS Logic:** Reuse logic from the **"Context Quarantine"** pattern where only the last $N$ turns and the relevant tool definitions are kept active. This maintains a flat latency even as your session grows.

### Architecture Comparison

| Tool | Concurrency Strategy | Context Swapping | Best For |
| :--- | :--- | :--- | :--- |
| **vllm-mlx** | Continuous Batching | Paged Attention (RAM) | High-throughput, low-latency concurrent calls. |
| **oMLX** | Serial + Batching | **SSD Cold Storage** | Long coding sessions where you want to "pause" and "resume". |
| **Sluice** | Priority Queueing | None (External Proxy) | Simple, reliable serialization of multiple local tools. |

### A Note on "Hybrid" Architectures
If you are using **Qwen 3.5** or **Gemma 3**, standard prefix caching is currently unstable because they use "sliding window" or "Mamba/SSM" layers. For these models, you must use **oMLX**, as it is currently one of the few MLX servers implementing specialized "Hybrid Cache" logic to handle non-standard attention layers correctly.

**Would you like me to help you configure a `vllm-mlx` or `oMLX` instance to serve as the unified backend for your agents?**

# Anthropic:

This is a great systems problem. Here's a breakdown of the landscape and reusable OSS pieces:

## The Core Challenge

MLX runs on the Metal GPU and is inherently single-threaded for inference — you can't truly parallelize model forward passes. So your architecture is really about **smart serialization + fast context restoration**, not true concurrency.

---

## Tier 1: Just Use `mlx_lm.server` (Baseline)

`mlx-lm` ships a FastAPI-based OpenAI-compatible server out of the box:

```bash
mlx_lm.server --model mlx-community/Mistral-7B-Instruct-v0.3-4bit --port 8080
```

It already serializes requests. Your agents (opencode, openclaw, your firewall) can all point at it. The problem: **no KV cache persistence across requests** — each call is cold. This is your starting point to beat.

---

## Tier 2: KV Cache Swapping (The Key Insight)

The real win is **saving and restoring KV caches** so a returning agent doesn't re-encode its entire context. MLX supports this:

```python
import mlx.core as mx
from mlx_lm import load
from mlx_lm.models.cache import make_prompt_cache

model, tokenizer = load("mlx-community/Mistral-7B-v0.3-4bit")

# Per-agent: build and save KV cache after system prompt
cache = make_prompt_cache(model)
# ... run prefill on system prompt + history ...
# Save cache state (list of mx.arrays)
saved = [mx.array(layer) for layer in cache]
mx.save("agent_A.safetensors", {"cache": mx.stack(saved)})

# Restore later
loaded = mx.load("agent_A.safetensors")
# Hydrate back into cache object
```

`make_prompt_cache` was added specifically for this. The savings are massive for agents with long system prompts or tool histories.

---

## OSS Projects Worth Studying / Reusing

### `mlx-lm` itself
- **Source**: `mlx_lm/server.py` — FastAPI + asyncio queue, good reference for the scaffold
- The `generate_step` generator + `make_prompt_cache` are your primitives
- GitHub: `ml-explore/mlx-lm`

### `llama-swap`
- Lightweight HTTP proxy that sits in front of any OpenAI-compatible server (Ollama, llama.cpp, mlx_lm)
- Handles model swapping, request queuing, and routing by model name
- **Very relevant** — you can use it to route different agents to different model configs
- GitHub: `mostlygeek/llama-swap`

### `llama.cpp` server slot design
- Not MLX, but the **slot architecture** is the gold standard to copy
- Each "slot" is a saved KV cache + sequence state for a session
- Implements LRU eviction when slots fill up
- Study `llama_server.cpp` → `server_slot` struct

### `LiteLLM`
- Acts as a universal proxy with queuing, rate limiting, and routing
- Can sit in front of your mlx_lm server
- Gives you per-agent spend tracking, priority queues, fallbacks
- GitHub: `BerriAI/litellm`

### `aiohttp` / `asyncio.Queue`
- For your custom scaffolding, Python's native async queue is sufficient
- Priority queue via `asyncio.PriorityQueue` — your firewall agent can get queue priority

---

## Recommended Architecture

```
┌─────────────┐   ┌─────────────┐   ┌──────────────┐
│  opencode   │   │  openclaw   │   │ agentic FW   │
└──────┬──────┘   └──────┬──────┘   └──────┬───────┘
       │                 │                  │  (priority)
       └─────────────────┴──────────────────┘
                         │
              ┌──────────▼──────────┐
              │   Your Proxy Layer  │  ← asyncio.PriorityQueue
              │  (FastAPI / aiohttp)│  ← per-agent KV cache registry
              └──────────┬──────────┘
                         │
              ┌──────────▼──────────┐
              │    mlx_lm runner    │  ← single inference worker
              │  + cache swapper    │  ← serialize/restore on switch
              └─────────────────────┘
```

Key design decisions for your proxy layer:

- **One inference worker thread** — everything funnels through it, no locking races
- **Cache registry** — dict of `agent_id → saved KV cache` (in-memory first, spill to disk with `mx.save` / `safetensors`)
- **LRU eviction** — Metal memory is limited; evict cold caches to disk
- **Priority slots** — your firewall agent bypasses the queue via `PriorityQueue`
- **Prefix dedup** — agents sharing a system prompt share one cached KV prefix (huge memory win)

---

## Concrete Starting Point

I'd clone `mlx-lm` and modify `server.py` to add:
1. A `CacheRegistry` class wrapping a dict + LRU + `mx.save/load`
2. Replace the simple request handler with a `PriorityQueue` worker loop
3. Before each generation, check if the agent has a warm cache and restore it
4. After generation (or on preemption), save the updated cache back

`llama-swap` is worth deploying immediately as a stopgap while you build the proper solution — it'll at least give you routing and basic queueing with zero code.

Want me to sketch out the `CacheRegistry` + worker loop code structure?This is a great systems problem. Here's a breakdown of the landscape and reusable OSS pieces:

## The Core Challenge

MLX runs on the Metal GPU and is inherently single-threaded for inference — you can't truly parallelize model forward passes. So your architecture is really about **smart serialization + fast context restoration**, not true concurrency.

---

## Tier 1: Just Use `mlx_lm.server` (Baseline)

`mlx-lm` ships a FastAPI-based OpenAI-compatible server out of the box:

```bash
mlx_lm.server --model mlx-community/Mistral-7B-Instruct-v0.3-4bit --port 8080
```

It already serializes requests. Your agents (opencode, openclaw, your firewall) can all point at it. The problem: **no KV cache persistence across requests** — each call is cold. This is your starting point to beat.

---

## Tier 2: KV Cache Swapping (The Key Insight)

The real win is **saving and restoring KV caches** so a returning agent doesn't re-encode its entire context. MLX supports this:

```python
import mlx.core as mx
from mlx_lm import load
from mlx_lm.models.cache import make_prompt_cache

model, tokenizer = load("mlx-community/Mistral-7B-v0.3-4bit")

# Per-agent: build and save KV cache after system prompt
cache = make_prompt_cache(model)
# ... run prefill on system prompt + history ...
# Save cache state (list of mx.arrays)
saved = [mx.array(layer) for layer in cache]
mx.save("agent_A.safetensors", {"cache": mx.stack(saved)})

# Restore later
loaded = mx.load("agent_A.safetensors")
# Hydrate back into cache object
```

`make_prompt_cache` was added specifically for this. The savings are massive for agents with long system prompts or tool histories.

---

## OSS Projects Worth Studying / Reusing

### `mlx-lm` itself
- **Source**: `mlx_lm/server.py` — FastAPI + asyncio queue, good reference for the scaffold
- The `generate_step` generator + `make_prompt_cache` are your primitives
- GitHub: `ml-explore/mlx-lm`

### `llama-swap`
- Lightweight HTTP proxy that sits in front of any OpenAI-compatible server (Ollama, llama.cpp, mlx_lm)
- Handles model swapping, request queuing, and routing by model name
- **Very relevant** — you can use it to route different agents to different model configs
- GitHub: `mostlygeek/llama-swap`

### `llama.cpp` server slot design
- Not MLX, but the **slot architecture** is the gold standard to copy
- Each "slot" is a saved KV cache + sequence state for a session
- Implements LRU eviction when slots fill up
- Study `llama_server.cpp` → `server_slot` struct

### `LiteLLM`
- Acts as a universal proxy with queuing, rate limiting, and routing
- Can sit in front of your mlx_lm server
- Gives you per-agent spend tracking, priority queues, fallbacks
- GitHub: `BerriAI/litellm`

### `aiohttp` / `asyncio.Queue`
- For your custom scaffolding, Python's native async queue is sufficient
- Priority queue via `asyncio.PriorityQueue` — your firewall agent can get queue priority

---

## Recommended Architecture

```
┌─────────────┐   ┌─────────────┐   ┌──────────────┐
│  opencode   │   │  openclaw   │   │ agentic FW   │
└──────┬──────┘   └──────┬──────┘   └──────┬───────┘
       │                 │                  │  (priority)
       └─────────────────┴──────────────────┘
                         │
              ┌──────────▼──────────┐
              │   Your Proxy Layer  │  ← asyncio.PriorityQueue
              │  (FastAPI / aiohttp)│  ← per-agent KV cache registry
              └──────────┬──────────┘
                         │
              ┌──────────▼──────────┐
              │    mlx_lm runner    │  ← single inference worker
              │  + cache swapper    │  ← serialize/restore on switch
              └─────────────────────┘
```

Key design decisions for your proxy layer:

- **One inference worker thread** — everything funnels through it, no locking races
- **Cache registry** — dict of `agent_id → saved KV cache` (in-memory first, spill to disk with `mx.save` / `safetensors`)
- **LRU eviction** — Metal memory is limited; evict cold caches to disk
- **Priority slots** — your firewall agent bypasses the queue via `PriorityQueue`
- **Prefix dedup** — agents sharing a system prompt share one cached KV prefix (huge memory win)

---

## Concrete Starting Point

I'd clone `mlx-lm` and modify `server.py` to add:
1. A `CacheRegistry` class wrapping a dict + LRU + `mx.save/load`
2. Replace the simple request handler with a `PriorityQueue` worker loop
3. Before each generation, check if the agent has a warm cache and restore it
4. After generation (or on preemption), save the updated cache back

`llama-swap` is worth deploying immediately as a stopgap while you build the proper solution — it'll at least give you routing and basic queueing with zero code.

Want me to sketch out the `CacheRegistry` + worker loop code structure?

Let me build this out as a complete, runnable scaffold. I'll create three files: the cache registry, the inference worker, and the FastAPI proxy server.Here's what was built and why each piece is designed the way it is:

**`cache_registry.py`** — The `CacheRegistry` is an `OrderedDict`-backed LRU store. Each agent gets a `_Slot` containing its live `mx.array` cache layers and metadata. When you exceed `max_ram_slots`, the LRU slot is serialised to `.safetensors` via `mx.save_safetensors` and the in-memory arrays are freed. Restoration is lazy — only happens when that agent next submits a request. There's also a `get_shared_prefix_cache()` method for the common-system-prompt case: encode it once under a shared key like `__system__`, then every agent shallow-copies that cache as their starting point.

**`inference_worker.py`** — One `asyncio.PriorityQueue` feeds one `_inference_loop` task. The loop is the *only* thing that touches the model. Priorities map cleanly to your use case: `CRITICAL=0` for your firewall, `HIGH=1` for opencode/openclaw, etc. The actual MLX work runs in `run_in_executor` to avoid blocking the event loop during long generations, which keeps queue management and SSE streaming responsive. The KV cache swap happens inside `_blocking_inference`: it checks `registry.token_len()` to figure out how many prefix tokens are already encoded, then only encodes the *diff*.

**`server.py`** — Drop-in OpenAI-compatible surface. Agents identify themselves via the `X-Agent-ID` header and `X-Agent-Priority` header, so opencode/openclaw need zero changes beyond pointing their base URL at your local server. The `/stats` endpoint surfaces queue depth + cache hit rate in real time, and `/cache/{agent_id}` lets you manually evict a session (useful when a conversation ends).

A few things to watch out for as you extend this:

The `generate_step` integration in `inference_worker.py` is the part most likely to need tuning — the exact API varies between `mlx-lm` versions, and cache shape differs between model architectures (Mistral vs Llama vs Qwen). Test the cache save/restore round-trip carefully on your specific model before relying on it in production. The `make_prompt_cache` call returns architecture-specific structures, so check what `type(cache[0])` gives you.

# Server.python

"""
server.py — OpenAI-compatible proxy server for MLX inference with KV cache swapping.

Endpoints
---------
POST /v1/chat/completions      — standard + streaming (SSE)
GET  /v1/models                — list available model
GET  /health                   — liveness check
GET  /stats                    — cache + queue diagnostics

Each agent is identified by a custom header:
    X-Agent-ID: opencode          # defaults to "default"
    X-Agent-Priority: HIGH        # CRITICAL / HIGH / NORMAL / LOW

Running
-------
    pip install fastapi uvicorn mlx-lm
    python server.py --model mlx-community/Mistral-7B-v0.3-4bit --port 8080

Your existing agents (opencode, openclaw, etc.) point at http://localhost:8080
with no other changes — it's drop-in OpenAI-compatible.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import time
from pathlib import Path
from typing import AsyncIterator, Optional

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from cache_registry import CacheRegistry
from inference_worker import InferenceWorker, Priority

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("server")

app = FastAPI(title="MLX Proxy", version="0.1.0")

# Populated at startup
_worker: Optional[InferenceWorker] = None
_model_id: str = "local-mlx"


# ---------------------------------------------------------------------------
# Pydantic request / response models (OpenAI-compatible subset)
# ---------------------------------------------------------------------------

class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str = "local-mlx"
    messages: list[Message]
    max_tokens: int = Field(default=512, ge=1, le=8192)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    stream: bool = False
    # Non-standard extension: explicit agent id (also settable via header)
    agent_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve_priority(priority_str: Optional[str]) -> Priority:
    if priority_str is None:
        return Priority.NORMAL
    try:
        return Priority[priority_str.upper()]
    except KeyError:
        return Priority.NORMAL


def _messages_to_prompt(messages: list[Message], tokenizer) -> str:
    """Apply the model's chat template if available, else naïve concatenation."""
    if hasattr(tokenizer, "apply_chat_template"):
        try:
            return tokenizer.apply_chat_template(
                [m.model_dump() for m in messages],
                tokenize=False,
                add_generation_prompt=True,
            )
        except Exception:
            pass
    # Fallback
    parts = []
    for m in messages:
        parts.append(f"<|{m.role}|>\n{m.content}\n")
    parts.append("<|assistant|>\n")
    return "".join(parts)


def _chat_completion_response(result, model_id: str) -> dict:
    return {
        "id": f"chatcmpl-{int(time.time()*1000)}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model_id,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": result.text},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": result.prompt_tokens,
            "completion_tokens": result.completion_tokens,
            "total_tokens": result.prompt_tokens + result.completion_tokens,
        },
        "x_cache_hit": result.cache_hit,
        "x_latency_s": round(result.latency_s, 3),
    }


async def _sse_stream(
    agent_id: str,
    prompt: str,
    priority: Priority,
    max_tokens: int,
    temperature: float,
    model_id: str,
) -> AsyncIterator[str]:
    """Yield SSE-formatted chunks for streaming responses."""
    cmpl_id = f"chatcmpl-{int(time.time()*1000)}"
    created = int(time.time())

    async for chunk in _worker.submit_stream(
        agent_id=agent_id,
        prompt=prompt,
        priority=priority,
        max_tokens=max_tokens,
        temperature=temperature,
    ):
        payload = {
            "id": cmpl_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model_id,
            "choices": [
                {
                    "index": 0,
                    "delta": {"role": "assistant", "content": chunk},
                    "finish_reason": None,
                }
            ],
        }
        yield f"data: {json.dumps(payload)}\n\n"

    # Final chunk signals end
    final = {
        "id": cmpl_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": model_id,
        "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
    }
    yield f"data: {json.dumps(final)}\n\n"
    yield "data: [DONE]\n\n"


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.post("/v1/chat/completions")
async def chat_completions(
    req: ChatRequest,
    x_agent_id: Optional[str] = Header(default=None),
    x_agent_priority: Optional[str] = Header(default=None),
):
    if _worker is None:
        raise HTTPException(503, "Worker not initialised")

    agent_id = req.agent_id or x_agent_id or "default"
    priority = _resolve_priority(x_agent_priority)
    prompt = _messages_to_prompt(req.messages, _worker._tokenizer)

    if req.stream:
        return StreamingResponse(
            _sse_stream(
                agent_id=agent_id,
                prompt=prompt,
                priority=priority,
                max_tokens=req.max_tokens,
                temperature=req.temperature,
                model_id=_model_id,
            ),
            media_type="text/event-stream",
        )

    try:
        result = await _worker.submit(
            agent_id=agent_id,
            prompt=prompt,
            priority=priority,
            max_tokens=req.max_tokens,
            temperature=req.temperature,
            top_p=req.top_p,
        )
    except RuntimeError as exc:
        raise HTTPException(429, str(exc))

    return JSONResponse(_chat_completion_response(result, _model_id))


@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": _model_id,
                "object": "model",
                "owned_by": "local",
                "created": 0,
            }
        ],
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "queue_size": _worker._queue.qsize() if _worker else -1,
    }


@app.get("/stats")
async def stats():
    if _worker is None:
        raise HTTPException(503, "Worker not initialised")
    return {
        "worker": _worker.stats,
        "cache": _worker.registry.stats(),
        "queue_size": _worker._queue.qsize(),
    }


@app.delete("/cache/{agent_id}")
async def evict_cache(agent_id: str):
    """Manually evict a specific agent's cache (e.g. on session end)."""
    if _worker is None:
        raise HTTPException(503, "Worker not initialised")
    _worker.registry.delete(agent_id)
    return {"deleted": agent_id}


# ---------------------------------------------------------------------------
# Startup / shutdown
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup():
    global _worker, _model_id
    # CLI args are parsed before uvicorn starts — stored in app.state
    cfg = app.state.config
    _model_id = cfg.model.split("/")[-1]

    registry = CacheRegistry(
        max_ram_slots=cfg.max_ram_slots,
        cache_dir=Path(cfg.cache_dir),
        max_token_len=cfg.max_token_len,
    )
    _worker = InferenceWorker(
        model_path=cfg.model,
        registry=registry,
        max_queue_depth=cfg.max_queue_depth,
    )
    await _worker.start()
    log.info("Server ready on port %d", cfg.port)


@app.on_event("shutdown")
async def shutdown():
    if _worker:
        await _worker.stop()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(description="MLX proxy server")
    p.add_argument("--model", required=True, help="Model path or HF repo")
    p.add_argument("--port", type=int, default=8080)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--max-ram-slots", type=int, default=4,
                   help="Max warm KV caches in RAM")
    p.add_argument("--cache-dir", default=".cache/kv",
                   help="Directory for spilled KV caches")
    p.add_argument("--max-token-len", type=int, default=8192,
                   help="Caches longer than this are dropped")
    p.add_argument("--max-queue-depth", type=int, default=64)
    p.add_argument("--workers", type=int, default=1,
                   help="Uvicorn worker count (keep at 1 for MLX)")
    return p.parse_args()


if __name__ == "__main__":
    cfg = parse_args()
    app.state.config = cfg
    uvicorn.run(
        app,
        host=cfg.host,
        port=cfg.port,
        workers=1,          # MUST be 1 — MLX owns Metal exclusively
        loop="asyncio",
    )
# Inference Worker:

    """
inference_worker.py — Serialised MLX inference with priority queuing and KV swap.

Architecture
------------
One asyncio task (`_inference_loop`) owns the model exclusively. All callers
submit `InferenceRequest` objects to an `asyncio.PriorityQueue`. Results (or
errors) are delivered back via per-request `asyncio.Future` objects — callers
just `await` the future and never touch the model directly.

Priority levels (lower = higher priority):
    0 : CRITICAL — firewall / safety agents
    1 : HIGH     — interactive / user-facing agents (opencode, openclaw)
    2 : NORMAL   — background tasks
    3 : LOW      — batch / eval jobs

Usage (from your FastAPI route):
    worker = InferenceWorker(model, tokenizer, registry)
    await worker.start()

    result = await worker.submit(
        agent_id="opencode",
        messages=[{"role": "user", "content": "..."}],
        priority=Priority.HIGH,
        max_tokens=512,
    )
    print(result.text)
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import IntEnum
from typing import AsyncIterator, Optional

import mlx.core as mx
from mlx_lm import load
from mlx_lm.models.cache import make_prompt_cache
from mlx_lm.utils import generate_step

from cache_registry import CacheRegistry

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Priority levels
# ---------------------------------------------------------------------------

class Priority(IntEnum):
    CRITICAL = 0   # firewall / safety
    HIGH     = 1   # interactive agents
    NORMAL   = 2   # default
    LOW      = 3   # batch / background


# ---------------------------------------------------------------------------
# Request / Result types
# ---------------------------------------------------------------------------

@dataclass(order=True)
class InferenceRequest:
    priority: int
    # tie-break on submission order so equal-priority requests are FIFO
    seq: int = field(compare=True)

    # ---- actual payload (not compared) ----
    agent_id: str         = field(compare=False)
    prompt: str           = field(compare=False)
    max_tokens: int       = field(compare=False, default=512)
    temperature: float    = field(compare=False, default=0.7)
    top_p: float          = field(compare=False, default=0.9)
    repetition_penalty: float = field(compare=False, default=1.0)
    stream: bool          = field(compare=False, default=False)

    # Populated by the worker
    future: asyncio.Future = field(compare=False, default=None)
    # For streaming: a queue the worker pushes token chunks into
    stream_queue: Optional[asyncio.Queue] = field(compare=False, default=None)

    submitted_at: float = field(compare=False, default_factory=time.monotonic)


@dataclass
class InferenceResult:
    agent_id: str
    text: str
    prompt_tokens: int
    completion_tokens: int
    latency_s: float
    cache_hit: bool


# ---------------------------------------------------------------------------
# Worker
# ---------------------------------------------------------------------------

class InferenceWorker:
    """
    Manages the model and serialises all inference through a priority queue.

    Parameters
    ----------
    model_path : str
        HuggingFace / local path passed to mlx_lm.load().
    registry : CacheRegistry
        Shared cache registry (can also be used by multiple workers
        if you ever shard across models).
    max_queue_depth : int
        Drop requests with an error if the queue is full (back-pressure).
    """

    def __init__(
        self,
        model_path: str,
        registry: CacheRegistry,
        max_queue_depth: int = 64,
    ):
        self.model_path = model_path
        self.registry = registry
        self.max_queue_depth = max_queue_depth

        self._model = None
        self._tokenizer = None
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue(
            maxsize=max_queue_depth
        )
        self._seq_counter = 0
        self._task: Optional[asyncio.Task] = None
        self._running = False

        # Metrics
        self.stats = {
            "requests_served": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total_tokens": 0,
            "queue_drops": 0,
        }

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Load model and start the inference loop."""
        log.info("Loading model from %s …", self.model_path)
        loop = asyncio.get_running_loop()
        # Load in executor so we don't block the event loop during startup
        self._model, self._tokenizer = await loop.run_in_executor(
            None, lambda: load(self.model_path)
        )
        log.info("Model loaded. Starting inference loop.")
        self._running = True
        self._task = asyncio.create_task(self._inference_loop())

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    # ------------------------------------------------------------------
    # Public submit API
    # ------------------------------------------------------------------

    async def submit(
        self,
        agent_id: str,
        prompt: str,
        priority: Priority = Priority.NORMAL,
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        repetition_penalty: float = 1.0,
    ) -> InferenceResult:
        """
        Submit a request and wait for the complete result.
        Raises asyncio.QueueFull if the queue is at capacity.
        """
        future = asyncio.get_running_loop().create_future()
        req = self._make_request(
            agent_id=agent_id,
            prompt=prompt,
            priority=priority,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            repetition_penalty=repetition_penalty,
            future=future,
        )
        try:
            self._queue.put_nowait(req)
        except asyncio.QueueFull:
            self.stats["queue_drops"] += 1
            raise RuntimeError(
                f"Inference queue full ({self.max_queue_depth}). "
                "Try again or increase max_queue_depth."
            )
        return await future

    async def submit_stream(
        self,
        agent_id: str,
        prompt: str,
        priority: Priority = Priority.NORMAL,
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """
        Submit a streaming request. Yields token chunks as they arrive.

        Usage:
            async for chunk in worker.submit_stream("agent_A", prompt):
                print(chunk, end="", flush=True)
        """
        stream_queue: asyncio.Queue = asyncio.Queue()
        future = asyncio.get_running_loop().create_future()
        req = self._make_request(
            agent_id=agent_id,
            prompt=prompt,
            priority=priority,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
            future=future,
            stream_queue=stream_queue,
        )
        self._queue.put_nowait(req)

        # Drain the stream queue until the sentinel None arrives
        while True:
            chunk = await stream_queue.get()
            if chunk is None:
                break
            yield chunk

    # ------------------------------------------------------------------
    # Core inference loop (runs as a single asyncio task)
    # ------------------------------------------------------------------

    async def _inference_loop(self) -> None:
        log.info("Inference loop started.")
        while self._running:
            try:
                req: InferenceRequest = await asyncio.wait_for(
                    self._queue.get(), timeout=1.0
                )
            except asyncio.TimeoutError:
                continue

            try:
                queue_wait = time.monotonic() - req.submitted_at
                log.info(
                    "Serving agent=%s priority=%s waited=%.2fs",
                    req.agent_id, Priority(req.priority).name, queue_wait
                )
                result = await self._run_inference(req)
                if not req.future.done():
                    req.future.set_result(result)
            except Exception as exc:
                log.exception("Inference error for %s", req.agent_id)
                if req.future and not req.future.done():
                    req.future.set_exception(exc)
                if req.stream_queue:
                    await req.stream_queue.put(None)  # unblock consumer
            finally:
                self._queue.task_done()

    async def _run_inference(self, req: InferenceRequest) -> InferenceResult:
        loop = asyncio.get_running_loop()
        # Offload blocking MLX work to a thread executor
        return await loop.run_in_executor(None, self._blocking_inference, req)

    def _blocking_inference(self, req: InferenceRequest) -> InferenceResult:
        """
        Runs synchronously in a thread pool. All MLX calls are here.

        Steps:
          1. Tokenise the prompt.
          2. Try to warm-restore the agent's KV cache.
          3. If cache hit: skip prefix tokens already encoded (run only new tail).
          4. Run generate_step until max_tokens or EOS.
          5. Persist the updated cache back to the registry.
        """
        t0 = time.monotonic()
        model = self._model
        tokenizer = self._tokenizer

        # ---- tokenise ----
        input_ids: list[int] = tokenizer.encode(req.prompt)
        prompt_tokens = len(input_ids)

        # ---- KV cache restore ----
        prev_len = self.registry.token_len(req.agent_id)
        cache = self.registry.load(req.agent_id, model)
        cache_hit = cache is not None

        if cache_hit and prev_len < len(input_ids):
            # Only encode the *new* tail tokens — the prefix is already in cache
            new_tokens = input_ids[prev_len:]
            log.debug(
                "Cache hit: skipping %d prefix tokens, encoding %d new",
                prev_len, len(new_tokens),
            )
        else:
            # Cold start — full prefill
            new_tokens = input_ids
            cache = make_prompt_cache(model)
            cache_hit = False

        # ---- prefill new tokens ----
        if new_tokens:
            prefill_tensor = mx.array(new_tokens)[None]
            _, cache = model(prefill_tensor, cache=cache)
            mx.eval(cache)

        # ---- generate ----
        generated_ids: list[int] = []
        last_token = mx.array([input_ids[-1]])

        for token, _ in generate_step(
            last_token,
            model,
            temperature=req.temperature,
            top_p=req.top_p,
            repetition_penalty=req.repetition_penalty,
            cache=cache,
        ):
            tok_id = token.item()

            # Check EOS
            if tok_id in (tokenizer.eos_token_id, tokenizer.pad_token_id):
                break

            generated_ids.append(tok_id)

            # Streaming: push decoded chunk into the queue
            if req.stream and req.stream_queue:
                chunk = tokenizer.decode([tok_id])
                req.stream_queue.put_nowait(chunk)

            if len(generated_ids) >= req.max_tokens:
                break

        # Signal end-of-stream
        if req.stream and req.stream_queue:
            req.stream_queue.put_nowait(None)

        # ---- save updated cache ----
        self.registry.save(
            req.agent_id,
            model,
            cache,
            token_len=len(input_ids) + len(generated_ids),
        )

        generated_text = tokenizer.decode(generated_ids)
        latency = time.monotonic() - t0

        # ---- update stats ----
        self.stats["requests_served"] += 1
        self.stats["total_tokens"] += len(generated_ids)
        if cache_hit:
            self.stats["cache_hits"] += 1
        else:
            self.stats["cache_misses"] += 1

        log.info(
            "agent=%s tokens=%d latency=%.2fs cache=%s",
            req.agent_id, len(generated_ids), latency,
            "HIT" if cache_hit else "MISS",
        )

        return InferenceResult(
            agent_id=req.agent_id,
            text=generated_text,
            prompt_tokens=prompt_tokens,
            completion_tokens=len(generated_ids),
            latency_s=latency,
            cache_hit=cache_hit,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _make_request(self, **kwargs) -> InferenceRequest:
        self._seq_counter += 1
        return InferenceRequest(seq=self._seq_counter, **kwargs)

# Cache registry:

"""
cache_registry.py — Per-agent KV cache registry with LRU eviction and disk spill.

Each agent gets a named slot. Warm caches live in RAM (mx.arrays). When RAM
pressure hits the limit, least-recently-used caches are serialised to disk via
safetensors so they can be rehydrated on the next request without re-encoding
the full prompt.

Usage:
    registry = CacheRegistry(max_ram_slots=4, cache_dir=Path(".cache/kv"))
    registry.save("agent_A", model, cache)
    cache = registry.load("agent_A", model)   # None → cold start
    registry.delete("agent_A")
"""

from __future__ import annotations

import logging
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import mlx.core as mx
import numpy as np
from mlx_lm.models.cache import make_prompt_cache

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal slot
# ---------------------------------------------------------------------------

@dataclass
class _Slot:
    agent_id: str
    # Live mx.array cache layers — None when evicted to disk
    layers: Optional[list] = None
    # Token length at save time (used for context-length checks)
    token_len: int = 0
    # Approximate size in bytes (RAM estimate)
    ram_bytes: int = 0
    last_used: float = field(default_factory=time.monotonic)
    on_disk: bool = False

    def touch(self):
        self.last_used = time.monotonic()


# ---------------------------------------------------------------------------
# Public registry
# ---------------------------------------------------------------------------

class CacheRegistry:
    """
    Thread-safe (asyncio single-threaded) LRU registry of per-agent KV caches.

    Parameters
    ----------
    max_ram_slots : int
        How many agent caches to keep warm in Metal/RAM simultaneously.
        When exceeded, the LRU slot is spilled to disk.
    cache_dir : Path
        Where spilled caches are written (.safetensors format).
    max_token_len : int
        Caches whose token_len exceeds this are dropped rather than saved —
        they would eat too much RAM on restore.
    """

    def __init__(
        self,
        max_ram_slots: int = 4,
        cache_dir: Path = Path(".cache/kv"),
        max_token_len: int = 8192,
    ):
        self.max_ram_slots = max_ram_slots
        self.cache_dir = Path(cache_dir)
        self.max_token_len = max_token_len
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Ordered by insertion/access — back = most recently used
        self._slots: OrderedDict[str, _Slot] = OrderedDict()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save(self, agent_id: str, model, cache: list, token_len: int = 0) -> None:
        """
        Persist the KV cache for agent_id.

        Parameters
        ----------
        agent_id : str
            Unique identifier for the agent/session.
        model : mlx_lm model
            The loaded model (used only for make_prompt_cache shape info).
        cache : list
            The live cache object returned by make_prompt_cache / generate_step.
        token_len : int
            Number of tokens already encoded in this cache.
        """
        if token_len > self.max_token_len:
            log.warning(
                "Cache for %s has %d tokens (limit %d) — dropping.",
                agent_id, token_len, self.max_token_len,
            )
            return

        # Evaluate all pending Metal ops so we capture committed state
        mx.eval(*[layer for layer in cache if isinstance(layer, mx.array)])

        ram_bytes = self._estimate_bytes(cache)

        slot = _Slot(
            agent_id=agent_id,
            layers=cache,
            token_len=token_len,
            ram_bytes=ram_bytes,
        )
        slot.touch()

        self._slots[agent_id] = slot
        self._slots.move_to_end(agent_id)  # mark MRU

        # Evict if over budget
        self._evict_if_needed()

    def load(self, agent_id: str, model) -> Optional[list]:
        """
        Retrieve the KV cache for agent_id, rehydrating from disk if necessary.

        Returns None on a cache miss (cold start).
        """
        slot = self._slots.get(agent_id)
        if slot is None:
            log.debug("Cache miss for %s (cold start)", agent_id)
            return None

        slot.touch()
        self._slots.move_to_end(agent_id)

        if slot.on_disk:
            log.info("Cache hit (disk) for %s — rehydrating", agent_id)
            cache = self._load_from_disk(agent_id, model)
            if cache is None:
                del self._slots[agent_id]
                return None
            slot.layers = cache
            slot.on_disk = False
            slot.ram_bytes = self._estimate_bytes(cache)
            self._evict_if_needed()
            return cache

        log.debug("Cache hit (RAM) for %s (%d tokens)", agent_id, slot.token_len)
        return slot.layers

    def delete(self, agent_id: str) -> None:
        """Evict and remove a cache slot entirely."""
        slot = self._slots.pop(agent_id, None)
        if slot is None:
            return
        disk_path = self._disk_path(agent_id)
        if disk_path.exists():
            disk_path.unlink()
        log.debug("Deleted cache for %s", agent_id)

    def token_len(self, agent_id: str) -> int:
        """Return the stored token length for agent_id, or 0 if missing."""
        slot = self._slots.get(agent_id)
        return slot.token_len if slot else 0

    def stats(self) -> dict:
        ram_slots = [s for s in self._slots.values() if not s.on_disk]
        disk_slots = [s for s in self._slots.values() if s.on_disk]
        return {
            "total_agents": len(self._slots),
            "ram_slots": len(ram_slots),
            "disk_slots": len(disk_slots),
            "ram_bytes": sum(s.ram_bytes for s in ram_slots),
            "agents": {
                aid: {
                    "token_len": s.token_len,
                    "on_disk": s.on_disk,
                    "last_used_ago_s": round(time.monotonic() - s.last_used, 1),
                }
                for aid, s in self._slots.items()
            },
        }

    # ------------------------------------------------------------------
    # Prefix deduplication helper
    # ------------------------------------------------------------------

    def get_shared_prefix_cache(self, prefix_id: str, model, prompt_tokens: list) -> Optional[list]:
        """
        Return a *copy* of a shared prefix cache (e.g. a common system prompt).

        The copy is safe to extend per-agent without polluting the shared slot.
        Callers own the returned cache and should save it back under their own
        agent_id after generation.
        """
        cache = self.load(prefix_id, model)
        if cache is None:
            return None
        # Shallow-copy the list; mx.arrays are immutable so this is safe
        return list(cache)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _evict_if_needed(self) -> None:
        ram_slots = [aid for aid, s in self._slots.items() if not s.on_disk]
        while len(ram_slots) > self.max_ram_slots:
            lru_id = ram_slots.pop(0)  # front = least recently used
            self._spill_to_disk(lru_id)

    def _spill_to_disk(self, agent_id: str) -> None:
        slot = self._slots.get(agent_id)
        if slot is None or slot.on_disk or slot.layers is None:
            return
        path = self._disk_path(agent_id)
        try:
            arrays = {
                f"layer_{i}": mx.array(layer)
                for i, layer in enumerate(slot.layers)
                if isinstance(layer, (mx.array, list))
            }
            # Also persist metadata as a scalar
            arrays["_token_len"] = mx.array([slot.token_len])
            mx.save_safetensors(str(path), arrays)
            slot.layers = None
            slot.on_disk = True
            slot.ram_bytes = 0
            log.info("Spilled cache for %s to %s", agent_id, path)
        except Exception as exc:
            log.error("Failed to spill cache for %s: %s", agent_id, exc)

    def _load_from_disk(self, agent_id: str, model) -> Optional[list]:
        path = self._disk_path(agent_id)
        if not path.exists():
            log.warning("Disk cache missing for %s", agent_id)
            return None
        try:
            arrays = mx.load(str(path))
            token_len_arr = arrays.pop("_token_len", None)
            if token_len_arr is not None:
                self._slots[agent_id].token_len = int(token_len_arr[0])
            # Reconstruct cache in layer index order
            max_idx = max(int(k.split("_")[1]) for k in arrays)
            cache = [arrays[f"layer_{i}"] for i in range(max_idx + 1)]
            return cache
        except Exception as exc:
            log.error("Failed to load cache for %s from disk: %s", agent_id, exc)
            return None

    def _disk_path(self, agent_id: str) -> Path:
        safe = agent_id.replace("/", "_").replace(":", "_")
        return self.cache_dir / f"{safe}.safetensors"

    @staticmethod
    def _estimate_bytes(cache: list) -> int:
        total = 0
        for layer in cache:
            if isinstance(layer, mx.array):
                total += layer.nbytes
            elif isinstance(layer, (list, tuple)):
                for sub in layer:
                    if isinstance(sub, mx.array):
                        total += sub.nbytes
        return total


# Example Usage:

"""
example_usage.py — Test the proxy directly (no HTTP) and via OpenAI client.

Run the server first:
    python server.py --model mlx-community/Mistral-7B-Instruct-v0.3-4bit

Then run this file:
    python example_usage.py
"""

from __future__ import annotations

import asyncio
import time
from pathlib import Path

# ---- Direct usage (no HTTP) ----

async def demo_direct():
    """
    Use the worker directly — useful for testing or embedding in another process.
    """
    from cache_registry import CacheRegistry
    from inference_worker import InferenceWorker, Priority

    registry = CacheRegistry(max_ram_slots=3, cache_dir=Path(".cache/kv"))
    worker = InferenceWorker(
        model_path="mlx-community/Mistral-7B-Instruct-v0.3-4bit",
        registry=registry,
    )
    await worker.start()

    system = "<s>[INST] You are a helpful coding assistant. [/INST]"

    # --- Warm up each agent's system prompt (shared prefix trick) ---
    # Pre-encode the system prompt once and save under a shared key
    result = await worker.submit(
        agent_id="__system_prefix__",
        prompt=system,
        priority=Priority.CRITICAL,
        max_tokens=1,  # just prefill, don't generate
    )
    print(f"Prefix cache seeded: {result.prompt_tokens} tokens")

    # --- Simulate 3 concurrent agent requests ---
    async def agent_call(name: str, question: str, prio: Priority):
        prompt = system + f"\n{question} [/INST]"
        t0 = time.monotonic()
        result = await worker.submit(
            agent_id=name,
            prompt=prompt,
            priority=prio,
            max_tokens=200,
        )
        print(
            f"[{name}] cache={'HIT' if result.cache_hit else 'MISS'} "
            f"tokens={result.completion_tokens} latency={result.latency_s:.2f}s\n"
            f"  -> {result.text[:80]}…\n"
        )
        return result

    # Fire all three concurrently — the worker serialises them by priority
    results = await asyncio.gather(
        agent_call("agentic_firewall", "Is this prompt safe?", Priority.CRITICAL),
        agent_call("opencode",         "Write a Python hello world", Priority.HIGH),
        agent_call("openclaw",         "Summarise the repo structure", Priority.NORMAL),
    )

    # --- Second round: cache should be warm for all agents ---
    print("\n=== Round 2 (caches should be warm) ===\n")
    results2 = await asyncio.gather(
        agent_call("opencode", "Now add type hints", Priority.HIGH),
        agent_call("openclaw", "List the top 3 files", Priority.NORMAL),
    )

    print("\nWorker stats:", worker.stats)
    print("Cache stats:", registry.stats())

    await worker.stop()


# ---- HTTP usage via openai client ----

async def demo_openai_client():
    """
    Drop-in usage: point any OpenAI-compatible client at localhost:8080.
    Requires: pip install openai
    """
    try:
        from openai import AsyncOpenAI
    except ImportError:
        print("pip install openai to run this demo")
        return

    client = AsyncOpenAI(
        base_url="http://localhost:8080/v1",
        api_key="not-needed",
    )

    # Each agent sends its ID via the model field or a custom header
    # (the server reads X-Agent-ID header; openai client doesn't support
    #  custom headers directly, so use extra_headers on the request)

    response = await client.chat.completions.create(
        model="local-mlx",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user",   "content": "What is the capital of France?"},
        ],
        max_tokens=64,
        extra_headers={"X-Agent-ID": "opencode", "X-Agent-Priority": "HIGH"},
    )
    print("Non-streaming:", response.choices[0].message.content)

    # Streaming
    print("\nStreaming: ", end="")
    stream = await client.chat.completions.create(
        model="local-mlx",
        messages=[{"role": "user", "content": "Count from 1 to 5."}],
        max_tokens=64,
        stream=True,
        extra_headers={"X-Agent-ID": "opencode"},
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta.content or ""
        print(delta, end="", flush=True)
    print()


# ---- Priority queue stress test ----

async def demo_priority_stress():
    """
    Submit a burst of mixed-priority requests and verify the firewall
    agent always finishes first despite being submitted last.
    """
    from cache_registry import CacheRegistry
    from inference_worker import InferenceWorker, Priority

    registry = CacheRegistry(max_ram_slots=2)
    worker = InferenceWorker(
        "mlx-community/Mistral-7B-Instruct-v0.3-4bit",
        registry,
        max_queue_depth=32,
    )
    await worker.start()

    completion_order = []

    async def timed_submit(name, prompt, prio):
        result = await worker.submit(
            agent_id=name, prompt=prompt,
            priority=prio, max_tokens=32,
        )
        completion_order.append(name)
        return result

    # Submit LOW jobs first to fill the queue, then CRITICAL
    tasks = [
        asyncio.create_task(timed_submit(f"batch_{i}", "Hello", Priority.LOW))
        for i in range(5)
    ]
    # Give the queue a moment to fill before critical arrives
    await asyncio.sleep(0.05)
    tasks.insert(0,
        asyncio.create_task(timed_submit("firewall", "Is this safe?", Priority.CRITICAL))
    )

    await asyncio.gather(*tasks)
    print("Completion order:", completion_order)
    assert completion_order[0] == "firewall", "Firewall should complete first!"
    print("Priority ordering verified.")

    await worker.stop()


if __name__ == "__main__":
    import sys
    demo = sys.argv[1] if len(sys.argv) > 1 else "direct"
    if demo == "direct":
        asyncio.run(demo_direct())
    elif demo == "http":
        asyncio.run(demo_openai_client())
    elif demo == "stress":
        asyncio.run(demo_priority_stress())
    else:
        print("Usage: python example_usage.py [direct|http|stress]")


