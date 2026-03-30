# Event Horizon Core

Unified Local LLM Inference Bridge for Apple Silicon. 
Designed for high-performance, private, and local-first AI experimentation.

## Features
- **MLX Provider**: Direct, low-latency inference on Apple Silicon (M1/M2/M3/M4) using Metal.
- **Ollama Provider**: Robust, multi-model support via the Ollama API/CLI.
- **Unified CLI**: Single tool to manage and query all local models.
- **Cross-Project Ready**: Designed to be shared between AntiGravity and Anthropic projects.

## Installation
From any Python environment:
```bash
pip install -e ~/antigravity/event-horizon-core
```

## CLI Usage
```bash
# Check status of all providers
event-horizon status

# Generate text using MLX (Fastest on Mac)
event-horizon generate mlx "Explain quantum computing."

# Generate text using Ollama
event-horizon generate ollama "What is the event horizon?" --model llama3.2
```

## 🛠️ Performance & Concurrency

### Hardware Boundaries (M5 24GB Unified Memory)
Event Horizon Core is optimized for **Apple Silicon M5 (24GB RAM)**. 
- **VRAM Guard**: `MLXProvider` will now calculate estimated VRAM before loading. If a model (e.g. 70B variant) exceeds **22GB**, the load will be aborted to prevent OS instability.
- **Unified Memory**: Local models share the 24GB pool with your OS and applications. For large models (14B+), close high-memory apps (Chrome, IDEs) for optimal performance.

### Concurrency 
- **Ollama**: Automatically handles request queueing. Subsequent calls will wait for the first to complete.
- **MLX**: Uses a single-process Metal lock. Multiple concurrent MLX calls might result in Resource Contention leading to failure. 
- **Roadmap**: A unified cross-provider locking/queue system is planned for Phase 3.

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
