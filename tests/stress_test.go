package tests

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"sync"
	"testing"
	"time"
)

const baseURL = "http://localhost:8000"

func TestHighConcurrency(t *testing.T) {
	const numRequests = 5
	var wg sync.WaitGroup
	wg.Add(numRequests)

	payload := map[string]interface{}{
		"model": "mlx-community/Llama-3.2-3B-Instruct-4bit",
		"messages": []map[string]string{
			{"role": "user", "content": "Say 'Concurrency Test'"},
		},
		"max_tokens": 5,
	}
	body, _ := json.Marshal(payload)

	startTime := time.Now()

	for i := 0; i < numRequests; i++ {
		go func(id int) {
			defer wg.Done()
			
			resp, err := http.Post(baseURL+"/v1/chat/completions", "application/json", bytes.NewBuffer(body))
			if err != nil {
				t.Errorf("Request %d failed: %v", id, err)
				return
			}
			defer resp.Body.Close()

			if resp.StatusCode != http.StatusOK {
				respBody, _ := io.ReadAll(resp.Body)
				t.Errorf("Request %d returned status %d: %s", id, resp.StatusCode, string(respBody))
				return
			}
			fmt.Printf("[+] Request %d completed successfully\n", id)
		}(i)
	}

	wg.Wait()
	duration := time.Since(startTime)
	fmt.Printf("[*] Completed %d concurrent requests in %v\n", numRequests, duration)
}

func TestHotSwapRace(t *testing.T) {
	// Tests switching between two models rapidly
	models := []string{
		"mlx-community/Llama-3.2-3B-Instruct-4bit",
		"mlx-community/Llama-3.2-1B-Instruct-4bit",
	}

	for _, model := range models {
		fmt.Printf("[*] Testing swap to model: %s\n", model)
		payload := map[string]interface{}{
			"model": model,
			"messages": []map[string]string{
				{"role": "user", "content": "Confirm model."},
			},
			"max_tokens": 5,
		}
		body, _ := json.Marshal(payload)

		startTime := time.Now()
		resp, err := http.Post(baseURL+"/v1/chat/completions", "application/json", bytes.NewBuffer(body))
		if err != nil {
			t.Fatalf("Swap to %s failed: %v", model, err)
		}
		defer resp.Body.Close()
		
		fmt.Printf("[+] Swap to %s completed in %v\n", model, time.Since(startTime))
		if resp.StatusCode != http.StatusOK {
			t.Errorf("Swap to %s returned status %d", model, resp.StatusCode)
		}
	}
}

func TestOpenRouterFallback(t *testing.T) {
	fmt.Println("[*] Testing OpenRouter Fallback (Model: free)...")
	payload := map[string]interface{}{
		"model": "free",
		"messages": []map[string]string{
			{"role": "user", "content": "Confirm you are Gemini Flash via OpenRouter."},
		},
		"max_tokens": 10,
	}
	body, _ := json.Marshal(payload)

	startTime := time.Now()
	resp, err := http.Post(baseURL+"/v1/chat/completions", "application/json", bytes.NewBuffer(body))
	if err != nil {
		t.Fatalf("OpenRouter fallback failed: %v", err)
	}
	defer resp.Body.Close()

	fmt.Printf("[+] OpenRouter response received in %v\n", time.Since(startTime))
	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		t.Errorf("OpenRouter returned status %d: %s", resp.StatusCode, string(respBody))
	}
}
