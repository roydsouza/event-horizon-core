"""
forge/charter.py — Universal Forge Charter (DSL-encoded policy rules).
Version: 1.0

Two universal rules. Projects add a third (project-health) if they need a
runtime health check before submission. New rules are added only when an
actual violation is observed in an audit and the fix cannot be achieved by
tightening the existing two.

S-expressions are evaluated by gate.py via harness_lib.eval_sexp.
"""

CHARTER_VERSION = "1.0"

# ── Rule 1 ─────────────────────────────────────────────────────────────────────
# Never start or submit new work while something is already in flight.
# Host primitive (injected by gate.py): (inflight-count) → int
RULE_NO_INFLIGHT = [
    "if", ["gt", ["inflight-count"], 0],
    False,
    True,
]

# ── Rule 2 ─────────────────────────────────────────────────────────────────────
# Governance files may not be modified without an explicit APPROVED Audit Verdict.
# Host primitive: (governance-modified) → bool
# The list of governance files is defined per-project in gate.py.
RULE_NO_GOVERNANCE_CHANGE = [
    "if", ["governance-modified"],
    False,
    True,
]

# ── Composite gate ─────────────────────────────────────────────────────────────
# Projects that add a RULE_PROJECT_HEALTH should extend this to:
#   PRE_SUBMIT_GATE = ["and", RULE_NO_INFLIGHT, RULE_PROJECT_HEALTH, RULE_NO_GOVERNANCE_CHANGE]
PRE_SUBMIT_GATE = [
    "and",
    RULE_NO_INFLIGHT,
    RULE_NO_GOVERNANCE_CHANGE,
]
