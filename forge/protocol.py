"""
forge/protocol.py — Universal Forge Protocol (DSL-encoded workflow steps).
Version: 1.0
"""

PROTOCOL_VERSION = "1.0"

# ── session-start ──────────────────────────────────────────────────────────────
# Informational only — never blocks. Prints durable state so Forge can
# reconstruct context at the start of every session.
# Host primitives: (print-context) → None, (inflight-count) → int
SESSION_START = [
    "begin",
    ["print-context"],
    ["if", ["gt", ["inflight-count"], 0],
     ["print", "ACTION: item in flight — check crucible-verdicts/ before starting new work"],
     ["print", "READY: no items in flight — pick up next task from TASKS.md"]],
]
