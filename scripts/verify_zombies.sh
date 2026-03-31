#!/bin/bash

# Configuration
DAEMON_BINARY="./event-horizon"
TARGET_PORT=8000
MLX_PORT=8080

echo "[*] Phase 8: Zombie Verification Start"

# 1. Kill any existing instances
pkill -9 event-horizon 2>/dev/null
pkill -9 -f mlx_lm.server 2>/dev/null

# 2. Boot the daemon in the background
echo "[*] Booting Go Daemon..."
$DAEMON_BINARY > zombie_test.log 2>&1 &
DAEMON_PID=$!
sleep 5

# 3. Verify MLX is running
MLX_PID=$(pgrep -f mlx_lm.server)
if [ -n "$MLX_PID" ]; then
    echo "[+] MLX Server correctly spawned (PID: $MLX_PID)"
else
    echo "[-] ERROR: MLX Server failed to spawn."
    exit 1
fi

# 4. KILL THE DAEMON (Sigkill - Simulation of a crash)
echo "[*] CRASHING Go Daemon (kill -9)..."
kill -9 $DAEMON_PID

# 5. Check if MLX is still alive
sleep 2
ZOMBIE_PID=$(pgrep -f mlx_lm.server)

if [ -n "$ZOMBIE_PID" ]; then
    echo "[-] FAILURE: MLX Server is still running (PID: $ZOMBIE_PID). Leak confirmed."
    pkill -9 -f mlx_lm.server
    exit 1
else
    echo "[+] SUCCESS: MLX Server was reaped by the kernel. Zero VRAM leaks."
fi

echo "[*] Phase 8: Zombie Verification Complete."
