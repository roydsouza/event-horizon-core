"""
crucible/protocol.py — Universal Crucible Protocol (DSL-encoded workflow steps).
Version: 1.0
"""

PROTOCOL_VERSION = "1.0"

# ── session-start ──────────────────────────────────────────────────────────────
# Informational only. Prints durable state and signals whether a briefing
# is waiting for review.
# Host primitives: (print-context) → None, (inbox-count) → int
SESSION_START = [
    "begin",
    ["print-context"],
    ["if", ["gt", ["inbox-count"], 0],
     ["print", "ITEM AWAITING REVIEW: check crucible-inbox/ for latest briefing"],
     ["print", "IDLE: no briefings currently awaiting review"]],
]
