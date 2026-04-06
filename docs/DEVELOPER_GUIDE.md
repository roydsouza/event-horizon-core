# Event Horizon Core: Developer Guide

This guide describes the architecture and maintenance of the **Event Horizon Core** Go Substrate.

## 🏗️ Architecture

Event Horizon Core consists of a high-performance **Go Daemon** that supervises local inference engines and a **Python Thin Client** for CLI interaction.

### 1. Go Substrate (The Daemon)
Located in `internal/`, the Go substrate is responsible for:
- **Process Management** (`internal/supervisor`): Dynamically launches, monitors, and hot-swaps `mlx_lm.server` instances.
- **Anti-Zombie Mutex**: Uses Process Groups (`syscall.Setpgid`) to bind child processes to the daemon. If the daemon is killed, the entire process tree (including MLX) is instantly reaped by the OS.
- **HTTP Proxy** (`internal/server`): An OpenAI-compatible REST server (Port 8000) that implements blocking hot-swap middleware.

### 2. Python Thin Client
Located in `event_horizon_core/`, the Python package provides the `event-horizon` CLI. It contains zero inference logic and acts purely as a proxy to the Go Daemon.

## 🛠️ Development Workflow

### Building the Daemon
The daemon should be compiled with Go 1.22+:
```bash
go build -o event-horizon ./cmd/event-horizon
```

### Running in Development
To run the daemon manually for debugging:
```bash
./event-horizon start --port 8000
```

## 🔄 Hot-Swap Implementation Details

When a client requests a model (`req.Model`) that is not currently active, the `internal/server/handler.go` middleware:
1.  Intercepts the request.
2.  Calls `supervisor.SwitchModel(ctx, modelName)`.
3.  The supervisor kills the active MLX server and launches a new one.
4.  The server polls the MLX health port until ready.
5.  The original HTTP request is released and forwarded to the new local backend.

## 🧪 Testing

### Go Internal Tests
Run standard Go tests for supervisor and server logic:
```bash
go test ./internal/...
```

### Stress Testing (Python)
Use the Python suite to simulate concurrent agent load:
```bash
uv run pytest tests/test_torture.py
```

## 🔐 Security & Hardened Attack Surface
By moving to a "Local Only" architecture, we have eliminated external API dependencies and orphaned provider code. The daemon now only listens on `127.0.0.1`, ensuring that inference remains strictly isolated to the host M5 hardware.
