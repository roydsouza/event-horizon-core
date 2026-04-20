# Event Horizon Core — Defects

This is the contract for bug fixes. Forge picks up defects here **before** working on `TASKS.md`.

**Format:** Each defect has a DEF-XXX id, a description, a verification criterion (the exact output or behavior that confirms the fix), and a status marker.

| Status | Meaning |
|--------|---------|
| `[ ]` | Open — available for Forge to pick up |
| `[/]` | In Progress — Forge has this; do not touch |
| `[x]` | Fixed — Crucible verified + verdict on file in `../ehc-lpg/crucible-verdicts/` |

**Rules:**
- Fix only the claimed defect per commit — no feature additions in the same commit.
- Reference the DEF-XXX id in the commit message and briefing.
- Crucible must verify the exact verification criterion stated here, not a paraphrase.

---

*No open defects at this time.*
