package providers

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strings"
	"time"
)

var (
	// OpenRouter Model Aliases for cleaner client requests
	Aliases = map[string]string{
		"best":     "anthropic/claude-3.5-sonnet",
		"fast":     "google/gemini-2.0-flash-001",
		"free":     "google/gemini-2.0-flash-exp:free",
		"cheap":    "meta-llama/llama-3.3-70b-instruct",
		"reasoner": "openai/o1-preview",
	}
)

type OpenRouterClient struct {
	APIKey  string
	BaseURL string
	HTTP    *http.Client
}

func NewOpenRouterClient() *OpenRouterClient {
	return &OpenRouterClient{
		APIKey:  os.Getenv("OPENROUTER_API_KEY"),
		BaseURL: "https://openrouter.ai/api/v1",
		HTTP:    &http.Client{Timeout: 120 * time.Second},
	}
}

func (c *OpenRouterClient) ResolveModel(model string) string {
	if actual, ok := Aliases[strings.ToLower(model)]; ok {
		return actual
	}
	return model
}

func (c *OpenRouterClient) ProxyRequest(ctx context.Context, body []byte) (io.ReadCloser, http.Header, int, error) {
	if c.APIKey == "" {
		return nil, nil, 0, fmt.Errorf("OPENROUTER_API_KEY not set")
	}

	// First, let's check if the model in the body needs resolving (aliasing)
	var reqMap map[string]interface{}
	if err := json.Unmarshal(body, &reqMap); err == nil {
		if model, ok := reqMap["model"].(string); ok {
			resolved := c.ResolveModel(model)
			if resolved != model {
				log.Printf("[OpenRouter] Resolving alias: %s -> %s", model, resolved)
				reqMap["model"] = resolved
				body, _ = json.Marshal(reqMap)
			}
		}
	}

	url := fmt.Sprintf("%s/chat/completions", c.BaseURL)
	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(body))
	if err != nil {
		return nil, nil, 0, err
	}

	req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", c.APIKey))
	req.Header.Set("HTTP-Referer", "https://github.com/roydsouza/event-horizon-core")
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.HTTP.Do(req)
	if err != nil {
		return nil, nil, 0, err
	}

	return resp.Body, resp.Header, resp.StatusCode, nil
}
