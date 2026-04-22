package supervisor

import (
	"fmt"
	"os"
)

// Engine defines the interface for an inference backend.
type Engine interface {
	ID() string
	GetArgs(modelPath string, port int) []string
	Executable() string
}

// MLXEngine is the default engine using mlx_lm.server via uv.
type MLXEngine struct{}

func (e *MLXEngine) ID() string { return "mlx-lm" }
func (e *MLXEngine) Executable() string { return "uv" }
func (e *MLXEngine) GetArgs(modelPath string, port int) []string {
	args := []string{"run", "mlx_lm.server",
		"--model", modelPath,
		"--port", fmt.Sprintf("%d", port),
		"--prompt-cache-size", "512",
		"--prompt-concurrency", "4",
		"--decode-concurrency", "4",
	}

	if draft := os.Getenv("MLX_DRAFT_MODEL"); draft != "" {
		args = append(args, "--draft-model", draft)
	}
	return args
}

// BodegaEngine is the high-performance agentic engine.
type BodegaEngine struct{}

func (e *BodegaEngine) ID() string { return "bodega" }
func (e *BodegaEngine) Executable() string { return "bodega" }
func (e *BodegaEngine) GetArgs(modelPath string, port int) []string {
	// Logic based on preliminary Bodega CLI research
	return []string{"server",
		"--model", modelPath,
		"--port", fmt.Sprintf("%d", port),
		"--continuous-batching",
		"--speculative-decoding",
	}
}

// VLLMEngine is the throughput-optimized engine.
type VLLMEngine struct{}

func (e *VLLMEngine) ID() string { return "vllm" }
func (e *VLLMEngine) Executable() string { return "python3" }
func (e *VLLMEngine) GetArgs(modelPath string, port int) []string {
	return []string{"-m", "vllm.entrypoints.openai.api_server",
		"--model", modelPath,
		"--port", fmt.Sprintf("%d", port),
		"--gpu-memory-utilization", "0.9",
		"--max-model-len", "8192",
	}
}

// GetEngine returns the engine implementation by name.
func GetEngine(name string) (Engine, error) {
	switch name {
	case "mlx-lm", "":
		return &MLXEngine{}, nil
	case "bodega":
		return &BodegaEngine{}, nil
	case "vllm":
		return &VLLMEngine{}, nil
	default:
		return nil, fmt.Errorf("unknown engine: %s", name)
	}
}
