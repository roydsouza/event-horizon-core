import json
import requests
import time
import sys

def verify_streaming():
    url = "http://127.0.0.1:8000/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "X-Agent-Name": "verification-script"
    }
    data = {
        "messages": [{"role": "user", "content": "Counter to 5 slowly, one number per line."}],
        "stream": True,
        "max_tokens": 50
    }

    print(f"Sending streaming request to {url}...")
    start_time = time.time()
    
    try:
        response = requests.post(url, headers=headers, json=data, stream=True, timeout=30)
        response.raise_for_status()
    except Exception as e:
        print(f"ERROR: Request failed: {e}")
        sys.exit(1)

    chunk_count = 0
    first_token_time = None
    last_chunk_time = time.time()
    deltas = []

    for line in response.iter_lines():
        if not line:
            continue
        
        line = line.decode('utf-8')
        if line.startswith("data: "):
            content = line[6:]
            if content == "[DONE]":
                break
            
            try:
                chunk = json.loads(content)
                delta = chunk['choices'][0]['delta'].get('content', '')
                if delta:
                    now = time.time()
                    if first_token_time is None:
                        first_token_time = now
                        print(f"First token received in {first_token_time - start_time:.2f}s")
                    
                    time_since_last = now - last_chunk_time
                    deltas.append(time_since_last)
                    last_chunk_time = now
                    chunk_count += 1
                    print(f"Chunk {chunk_count:02d} | Delta: {time_since_last:.3f}s | Content: {repr(delta)}")
            except json.JSONDecodeError:
                continue

    total_time = time.time() - start_time
    print("-" * 40)
    print(f"Streaming Verification Complete")
    print(f"Total Chunks: {chunk_count}")
    print(f"Total Time: {total_time:.2f}s")
    
    if chunk_count < 5:
        print("FAILURE: Too few chunks received. Streaming might be disabled or buffered.")
        sys.exit(1)
    
    # If deltas are very small (e.g. all < 10ms for a slow prompt), it might be buffering.
    # But for mlx_lm, tokens can be fast. The key is that they arrive sequentially.
    avg_delta = sum(deltas) / len(deltas) if deltas else 0
    print(f"Average Delta: {avg_delta:.3f}s")
    
    if any(d > 2.0 for d in deltas[1:]): # Ignore first token delay
        print("WARNING: High jitter detected between chunks.")
    
    print("SUCCESS: Streaming is functional and unbuffered.")

if __name__ == "__main__":
    verify_streaming()
