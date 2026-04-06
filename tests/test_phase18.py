import time
import requests
import json
import os

BASE_URL = "http://127.0.0.1:8000"
ADMIN_TOKEN = os.environ.get("EHC_ADMIN_TOKEN", "test-token")
HEADERS = {"X-EHC-Admin-Token": ADMIN_TOKEN, "Content-Type": "application/json"}

def test_metrics():
    print("Testing /metrics...")
    resp = requests.get(f"{BASE_URL}/metrics", headers=HEADERS)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    assert "active_mb" in data
    assert "peak_mb" in data
    print(f"Metrics: {data}")

def test_maintenance_lifecycle():
    print("Testing /system/maintenance...")
    resp = requests.post(
        f"{BASE_URL}/system/maintenance",
        headers=HEADERS,
        json={"reason": "integration test", "requested_by": "test_phase18"}
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code} - {resp.text}"
    status_data = resp.json()
    assert status_data["status"] == "maintenance"

    print("Testing 503 on completions while in maintenance...")
    resp_chat = requests.post(f"{BASE_URL}/v1/chat/completions", headers=HEADERS, json={"model": "default"})
    assert resp_chat.status_code == 503, f"Expected 503, got {resp_chat.status_code}"

    print("Testing /system/maintenance/status...")
    resp_status = requests.get(f"{BASE_URL}/system/maintenance/status", headers=HEADERS)
    data = resp_status.json()
    assert data["in_maintenance"] is True

    print("Testing /v1/model/swap inside maintenance...")
    resp_swap = requests.post(f"{BASE_URL}/v1/model/swap", headers=HEADERS, json={"model": "mlx-community/Llama-3.2-1B-Instruct-4bit"})
    assert resp_swap.status_code == 200, f"Expected 200, got {resp_swap.status_code} - {resp_swap.text}"

    print("Testing /system/maintenance/release...")
    resp_release = requests.post(f"{BASE_URL}/system/maintenance/release", headers=HEADERS, json={})
    assert resp_release.status_code == 200, f"Expected 200, got {resp_release.status_code} - {resp_release.text}"

    print("Testing completions recovery...")
    # NOTE: Since no underlying model might be reachable if MLX server isn't running properly 
    # for the test, we just expect it NOT to be 503. Usually 200 or 503 from backend proxy.
    resp_chat_2 = requests.post(f"{BASE_URL}/v1/chat/completions", headers=HEADERS, json={"model": "default"})
    assert resp_chat_2.status_code != 503, "Should not return 503 Maintenance Mode anymore"

    print("All Phase 18 Integration Tests Complete.")

if __name__ == "__main__":
    test_metrics()
    test_maintenance_lifecycle()
