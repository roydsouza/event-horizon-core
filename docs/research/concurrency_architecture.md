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

# Question:

How do I detect instability in my implementation as models get more sophisticated over time, and make prefix caching more complicated? How can I monitor this and know when to step in with an enhancement?

# Gemini:

Detecting instability in local MLX implementations as models move toward hybrid architectures (like **Gemma 3** or **Qwen 3.5**) requires shifting your focus from simple "cache hits" to measuring **architectural compatibility** and **latency regressions**.

### 1. The Primary Instability: "The Silent Recompute"
As of March 2026, the most common form of "instability" isn't a crash, but a **performance collapse**. Modern models increasingly use non-standard layers that are fundamentally incompatible with traditional "trim-and-reuse" prefix caching.

* **Hybrid SSM/Mamba Models (e.g., Qwen 3.5):** These use recurrent states that cannot be split or "trimmed" at arbitrary token boundaries like a standard KV cache.
* **Sliding Window Models (e.g., Gemma 3):** These use circular buffers (`RotatingKVCache`). If your server tries to trim this cache to match a common prefix, the state often corrupts, forcing a silent fallback to full prompt recomputation.
* **Multimodal RoPE (e.g., Qwen3-VL):** If you cache a text prefix and then inject an image, the positional embeddings (mRoPE) often break, causing the model to ignore new visual inputs or hallucinate wildly.

### 2. Monitoring Stack: The "Check Engine" Lights
To detect these issues in your concurrent agent scaffolding, monitor these four specific signals:

| Metric | "Healthy" State | "Intervention Required" Signal |
| :--- | :--- | :--- |
| **TTFT (Time to First Token)** | Flat/Constant (e.g., <500ms) for warm requests. | Scales **linearly** with prefix length (e.g., 10s for 10k tokens). |
| **Prefix Cache Hit Rate** | >80% for repetitive agent loops. | Drops below 10% or is consistently 0% for "warm" models. |
| **Inter-Token Latency (ITL)** | Smooth and steady. | Spikes or "jitter," indicating **KV cache thrashing** or preemptions. |
| **Context Length vs. VRAM** | High utilization but stable. | **Preemption count** > 0 (indicates the server is killing agent contexts to free RAM). |

### 3. How to Detect Semantic & Functional Drift
Instability can also be functional—where the cache "works" but the model becomes "stupid" or incoherent.

* **Logit Divergence Checks:** Periodically compare the first 5–10 tokens of a "cached" generation against a "cold start" generation for the same prefix. If the probability distribution (logits) differs significantly, your cache implementation is likely corrupting **Position IDs** or **RoPE deltas**.
* **The "Context Cliff" Test:** Monitor if your agent starts failing tasks specifically after $N$ turns. This often indicates your caching logic is failing to handle the **sliding window boundary** correctly.
* **TTFT Benchmarking:** If you see your TTFT jump from 1s to 30s after adding a new agent to the scaffolding, it means your locking/queueing is causing "cache misses" by evicting the high-value system prompt blocks.

### 4. When to Step In (Intervention Triggers)
Enhance your scaffolding when you hit these specific thresholds:

1.  **The "2-Second Rule":** If your TTFT for a "warm" request (reusing your system prompt) exceeds 2 seconds on your M5, your prefix caching is likely broken or disabled by a hybrid model architecture.
2.  **The "Dynamic Injection" Failure:** If your agents inject small dynamic pieces (like a `timestamp` or `agent_id`) early in the system prompt, it invalidates everything downstream.
    * *Enhancement:* Implement **Prompt Reordering** to move all dynamic variables to the very end of the prompt.
3.  **VRAM Fragmentation:** If your "agentic firewall" and "OpenCode" are constantly fighting for the same 24GB, and you see `num_preemptions` rising in your logs.
    * *Enhancement:* Move to an **SSD-Tiered KV Cache** (like `oMLX`) that swaps inactive agent states to your Mac's internal storage.

**Would you like me to provide a Python script that uses `mlx-lm` to benchmark your TTFT and detect "Silent Recomputes"?**

Claude: 

Good timing to think about this — cache instability from model upgrades is one of those failure modes that's silent at first (outputs look fine, just subtly wrong) before it becomes catastrophic. There are four distinct failure classes to instrument for.

## The four failure classes

**1. Tokenizer drift** — a model upgrade changes how a prompt tokenizes. Your `token_len` stored in the registry is now wrong, so the "diff" you encode in `_blocking_inference` starts at the wrong offset. The prefix cache hits but poisons the output. This is the nastiest one because it doesn't throw — it just generates garbage.

**2. Cache shape mismatch** — a new model architecture (GQA vs MHA, different head counts, sliding window attention) produces cache arrays with different shapes. Your `mx.load` from disk either silently broadcasts to a wrong shape or raises during the forward pass.

**3. Context budget creep** — newer models advertise 128K context but your `max_token_len` guard was set for 8K. Long-running agents accumulate caches you never expected to be that large, then spill to disk constantly, defeating the purpose.

**4. Semantic divergence** — even with correct shapes and tokenization, a fine-tuned or quantised update shifts the model's internal representations enough that a cached prefix from v1 leads to measurably different outputs on v2. Hard to detect, but measurable.

Here's how to instrument for all four, plus a monitoring layer you can drop into the existing scaffold:Now here's the actual monitoring code to add alongside the existing scaffold:Three new files. Here's the mental model for when each one fires:

**`ModelVersionGuard`** runs at startup only. It computes two fingerprints — one from probe encodings through the tokenizer (catching vocab changes), one from the model's config dict (catching architectural changes like GQA vs MHA or different head counts). If either differs from the last committed run, it wipes all `.safetensors` cache files before the server accepts any traffic. Critically, it fingerprints *actual tokenizer behavior* via probe strings rather than just a version string, because model cards often update the config without bumping a version number.

**`CacheHealthMonitor`** runs continuously. The four signals to watch in order of urgency:

- `mean_divergence` crossing 0.25 is your canary — it means warm-cache outputs are starting to drift from cold-start outputs on the same prompt. This is the earliest possible warning of a cache corruption problem, before users notice anything wrong. The shadow sampler (2% of requests by default) keeps the overhead negligible.
- `shape_mismatch` invalidations appearing at all is a hard bug — the guard should have caught architecture changes. When this fires it means a model was swapped in a way the fingerprint logic didn't detect (e.g. same config, different weights). Warrants immediate investigation.
- `hit_rate` dropping below 50% usually means agents are churning through novel prompts faster than the cache is being reused — a workload change, not a bug. But combined with rising `evictions_last_60s` it means `max_ram_slots` needs to go up.
- `hit_latency_p95` rising while hit rate stays high means Metal memory pressure — another process is competing for GPU memory, or you're spilling to disk so fast the disk round-trip is eating your latency advantage.

The `integration_patch.py` file has a reference table at the bottom mapping each metric to its actionable response. The shape validation hook is the most important thing to actually wire in — it belongs in `CacheRegistry._load_from_disk` right after `mx.load`, before the cache is ever handed to the model.
"""
model_version_guard.py — Detects model upgrades and invalidates stale KV caches.

Two fingerprints are computed at startup and stored alongside caches:
  1. Tokenizer fingerprint — hash of vocab size + special tokens + a set of
     probe encodings. Catches tokenizer updates that would corrupt token_len offsets.
  2. Architecture fingerprint — hash of model config dict. Catches head count,
     layer count, hidden-dim, or attention-type changes that would produce
     incompatible cache shapes.

If either fingerprint mismatches on load, the cache is invalidated before it
can poison inference.
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)

# Canonical probe strings — cover punctuation, code tokens, non-ASCII
_PROBE_STRINGS = [
    "Hello, world!",
    "def foo(x: int) -> str:",
    "SELECT * FROM users WHERE id = 1;",
    "日本語テスト",
    "<|system|>\n<|user|>\n<|assistant|>",
]


def _tokenizer_fingerprint(tokenizer) -> str:
    """
    Build a stable fingerprint of the tokenizer state.
    Sensitive to: vocab changes, special token reassignments, chat template edits.
    """
    parts = [
        str(getattr(tokenizer, "vocab_size", "?")),
        str(getattr(tokenizer, "eos_token_id", "?")),
        str(getattr(tokenizer, "bos_token_id", "?")),
        str(getattr(tokenizer, "pad_token_id", "?")),
    ]
    # Chat template (if present)
    tmpl = getattr(tokenizer, "chat_template", None)
    if tmpl:
        parts.append(hashlib.md5(tmpl.encode()).hexdigest()[:8])

    # Probe encodings — the real test
    for probe in _PROBE_STRINGS:
        try:
            ids = tokenizer.encode(probe)
            parts.append(f"{len(ids)}:{ids[0]}:{ids[-1]}")
        except Exception:
            parts.append("ERR")

    raw = "|".join(parts)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _architecture_fingerprint(model) -> str:
    """
    Fingerprint the model architecture config.
    Catches: layer count, head count, hidden dim, attention type (GQA vs MHA),
    sliding window size, context length, quantisation bits.
    """
    config = {}
    # Try to access the model's internal config dict
    for attr in ("args", "config", "model_config", "params"):
        obj = getattr(model, attr, None)
        if obj is not None:
            if hasattr(obj, "__dict__"):
                config = {
                    k: v for k, v in vars(obj).items()
                    if isinstance(v, (int, float, str, bool, type(None)))
                }
            elif isinstance(obj, dict):
                config = {k: v for k, v in obj.items()
                          if isinstance(v, (int, float, str, bool, type(None)))}
            break

    # Fallback: count parameters as a proxy
    if not config:
        try:
            import mlx.core as mx
            flat = model.parameters()
            if hasattr(flat, "items"):
                config["_param_keys"] = sorted(flat.keys())
        except Exception:
            pass

    raw = json.dumps(config, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


class ModelVersionGuard:
    """
    Persists model fingerprints to disk and checks them on every cache load.

    Usage:
        guard = ModelVersionGuard(model, tokenizer, cache_dir=Path(".cache/kv"))

        # Before loading a cache from the registry:
        if not guard.is_cache_valid(agent_id):
            registry.delete(agent_id)
            # proceed with cold start
    """

    def __init__(self, model, tokenizer, cache_dir: Path):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._fingerprint_path = self.cache_dir / "_model_fingerprint.json"

        self.tok_fp = _tokenizer_fingerprint(tokenizer)
        self.arch_fp = _architecture_fingerprint(model)
        self._current = {"tokenizer": self.tok_fp, "architecture": self.arch_fp}

        self._stored = self._load_stored()
        self._check_global_invalidation()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def model_changed(self) -> bool:
        """True if either fingerprint differs from the last stored run."""
        if self._stored is None:
            return False   # first run — nothing to invalidate
        return (
            self._stored.get("tokenizer") != self.tok_fp
            or self._stored.get("architecture") != self.arch_fp
        )

    @property
    def tokenizer_changed(self) -> bool:
        if self._stored is None:
            return False
        return self._stored.get("tokenizer") != self.tok_fp

    @property
    def architecture_changed(self) -> bool:
        if self._stored is None:
            return False
        return self._stored.get("architecture") != self.arch_fp

    def commit(self) -> None:
        """
        Call after the server is healthy and all stale caches have been dropped.
        Writes the current fingerprints as the new baseline.
        """
        with open(self._fingerprint_path, "w") as f:
            json.dump(self._current, f, indent=2)
        self._stored = self._current.copy()
        log.info(
            "Model fingerprints committed: tok=%s arch=%s",
            self.tok_fp, self.arch_fp,
        )

    def change_summary(self) -> dict:
        return {
            "tokenizer_changed": self.tokenizer_changed,
            "architecture_changed": self.architecture_changed,
            "previous": self._stored,
            "current": self._current,
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _load_stored(self) -> Optional[dict]:
        if not self._fingerprint_path.exists():
            return None
        try:
            with open(self._fingerprint_path) as f:
                return json.load(f)
        except Exception as exc:
            log.warning("Could not read fingerprint file: %s", exc)
            return None

    def _check_global_invalidation(self) -> None:
        if not self.model_changed:
            if self._stored is None:
                log.info("First run — no existing caches to validate.")
            else:
                log.info("Model fingerprints match — caches valid.")
            return

        log.warning(
            "Model change detected! tok_changed=%s arch_changed=%s",
            self.tokenizer_changed, self.architecture_changed,
        )
        if self.tokenizer_changed:
            log.warning(
                "  Tokenizer: %s → %s  (token_len offsets will be wrong!)",
                self._stored.get("tokenizer"), self.tok_fp,
            )
        if self.architecture_changed:
            log.warning(
                "  Architecture: %s → %s  (cache shapes may be incompatible!)",
                self._stored.get("architecture"), self.arch_fp,
            )
        # Wipe all on-disk caches — RAM caches are gone anyway on restart
        stale = list(self.cache_dir.glob("*.safetensors"))
        for p in stale:
            p.unlink()
        log.warning("Deleted %d stale cache files.", len(stale))
"""
integration_patch.py — How to wire ModelVersionGuard and CacheHealthMonitor
into your existing server.py and inference_worker.py.

This file is documentation-as-code. Copy the relevant sections into the
existing files — it is not meant to be imported directly.
"""

# =============================================================================
# PATCH 1: server.py startup — add guard and monitor
# =============================================================================

# In server.py, modify the startup() function:

async def startup_patched():
    from model_version_guard import ModelVersionGuard
    from cache_health_monitor import CacheHealthMonitor

    cfg = app.state.config

    registry = CacheRegistry(
        max_ram_slots=cfg.max_ram_slots,
        cache_dir=Path(cfg.cache_dir),
        max_token_len=cfg.max_token_len,
    )

    # Load model first so we can fingerprint it
    from mlx_lm import load
    model, tokenizer = load(cfg.model)

    # Guard: detects model upgrades and wipes stale caches automatically
    guard = ModelVersionGuard(model, tokenizer, cache_dir=Path(cfg.cache_dir))
    if guard.model_changed:
        print("⚠️  Model change detected:", guard.change_summary())
        # CacheRegistry already wiped disk caches in ModelVersionGuard.__init__
    guard.commit()  # accept current fingerprints as baseline

    # Monitor: shadow sampling + threshold alerts
    def alert_to_structured_log(alert):
        import json, sys
        print(json.dumps({
            "level": alert.level,
            "category": alert.category,
            "agent_id": alert.agent_id,
            "message": alert.message,
            "value": alert.value,
            "threshold": alert.threshold,
        }), file=sys.stderr)

    monitor = CacheHealthMonitor(
        shadow_rate=cfg.shadow_rate,      # add --shadow-rate CLI arg, default 0.02
        alert_callback=alert_to_structured_log,
        thresholds={
            "hit_rate_warn": cfg.hit_rate_warn,  # add CLI args for key thresholds
        },
    )

    # Pass both into the worker
    global _worker, _model_id
    _model_id = cfg.model.split("/")[-1]
    _worker = InferenceWorkerPatched(
        model=model,
        tokenizer=tokenizer,
        registry=registry,
        monitor=monitor,
        max_queue_depth=cfg.max_queue_depth,
    )
    await _worker.start()

    # Periodic threshold check (every 60s)
    async def _periodic_check():
        while True:
            await asyncio.sleep(60)
            alerts = monitor.check_thresholds()
            if alerts:
                print(f"[monitor] {len(alerts)} active alert(s)")

    asyncio.create_task(_periodic_check())


# =============================================================================
# PATCH 2: /stats endpoint — include health snapshot
# =============================================================================

# Replace the existing /stats route body:
async def stats_patched():
    return {
        "worker": _worker.stats,
        "cache": _worker.registry.stats(),
        "health": _worker.monitor.snapshot(),   # <-- add this
        "queue_size": _worker._queue.qsize(),
    }


# =============================================================================
# PATCH 3: inference_worker.py — wire in monitor + shadow checks
# =============================================================================

# Modify InferenceWorker to accept a monitor and patch _blocking_inference:

def _blocking_inference_patched(self, req):
    """
    Drop-in replacement for InferenceWorker._blocking_inference.
    Adds: shape validation on cache load, shadow divergence checks,
    and recording to the health monitor.
    """
    from cache_health_monitor import CacheHealthMonitor
    from mlx_lm.models.cache import make_prompt_cache
    import mlx.core as mx

    t0 = time.monotonic()
    model = self._model
    tokenizer = self._tokenizer

    input_ids = tokenizer.encode(req.prompt)
    prompt_tokens = len(input_ids)

    prev_len = self.registry.token_len(req.agent_id)
    cache = self.registry.load(req.agent_id, model)
    cache_hit = cache is not None

    # Shape validation on load
    if cache_hit:
        empty = make_prompt_cache(model)
        ok, err = CacheHealthMonitor.validate_cache_shapes(cache, empty, req.agent_id)
        if not ok:
            log.warning("Shape mismatch for %s: %s — cold starting", req.agent_id, err)
            self.monitor.record_invalidation(req.agent_id, reason="shape_mismatch")
            cache = empty
            cache_hit = False

    # Shadow check: run cold copy in parallel for divergence measurement
    run_shadow = cache_hit and self.monitor.should_shadow_check()
    warm_output = cold_output = None

    if cache is None or not cache_hit:
        cache = make_prompt_cache(model)

    # ... (normal prefill + generate, same as before) ...
    # result_text = (generated text from generate_step)
    warm_output = "PLACEHOLDER_warm"  # replace with actual generated text

    if run_shadow:
        # Re-run cold (no cache) on a trimmed prompt to limit cost
        shadow_cache = make_prompt_cache(model)
        # shadow_ids = short tail of prompt (last 128 tokens max)
        shadow_ids = input_ids[-128:]
        shadow_tensor = mx.array(shadow_ids)[None]
        _, shadow_cache = model(shadow_tensor, cache=shadow_cache)
        # generate a short sample (32 tokens) to compare
        # cold_output = (decoded shadow tokens)
        cold_output = "PLACEHOLDER_cold"  # replace with actual shadow output

    latency = time.monotonic() - t0

    self.monitor.record(
        agent_id=req.agent_id,
        cache_hit=cache_hit,
        latency_s=latency,
        completion_tokens=0,  # replace with actual count
        warm_output=warm_output if run_shadow else None,
        cold_output=cold_output,
    )
    self.monitor.record_eviction(req.agent_id)  # call only when eviction occurs

    # ... save cache back to registry, return InferenceResult ...


# =============================================================================
# PATCH 4: CacheRegistry._spill_to_disk — notify monitor on eviction
# =============================================================================

# In CacheRegistry._spill_to_disk, after the mx.save_safetensors call,
# call the monitor if one is attached:
#
#   if hasattr(self, '_monitor') and self._monitor:
#       self._monitor.record_eviction(agent_id)
#
# Wire it in __init__:
#   self._monitor = None   # set externally after construction


# =============================================================================
# PATCH 5: CLI args to add to server.py parse_args()
# =============================================================================

def parse_args_additions(p):
    """Additional args to add to the existing argparse setup."""
    p.add_argument("--shadow-rate", type=float, default=0.02,
                   help="Fraction of requests to run as shadow cold checks (0..1)")
    p.add_argument("--hit-rate-warn", type=float, default=0.50,
                   help="Alert when cache hit rate drops below this")
    p.add_argument("--alert-cooldown", type=int, default=300,
                   help="Seconds between repeated alerts for the same category")
    return p


# =============================================================================
# QUICK REFERENCE: What each metric tells you
# =============================================================================
#
# METRIC                    RISING/DROPPING          WHAT IT MEANS
# ──────────────────────────────────────────────────────────────────────────
# hit_rate (per agent)      Dropping                 Agents changing prompts a
#                                                    lot, or cache being evicted
#                                                    before reuse. Raise
#                                                    max_ram_slots or check
#                                                    agent session lifetimes.
#
# invalidation_rate         Spiking                  Model was swapped. Guard
#                                                    should have wiped caches
#                                                    but agents are still
#                                                    submitting stale sessions.
#
# mean_divergence           Crossing 0.25            Cached prefix is leading
#                                                    the model to different
#                                                    generations than cold.
#                                                    Could be quantization
#                                                    difference or architecture
#                                                    change that guard missed.
#
# hit_latency_p95           Rising                   Cache is warm but slow.
#                                                    Either spilling to disk
#                                                    (check evictions_last_60s)
#                                                    or Metal memory pressure
#                                                    from competing processes.
#
# evictions_last_60s        > 10/min                 max_ram_slots too small.
#                                                    Raise it or add a shared
#                                                    prefix slot to reduce per-
#                                                    agent footprint.
#
# shape_mismatch            Any occurrence           New model architecture
#                                                    that guard's config hash
#                                                    didn't catch. Check guard
#                                                    fingerprint logic for the
#                                                    specific model family.
"""
cache_health_monitor.py — Runtime stability monitoring for the KV cache proxy.

What it tracks
--------------
1. Cache hit / miss rates per agent and globally.
2. Cache invalidation events and their reasons (shape mismatch, fingerprint
   change, token overflow, explicit eviction).
3. Shadow divergence — a configurable fraction of requests are run twice: once
   with the warm cache, once cold. The outputs are compared and a divergence
   score is recorded. Rising divergence = model drift or cache corruption.
4. Latency distributions — p50 / p95 / p99 per agent and split by cache
   hit vs miss.
5. Eviction pressure — how often slots are being spilled to disk (sign that
   max_ram_slots is too low for current workload).

Alerting
--------
Thresholds are configurable. When exceeded, alert() is called — wire it to
your preferred sink (structured log, Prometheus, Slack webhook, etc.).

Usage
-----
    monitor = CacheHealthMonitor(shadow_rate=0.02)  # 2% shadow checks

    # In inference_worker._blocking_inference, wrap the result:
    monitor.record(
        agent_id=req.agent_id,
        cache_hit=result.cache_hit,
        latency_s=result.latency_s,
        completion_tokens=result.completion_tokens,
    )

    # On invalidation events:
    monitor.record_invalidation(agent_id, reason="shape_mismatch")

    # Check for alerts (call periodically or from /stats endpoint):
    alerts = monitor.check_thresholds()
"""

from __future__ import annotations

import asyncio
import logging
import math
import random
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Callable, Optional

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class AgentMetrics:
    agent_id: str
    hits: int = 0
    misses: int = 0
    invalidations: int = 0
    invalidation_reasons: dict = field(default_factory=lambda: defaultdict(int))
    # Rolling window of latencies (last 200 requests)
    hit_latencies:  deque = field(default_factory=lambda: deque(maxlen=200))
    miss_latencies: deque = field(default_factory=lambda: deque(maxlen=200))
    # Rolling window of divergence scores (last 50 shadow checks)
    divergence_scores: deque = field(default_factory=lambda: deque(maxlen=50))
    total_tokens: int = 0
    last_seen: float = field(default_factory=time.monotonic)

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    @property
    def request_count(self) -> int:
        return self.hits + self.misses

    def latency_percentile(self, p: float, hit: bool) -> Optional[float]:
        src = self.hit_latencies if hit else self.miss_latencies
        if not src:
            return None
        s = sorted(src)
        idx = max(0, int(math.ceil(p / 100 * len(s))) - 1)
        return s[idx]

    def mean_divergence(self) -> Optional[float]:
        if not self.divergence_scores:
            return None
        return sum(self.divergence_scores) / len(self.divergence_scores)


@dataclass
class Alert:
    level: str          # "warning" | "critical"
    category: str       # "hit_rate" | "divergence" | "invalidation_rate" | "latency" | "eviction"
    agent_id: Optional[str]
    message: str
    value: float
    threshold: float
    ts: float = field(default_factory=time.time)


# ---------------------------------------------------------------------------
# Text similarity (token overlap) for divergence scoring
# ---------------------------------------------------------------------------

def _jaccard_token_overlap(a: str, b: str) -> float:
    """
    Fast proxy for output similarity. Returns 0.0 (identical) .. 1.0 (no overlap).
    Real production use: embed both and compute cosine distance.
    """
    tok_a = set(a.lower().split())
    tok_b = set(b.lower().split())
    if not tok_a and not tok_b:
        return 0.0
    intersection = len(tok_a & tok_b)
    union = len(tok_a | tok_b)
    return 1.0 - (intersection / union if union > 0 else 0.0)


# ---------------------------------------------------------------------------
# Monitor
# ---------------------------------------------------------------------------

class CacheHealthMonitor:
    """
    Collects metrics from the inference worker and surfaces actionable alerts.

    Parameters
    ----------
    shadow_rate : float
        Fraction of requests to duplicate as cold-start shadow checks.
        0.02 = 2%. Keep low; shadows double inference cost for that request.
    alert_callback : callable, optional
        Called with (Alert) whenever a threshold is crossed. Defaults to logging.
    thresholds : dict, optional
        Override default alert thresholds (see _DEFAULT_THRESHOLDS).
    """

    _DEFAULT_THRESHOLDS = {
        # Hit rate below this triggers a warning (after 20+ requests)
        "hit_rate_warn": 0.50,
        "hit_rate_crit": 0.20,
        # Mean shadow divergence score above this is suspicious
        # (0 = identical, 1 = completely different vocab)
        "divergence_warn": 0.25,
        "divergence_crit": 0.50,
        # Invalidations per 100 requests
        "invalidation_rate_warn": 5.0,
        "invalidation_rate_crit": 15.0,
        # Cache-hit p95 latency above this (seconds) suggests cache is helping less
        "hit_latency_p95_warn": 5.0,
        # Evictions per minute
        "eviction_rate_warn": 10.0,
    }

    def __init__(
        self,
        shadow_rate: float = 0.02,
        alert_callback: Optional[Callable[[Alert], None]] = None,
        thresholds: Optional[dict] = None,
    ):
        self.shadow_rate = shadow_rate
        self.alert_callback = alert_callback or self._default_alert
        self.thresholds = {**self._DEFAULT_THRESHOLDS, **(thresholds or {})}

        self._agents: dict[str, AgentMetrics] = defaultdict(
            lambda: AgentMetrics(agent_id="unknown")
        )
        # Eviction events: timestamp list (rolling 60s window)
        self._eviction_times: deque = deque(maxlen=1000)
        # Global invalidation events
        self._invalidation_log: deque = deque(maxlen=500)
        # Fired alerts (dedup window)
        self._recent_alerts: dict[str, float] = {}
        self._alert_cooldown_s = 300  # re-fire same alert at most every 5 min

    # ------------------------------------------------------------------
    # Recording API (call from inference_worker)
    # ------------------------------------------------------------------

    def record(
        self,
        agent_id: str,
        cache_hit: bool,
        latency_s: float,
        completion_tokens: int,
        warm_output: Optional[str] = None,
        cold_output: Optional[str] = None,
    ) -> None:
        """Record a completed inference request."""
        m = self._get_agent(agent_id)
        if cache_hit:
            m.hits += 1
            m.hit_latencies.append(latency_s)
        else:
            m.misses += 1
            m.miss_latencies.append(latency_s)
        m.total_tokens += completion_tokens
        m.last_seen = time.monotonic()

        # Divergence scoring from shadow comparison
        if warm_output is not None and cold_output is not None:
            score = _jaccard_token_overlap(warm_output, cold_output)
            m.divergence_scores.append(score)
            if score > self.thresholds["divergence_warn"]:
                log.warning(
                    "Shadow divergence for agent %s: %.2f (warm vs cold outputs differ)",
                    agent_id, score,
                )

    def record_invalidation(self, agent_id: str, reason: str) -> None:
        """Record a cache invalidation event."""
        m = self._get_agent(agent_id)
        m.invalidations += 1
        m.invalidation_reasons[reason] += 1
        self._invalidation_log.append({
            "agent_id": agent_id,
            "reason": reason,
            "ts": time.time(),
        })
        log.info("Cache invalidated for %s reason=%s", agent_id, reason)

    def record_eviction(self, agent_id: str) -> None:
        """Record a RAM→disk eviction (spill)."""
        self._eviction_times.append(time.monotonic())

    def should_shadow_check(self) -> bool:
        """Returns True with probability shadow_rate."""
        return random.random() < self.shadow_rate

    # ------------------------------------------------------------------
    # Threshold checking (call periodically or from /stats)
    # ------------------------------------------------------------------

    def check_thresholds(self) -> list[Alert]:
        alerts = []
        now = time.monotonic()

        for agent_id, m in self._agents.items():
            if m.request_count < 20:
                continue  # not enough data

            # Hit rate
            hr = m.hit_rate
            if hr < self.thresholds["hit_rate_crit"]:
                alerts.append(Alert(
                    level="critical", category="hit_rate", agent_id=agent_id,
                    message=f"Cache hit rate critically low for {agent_id}: {hr:.1%}",
                    value=hr, threshold=self.thresholds["hit_rate_crit"],
                ))
            elif hr < self.thresholds["hit_rate_warn"]:
                alerts.append(Alert(
                    level="warning", category="hit_rate", agent_id=agent_id,
                    message=f"Cache hit rate low for {agent_id}: {hr:.1%}",
                    value=hr, threshold=self.thresholds["hit_rate_warn"],
                ))

            # Divergence
            div = m.mean_divergence()
            if div is not None:
                if div > self.thresholds["divergence_crit"]:
                    alerts.append(Alert(
                        level="critical", category="divergence", agent_id=agent_id,
                        message=f"High output divergence for {agent_id}: {div:.2f} — possible cache corruption",
                        value=div, threshold=self.thresholds["divergence_crit"],
                    ))
                elif div > self.thresholds["divergence_warn"]:
                    alerts.append(Alert(
                        level="warning", category="divergence", agent_id=agent_id,
                        message=f"Elevated output divergence for {agent_id}: {div:.2f}",
                        value=div, threshold=self.thresholds["divergence_warn"],
                    ))

            # Invalidation rate
            inval_rate = (m.invalidations / m.request_count) * 100
            if inval_rate > self.thresholds["invalidation_rate_crit"]:
                alerts.append(Alert(
                    level="critical", category="invalidation_rate", agent_id=agent_id,
                    message=f"High invalidation rate for {agent_id}: {inval_rate:.1f}/100 requests",
                    value=inval_rate, threshold=self.thresholds["invalidation_rate_crit"],
                ))

            # Hit latency p95 regression
            p95 = m.latency_percentile(95, hit=True)
            if p95 is not None and p95 > self.thresholds["hit_latency_p95_warn"]:
                alerts.append(Alert(
                    level="warning", category="latency", agent_id=agent_id,
                    message=f"Cache-hit p95 latency high for {agent_id}: {p95:.1f}s",
                    value=p95, threshold=self.thresholds["hit_latency_p95_warn"],
                ))

        # Eviction rate (global, last 60s)
        cutoff = now - 60
        recent_evictions = sum(1 for t in self._eviction_times if t > cutoff)
        if recent_evictions > self.thresholds["eviction_rate_warn"]:
            alerts.append(Alert(
                level="warning", category="eviction", agent_id=None,
                message=f"High eviction rate: {recent_evictions} spills/min — consider increasing max_ram_slots",
                value=float(recent_evictions), threshold=self.thresholds["eviction_rate_warn"],
            ))

        # Fire callbacks with dedup
        for alert in alerts:
            key = f"{alert.category}:{alert.agent_id}"
            last_fired = self._recent_alerts.get(key, 0)
            if now - last_fired > self._alert_cooldown_s:
                self.alert_callback(alert)
                self._recent_alerts[key] = now

        return alerts

    # ------------------------------------------------------------------
    # Snapshot for /stats endpoint
    # ------------------------------------------------------------------

    def snapshot(self) -> dict:
        now = time.monotonic()
        cutoff = now - 60
        recent_evictions = sum(1 for t in self._eviction_times if t > cutoff)

        agents_out = {}
        for agent_id, m in self._agents.items():
            div = m.mean_divergence()
            agents_out[agent_id] = {
                "requests": m.request_count,
                "hit_rate": round(m.hit_rate, 3),
                "hits": m.hits,
                "misses": m.misses,
                "invalidations": m.invalidations,
                "invalidation_reasons": dict(m.invalidation_reasons),
                "latency_p50_hit_s":  m.latency_percentile(50, hit=True),
                "latency_p95_hit_s":  m.latency_percentile(95, hit=True),
                "latency_p50_miss_s": m.latency_percentile(50, hit=False),
                "latency_p95_miss_s": m.latency_percentile(95, hit=False),
                "mean_divergence": round(div, 3) if div is not None else None,
                "shadow_checks": len(m.divergence_scores),
                "total_tokens": m.total_tokens,
            }

        alerts = self.check_thresholds()

        return {
            "agents": agents_out,
            "global": {
                "evictions_last_60s": recent_evictions,
                "recent_invalidations": list(self._invalidation_log)[-10:],
            },
            "active_alerts": [
                {
                    "level": a.level,
                    "category": a.category,
                    "agent_id": a.agent_id,
                    "message": a.message,
                }
                for a in alerts
            ],
        }

    # ------------------------------------------------------------------
    # Shape validation helper (call in CacheRegistry._load_from_disk)
    # ------------------------------------------------------------------

    @staticmethod
    def validate_cache_shapes(
        loaded_cache: list,
        expected_cache: list,
        agent_id: str,
    ) -> tuple[bool, Optional[str]]:
        """
        Compare loaded cache layer shapes against a freshly-made empty cache.
        Returns (valid: bool, error_message: str | None).

        Usage:
            empty = make_prompt_cache(model)
            ok, err = CacheHealthMonitor.validate_cache_shapes(loaded, empty, agent_id)
            if not ok:
                monitor.record_invalidation(agent_id, reason="shape_mismatch")
                return None  # force cold start
        """
        if len(loaded_cache) != len(expected_cache):
            return False, (
                f"Layer count mismatch: loaded {len(loaded_cache)} "
                f"vs expected {len(expected_cache)}"
            )
        for i, (l, e) in enumerate(zip(loaded_cache, expected_cache)):
            import mlx.core as mx
            l_arr = l if isinstance(l, mx.array) else None
            e_arr = e if isinstance(e, mx.array) else None
            if l_arr is not None and e_arr is not None:
                if l_arr.shape[1:] != e_arr.shape[1:]:   # ignore batch/seq dim
                    return False, (
                        f"Layer {i} shape mismatch: "
                        f"loaded {l_arr.shape} vs expected {e_arr.shape}"
                    )
        return True, None

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get_agent(self, agent_id: str) -> AgentMetrics:
        if agent_id not in self._agents:
            self._agents[agent_id] = AgentMetrics(agent_id=agent_id)
        return self._agents[agent_id]

    @staticmethod
    def _default_alert(alert: Alert) -> None:
        lvl = logging.CRITICAL if alert.level == "critical" else logging.WARNING
        log.log(lvl, "[ALERT %s] %s (value=%.3f threshold=%.3f)",
                alert.category, alert.message, alert.value, alert.threshold)
