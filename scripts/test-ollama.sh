#!/bin/bash
# Ollama Test Suite
# =================
#
# Regression tests for Ollama installation.
# Run after any update or configuration change.
#
# Usage: ./test-ollama.sh
#
# Exit codes:
#   0 = All tests passed
#   1 = One or more tests failed

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$SCRIPT_DIR/var"
RESULTS_FILE="$LOG_DIR/test-results.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Initialize
mkdir -p "$LOG_DIR"
echo "Ollama Test Suite - $(date)" > "$RESULTS_FILE"
echo "==============================" >> "$RESULTS_FILE"

# Test function
run_test() {
    local name="$1"
    local cmd="$2"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Testing: $name... "
    echo "" >> "$RESULTS_FILE"
    echo "TEST: $name" >> "$RESULTS_FILE"
    
    if eval "$cmd" >> "$RESULTS_FILE" 2>&1; then
        echo -e "${GREEN}PASS${NC}"
        echo "RESULT: PASS" >> "$RESULTS_FILE"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}FAIL${NC}"
        echo "RESULT: FAIL" >> "$RESULTS_FILE"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# =============================================================================
# TESTS
# =============================================================================

echo ""
echo "🧪 Ollama Test Suite"
echo "===================="
echo ""

# Test 1: Binary exists
run_test "Binary exists" "which ollama"

# Test 2: Version check
run_test "Version check" "ollama --version"

# Test 3: Server responding
run_test "Server responding (port 11434)" "curl -s http://localhost:11434 | grep -q 'Ollama is running'"

# Test 4: API version endpoint
run_test "API version endpoint" "curl -s http://localhost:11434/api/version | grep -q 'version'"

# Test 5: Model list accessible (may be empty)
run_test "Model list accessible" "ollama list 2>&1 | head -1"

# Test 6: Metal GPU check - inference test
# This is the critical test that failed with the source build
echo -n "Testing: Metal GPU inference... "
echo "" >> "$RESULTS_FILE"
echo "TEST: Metal GPU inference" >> "$RESULTS_FILE"
TESTS_RUN=$((TESTS_RUN + 1))

# Check if llama3.1 is available
if ollama list 2>&1 | grep -q "llama3.1"; then
    # Try a simple inference
    if echo "Say hello" | timeout 30 ollama run llama3.1 --nowordwrap 2>&1 | head -5 >> "$RESULTS_FILE"; then
        echo -e "${GREEN}PASS${NC}"
        echo "RESULT: PASS" >> "$RESULTS_FILE"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC}"
        echo "RESULT: FAIL (inference error - check Metal GPU)" >> "$RESULTS_FILE"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
else
    echo -e "${YELLOW}SKIP${NC} (llama3.1 not installed)"
    echo "RESULT: SKIP (model not available)" >> "$RESULTS_FILE"
fi

# =============================================================================
# SUMMARY
# =============================================================================

echo ""
echo "===================="
echo "Results: $TESTS_PASSED/$TESTS_RUN passed"
echo "===================="

echo "" >> "$RESULTS_FILE"
echo "==================" >> "$RESULTS_FILE"
echo "SUMMARY: $TESTS_PASSED/$TESTS_RUN passed, $TESTS_FAILED failed" >> "$RESULTS_FILE"
echo "==================" >> "$RESULTS_FILE"

if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "${RED}Some tests failed!${NC}"
    echo "See $RESULTS_FILE for details"
    exit 1
else
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
fi
