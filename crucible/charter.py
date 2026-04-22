"""
crucible/charter.py — Universal Crucible Charter (DSL-encoded policy rules).
Version: 1.0

Two universal rules. Projects add a third (project-health) if needed.
"""

CHARTER_VERSION = "1.0"

# ── Rule 1 ─────────────────────────────────────────────────────────────────────
# The briefing under review must contain a Forge GATE-PASS block.
# Host primitive: (forge-gate-ok) → bool
RULE_FORGE_GATE_PRESENT = [
    "if", ["forge-gate-ok"],
    True,
    False,
]

# ── Rule 2 ─────────────────────────────────────────────────────────────────────
# Crucible must explicitly attest it ran all relevant verification steps
# before issuing any verdict. Passed as --scripts-run flag.
# Host primitive: (scripts-attested) → bool
RULE_SCRIPTS_ATTESTED = [
    "if", ["scripts-attested"],
    True,
    False,
]

# ── Composite gate ─────────────────────────────────────────────────────────────
PRE_VERDICT_GATE = [
    "and",
    RULE_FORGE_GATE_PRESENT,
    RULE_SCRIPTS_ATTESTED,
]
