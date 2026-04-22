"""
forge/gate.py — Event Horizon Core Forge Gate.

Mandatory checkpoint commands (run from project root):

  python3 forge/gate.py session-start        # Start of every session
  python3 forge/gate.py lock <task-id>       # When beginning a task
  python3 forge/gate.py pre-submit           # Before filing any briefing
  python3 forge/gate.py unlock               # After task receives CLEARED verdict
"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROJECT_NAME = "event-horizon-core"

GOVERNANCE_FILES = [
    "forge/gate.py",
    "forge/charter.py",
    "forge/protocol.py",
    "crucible/gate.py",
    "crucible/charter.py",
    "crucible/protocol.py",
    "CLAUDE.md",
    "DEFECTS.md",
    "analyst-verdicts/",
]

AGENTS_LIB = Path.home() / "antigravity" / "agents"
sys.path.insert(0, str(AGENTS_LIB))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import harness_lib
harness_lib.PROJECT_ROOT = PROJECT_ROOT

from charter import CHARTER_VERSION, PRE_SUBMIT_GATE, RULE_NO_INFLIGHT, RULE_NO_GOVERNANCE_CHANGE
from protocol import SESSION_START

AGENT = "forge"


def _project_health() -> bool:
    result = subprocess.run(
        ["go", "build", "./..."],
        capture_output=True,
        cwd=str(PROJECT_ROOT),
    )
    return result.returncode == 0


def _run_checks() -> list:
    checks = []

    ok = _project_health()
    checks.append({
        "name": "go-build",
        "passed": ok,
        "detail": "go build ./... passed" if ok else "go build ./... failed — fix build errors before submitting",
    })

    modified = harness_lib.check_governance_modified(GOVERNANCE_FILES)
    gov_passed = not modified
    checks.append({
        "name": "no-governance-change",
        "passed": gov_passed,
        "detail": "unmodified" if gov_passed else "governance file(s) modified — requires APPROVED Audit Verdict",
    })

    return checks


def cmd_session_start() -> None:
    env = {
        "print-context": lambda: harness_lib.print_context(AGENT, PROJECT_NAME),
        "inflight-count": lambda: harness_lib.count_inflight(AGENT),
        "print": print,
    }
    ts = datetime.now(timezone.utc).isoformat()
    print(f"[FORGE session-start] {ts}  charter v{CHARTER_VERSION}")
    print()
    harness_lib.eval_sexp(SESSION_START, env)


def cmd_pre_submit() -> None:
    checks = _run_checks()
    overall = all(c["passed"] for c in checks)
    block = harness_lib.format_gate_block(AGENT, "pre-submit", overall, checks, CHARTER_VERSION)
    print(block)
    harness_lib.append_signal(AGENT, "pre-submit", overall, checks)
    sys.exit(0 if overall else 1)


def cmd_lock(task_id: str) -> None:
    existing = harness_lib.read_lock(AGENT).get("in_flight")
    if existing:
        print(f"[FORGE] BLOCKED: '{existing}' already in flight. Unlock it first.")
        sys.exit(1)
    harness_lib.set_lock(AGENT, task_id)
    print(f"[FORGE] Lock set: {task_id}")
    print(json.dumps(harness_lib.read_lock(AGENT), indent=2))


def cmd_unlock() -> None:
    harness_lib.clear_lock(AGENT)
    print("[FORGE] Lock cleared.")


def main() -> None:
    usage = (
        "Usage: python3 forge/gate.py "
        "<session-start | lock <task-id> | pre-submit | unlock>"
    )
    if len(sys.argv) < 2:
        print(usage); sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "session-start":
        cmd_session_start()
    elif cmd == "lock":
        if len(sys.argv) < 3:
            print("Usage: python3 forge/gate.py lock <task-id>"); sys.exit(1)
        cmd_lock(sys.argv[2])
    elif cmd == "pre-submit":
        cmd_pre_submit()
    elif cmd == "unlock":
        cmd_unlock()
    else:
        print(f"Unknown command: '{cmd}'\n{usage}"); sys.exit(1)


if __name__ == "__main__":
    main()
