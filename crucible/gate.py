"""
crucible/gate.py — Event Horizon Core Crucible Gate.

Mandatory checkpoint commands (run from project root):

  python3 crucible/gate.py session-start              # Start of every session
  python3 crucible/gate.py pre-verdict --scripts-run  # Before filing any verdict
"""
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROJECT_NAME = "event-horizon-core"
INBOX_DIR = "crucible-inbox"

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

from charter import CHARTER_VERSION, PRE_VERDICT_GATE
from protocol import SESSION_START

AGENT = "crucible"


def _inbox_count() -> int:
    inbox = PROJECT_ROOT / INBOX_DIR
    return len(list(inbox.glob("*.md"))) if inbox.exists() else 0


def _run_checks(scripts_attested: bool) -> list:
    checks = []

    result = harness_lib.check_forge_gate_present(INBOX_DIR)
    checks.append({
        "name": "forge-gate-present",
        "passed": result["present"],
        "detail": result["detail"],
    })

    if scripts_attested:
        detail = "Crucible attests: all relevant verification steps run independently"
    else:
        detail = (
            "--scripts-run flag not passed. "
            "Re-run: python3 crucible/gate.py pre-verdict --scripts-run"
        )
    checks.append({"name": "scripts-attested", "passed": scripts_attested, "detail": detail})

    return checks


def cmd_session_start() -> None:
    env = {
        "print-context": lambda: harness_lib.print_context(AGENT, PROJECT_NAME),
        "inbox-count": _inbox_count,
        "print": print,
    }
    ts = datetime.now(timezone.utc).isoformat()
    print(f"[CRUCIBLE session-start] {ts}  charter v{CHARTER_VERSION}")
    print()
    harness_lib.eval_sexp(SESSION_START, env)


def cmd_pre_verdict(scripts_attested: bool) -> None:
    checks = _run_checks(scripts_attested)
    overall = all(c["passed"] for c in checks)
    block = harness_lib.format_gate_block(AGENT, "pre-verdict", overall, checks, CHARTER_VERSION)
    print(block)
    harness_lib.append_signal(AGENT, "pre-verdict", overall, checks)
    sys.exit(0 if overall else 1)


def main() -> None:
    usage = (
        "Usage: python3 crucible/gate.py "
        "<session-start | pre-verdict [--scripts-run]>"
    )
    if len(sys.argv) < 2:
        print(usage); sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "session-start":
        cmd_session_start()
    elif cmd == "pre-verdict":
        scripts_run = "--scripts-run" in sys.argv
        cmd_pre_verdict(scripts_run)
    else:
        print(f"Unknown command: '{cmd}'\n{usage}"); sys.exit(1)


if __name__ == "__main__":
    main()
