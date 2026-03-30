# Anthropic Integration: Event Horizon Core

This guide explains how to use the centralized `event-horizon-core` inference engine from within your `~/anthropic` projects.

## Prerequisites
- macOS on Apple Silicon (M1/M2/M3/M4)
- Python 3.10+
- Ollama (optional, for Ollama provider)

## Setup Instructions

### 1. Link the Core Package
In the terminal of your Anthropic project (and inside its virtual environment), run:

```bash
pip install -e ~/antigravity/event-horizon-core
```

This installs the core in "editable" mode, meaning any updates to the core are immediately available to your Anthropic project.

### 2. Basic Usage (Python)

```python
from event_horizon_core import LLMFactory

# Use MLX (Native Apple Silicon performance)
mlx = LLMFactory.get_provider("mlx", model_path="mlx-community/Llama-3.2-3B-Instruct-4bit")
response = mlx.generate("Explain quantum entanglement.")
print(response)

# Use Ollama
ollama = LLMFactory.get_provider("ollama", model="llama3.1")
response = ollama.generate("What is the event horizon?")
print(response)
```

### 3. CLI Usage
Once installed, the `event-horizon` command will be available in your path:

```bash
event-horizon status
event-horizon generate mlx "Hello from Anthropic"
```

## Maintenance
To add new providers or models, modify the code in `~/antigravity/event-horizon-core`. Changes are shared across all linked projects.
