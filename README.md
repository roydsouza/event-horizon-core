# Event Horizon Core

Unified Local LLM Inference Bridge for Apple Silicon. 
Designed for high-performance, private, and local-first AI experimentation.

## Features
- **MLX Provider**: Direct, low-latency inference on Apple Silicon (M5 optimized) using Metal.
- **Llama.cpp Provider**: High-performance GGUF support via native `llama-server`.
- **Ollama Provider (Legacy)**: Standard Ollama API support for existing workflows.
- **OpenRouter Provider**: Remote fallback for high-reasoning tasks (Gemini 2.0, Claude 3.5).
- **Unified CLI**: Single tool to manage and query all local and remote models.
- **Performance Logging**: Real-world tok/s and latency tracking for every request.

## Installation & Setup

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install Inference Engines**:
   ```bash
   # Native MLX
   uv pip install mlx-lm
   
   # Native Llama.cpp (Homebrew recommended)
   brew install llama.cpp
   ```

3. **Sync the environment**:
   ```bash
   uv sync
   ```

4. **Configure Environment Variables**:
   Copy `.env.template` to `.env` and add your `OPENROUTER_API_KEY`.

## CLI Usage

All commands should be prefixed with `uv run` to use the managed environment:

```bash
# View the detailed help page and command list
uv run event-horizon help 

# Check status of all providers (Local & Remote)
uv run event-horizon status

# List models available on specific local/remote backends
uv run event-horizon mlx
uv run event-horizon llamacpp
uv run event-horizon openrouter

# Generate text using MLX (Fastest on Mac - Tier 1)
uv run event-horizon generate mlx "Explain quantum computing."

# Generate text using Llama.cpp (Native Fallback - Tier 2)
# Ensure llama-server is running on port 8081
uv run event-horizon generate llamacpp "What is the event horizon?" 

# Generate text using OpenRouter (Remote Fallback - Tier 3)
uv run event-horizon generate openrouter "Complex reasoning..." --model best
```

## 🛠️ Performance & Concurrency

### Hardware Boundaries (M5 24GB Unified Memory)
Event Horizon Core is optimized for **Apple Silicon M5 (24GB RAM)**. 
- **VRAM Guard**: `MLXProvider` will now calculate estimated VRAM before loading. If a model (e.g. 70B variant) exceeds **22GB**, the load will be aborted to prevent OS instability.
- **Unified Memory**: Local models share the 24GB pool with your OS and applications. For large models (14B+), close high-memory apps (Chrome, IDEs) for optimal performance.

### Concurrency 
- **MLX/Llama.cpp**: Shared local GPU resources are managed by the Core Orchestrator. 
- **Roadmap**: A unified cross-provider locking/queue system is implemented in Phase 4.

## 🏗️ Architecture: Multi-Agent Orchestration

Event Horizon Core acts as a **Unified Traffic Controller** for all your agents on Apple Silicon.

### The Intended Inference Hierarchy
To optimize for the **Apple Silicon M5 (24GB)**, the core follows this priority logic:

1.  **Tier 1: MLX (Primary / Native)**: Metal-optimized direct inference. Fastest tok/s and lowest latency.
    - *Default Port*: 8080 (`mlx_lm.server`)
2.  **Tier 2: Llama.cpp (Native Fallback)**: Fastest GGUF execution. Used if MLX is locked.
    - *Default Port*: 8081 (`llama-server`)
3.  **Tier 3: OpenRouter (Remote Fallback)**: Used for high-reasoning tasks (best/reasoner) or saturated local resources.
4.  **Tier 4: Ollama (Legacy)**: Maintained for backward compatibility.

### Running the Backends
For full orchestration, start both native servers in separate terminals:
```bash
# Terminal 1: MLX
uv run mlx_lm.server --model mlx-community/Llama-3.2-3B-Instruct-4bit --port 8080

# Terminal 2: Llama.cpp
llama-server -m ~/path/to/model.gguf --port 8081
```

### Fetching GGUF Models for Llama.cpp
To use `llama-server`, you must provide it with a local model in the `.gguf` format. You can download one easily using the `huggingface-cli`:

```bash
# 1. Install huggingface-cli (if needed)
uv pip install -U "huggingface_hub[cli]"

# 2. Download a high-performance quantized model (e.g. Q4_K_M)
huggingface-cli download \
  bartowski/Meta-Llama-3.1-8B-Instruct-GGUF \
  --include "*Q4_K_M.gguf" \
  --local-dir ~/models

# 3. Boot the Llama.cpp server on Port 8081
llama-server -m ~/models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf --port 8081
```

### Integration Patterns:
- **CLI Wrapper**: For simple scripts (`uv run event-horizon generate mlx`).
- **Python Library**: Direct import for Python agents (`from event_horizon_core import LLMFactory`).
- **OpenAI-Compatible Server**: (Phase 6 Roadmap) Unified local endpoint.

## 🤖 Agent Integration (Clients)

The following agentic frameworks can be hooked into Event Horizon Core:

| Client | Interface | Setup Guide |
| :--- | :--- | :--- |
| **OpenCode** | CLI / Config | [Guide](docs/clients/OPENCODE_SETUP.md) |
| **Tachyon Tongs** | Python Stub | [Stubbing Info](README.md#stubbing) |
| **OpenClaw** | Backend | [Guide](docs/clients/OPENCLAW_SETUP.md) |
| **ZeroClaw** | Backend | [Guide](docs/clients/ZEROCLAW_SETUP.md) |
| **OpenFang** | Backend | [Guide](docs/clients/OPENFANG_SETUP.md) |
| **Hermes** | Backend | [Guide](docs/clients/HERMES_AGENT_SETUP.md) |

## 🧩 Anthropic Integration

To use this core in your `~/anthropic` projects, follow the [Anthropic Setup Guide](docs/ANTHROPIC_SETUP.md).

## Documentation
- [Anthropic Setup](docs/ANTHROPIC_SETUP.md)
- [Developer Guide](docs/DEVELOPER_GUIDE.md)
