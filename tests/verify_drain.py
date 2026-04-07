import requests
import threading
import time
import sys

def verify_drain():
    status_url = "http://127.0.0.1:8000/status"
    completion_url = "http://127.0.0.1:8000/v1/chat/completions"
    maintenance_url = "http://127.0.0.1:8000/system/maintenance"
    
    headers = {
        "Content-Type": "application/json",
        "X-Agent-Name": "verify-drain-script",
        "X-EHC-Admin-Token": "test-admin-token" # We'll try to find this in .env
    }
    
    # Try to get the token from .env
    try:
        with open(".env", "r") as f:
            for line in f:
                if "EHC_ADMIN_TOKEN" in line:
                    headers["X-EHC-Admin-Token"] = line.split("=")[1].strip().strip('"')
    except:
        pass

    print(f"Verifying Maintenance Drain on {completion_url}...")

    # 1. Start a slow completion request in a background thread
    # Use max_tokens=100 and prompt "Say 'Hello' then wait then 'World'" to simulate load.
    # Actually just a normal prompt will be slow enough.
    data = {
        "messages": [{"role": "user", "content": "Count from 1 to 5 slowly, adding some poetic fluff."}],
        "max_tokens": 100,
        "stream": False
    }

    completion_success = False
    completion_done = False

    def slow_request():
        nonlocal completion_success, completion_done
        print(f"Thread 1: Starting slow request...")
        try:
            r = requests.post(completion_url, headers=headers, json=data, timeout=15)
            r.raise_for_status()
            completion_success = True
            print(f"Thread 1: Completion successful!")
        except Exception as e:
                print(f"Thread 1: Completion failed as expected if killed, but we want success: {e}")
        completion_done = True

    t1 = threading.Thread(target=slow_request)
    t1.start()
    
    # 2. Wait for it to be "in-flight" (approx 200ms)
    time.sleep(0.5)
    
    # 3. Enter maintenance mode
    print(f"Thread 2: Entering maintenance mode...")
    start_maintenance = time.time()
    try:
        m_r = requests.post(maintenance_url, headers=headers, timeout=10)
        m_r.raise_for_status()
        end_maintenance = time.time()
        print(f"Thread 2: Maintenance mode active in {end_maintenance - start_maintenance:.3f}s")
    except Exception as e:
        print(f"Thread 2: Maintenance request failed: {e}")
        sys.exit(1)

    # 4. Check if the completion finished BEFORE maintenance was granted
    # Actually, EHC blocks on maintenance until inFlightCount == 0.
    # So if maintenance returns SUCCESS, the completion thread must have finished or be near finishing.
    
    t1.join()
    
    # Ensure we release maintenance mode
    print("Releasing maintenance mode...")
    requests.post(f"{maintenance_url}/release", headers=headers)

    if completion_success:
        print("SUCCESS: Completion was not interrupted by maintenance mode entry.")
    else:
        print("FAILURE: Completion failed when maintenance mode was entered.")
        sys.exit(1)

if __name__ == "__main__":
    verify_drain()
