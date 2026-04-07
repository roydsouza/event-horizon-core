import requests
import time
import sys
import subprocess

def verify_metrics_ttl():
    # We'll use the /status endpoint to get current admin token or just pass one if needed.
    # From sync_log, we know X-EHC-Admin-Token is required. 
    # Let's assume for local verification we can find it in .env or it might be 'dev-token' for now.
    # Looking at CLAUDE.md/SYNC_LOG - Claude added it.
    
    url = "http://127.0.0.1:8000/metrics"
    headers = {
        "X-EHC-Admin-Token": "test-admin-token" # We'll try common local test tokens
    }
    
    # Let's try to get the token from .env if possible
    try:
        with open(".env", "r") as f:
            for line in f:
                if "EHC_ADMIN_TOKEN" in line:
                    headers["X-EHC-Admin-Token"] = line.split("=")[1].strip().strip('"')
    except:
        pass

    print(f"Verifying Metrics TTL (5s) cache on {url}...")
    
    # 1. Fetch once to prime cache
    start = time.time()
    try:
        r1 = requests.get(url, headers=headers, timeout=5)
        r1.raise_for_status()
        t1 = time.time() - start
        print(f"Request 1 Content Length: {len(r1.text)} | Time: {t1:.3f}s (Likely cold)")
    except Exception as e:
        print(f"ERROR: Priming request failed (Check admin token): {e}")
        sys.exit(1)

    # 2. Fetch rapidly 5 times
    for i in range(5):
        start = time.time()
        r = requests.get(url, headers=headers, timeout=2)
        r.raise_for_status()
        t = time.time() - start
        print(f"Repeat {i+1} | Time: {t:.3f}s (Should be cached < 0.050s)")
        if t > 0.100:
            print(f"WARNING: Request {i+1} took longer than expected for a cache hit.")

    # 3. Wait for TTL to expire (5s)
    print("Waiting 6 seconds for TTL expiry...")
    time.sleep(6)
    
    # 4. Fetch again
    start = time.time()
    r_expired = requests.get(url, headers=headers, timeout=5)
    r_expired.raise_for_status()
    t_expired = time.time() - start
    print(f"Post-Expiry Request | Time: {t_expired:.3f}s (Should be cold/slower)")
    
    if t_expired > t * 2 or t_expired > 0.100:
        print("SUCCESS: Metrics TTL caching is working as expected.")
    else:
        print("WARNING: Metrics fetch is consistently fast. Either subprocess is fast or cache is not working.")

if __name__ == "__main__":
    verify_metrics_ttl()
