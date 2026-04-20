# Quality & Goodness Framework

The fundamental issue mapping performance of Local LLMs resides in bridging the gap between empirical, robotic telemetry (TTFT, TPS) and subjective, qualitative traits (Context bridging, Tool execution, Logical adherence). 

The goal for `event-horizon-core` is zero abstractions outside of the agent layer itself, meaning the Orchestration interface needs a normalized profiling rubric to assess hardware-level telemetry mixed with human assessment.

---

## 1. Multi-Dimensional Load Profiles

Different client pathways interacting with `event-horizon-core` maintain vastly different Goodness matrices. We identify two principal archetypes:

### 🛡️ Firewall Profile (Shapeshifter-Airlock)
This profile intercepts requests in order to determine malice, constraint compliance, or context-leak severity. 
*   **Reasoning Logic [Heavy Weight]:** The ability to parse multi-hop questions directly without confusing variable definitions.
*   **Prompt Adherence [Heavy Weight]:** Refusal to override standard operating procedures when interacting with an adversarial injection prompt.
*   **Refusal Robustness [Heavy Weight]:** Security guarantees strictly disallowing behavior.
*   **TTFT / TPS [Low Weight]:** Latency is largely tolerated if the decision constraints map out correctly on behalf of the orchestration suite. Wait times of <5 seconds are largely disregarded relative to safety parameters.

### 🦅 Agent Profile (Claws)
Direct interaction sub-agent deployments rely heavily on conversational interactivity and structured response paths.
*   **Tool-Calling Precision [Heavy Weight]:** Strict emission of exact function signatures (without hallucinating extra inputs).
*   **JSON Schema Adherence [Heavy Weight]:** Returning data structures that do not inherently break generic parser middleware strings.
*   **TTFT (Time To First Token) [Heavy Weight]:** Interactivity determines UI/UX flows. A metric `TTFT` exceeding `1000ms` incurs aggressive penalties.
*   **Context Utilization [Medium Weight]:** The ability to maintain persona details from previous system-prompt structures over time.

---

## 2. Goodness Score Algorithm

The implementation of a normalized **Goodness Score (GS)** allows evaluating model swaps directly (`0 - 100`).

We map:
1.  **Reasoning Score (RC)**: Human/Agent evaluation score out of 100 on logic capability.
2.  **Tokens Per Second (TPS)**: Extracted passively from our telemetry buffers.
3.  **Time To First Token (TTFT)**: Extracted passively from stream inception blocks.

### The Algorithm

```text
GS_base = (RC * W_reasoning) + (TPS_normalized * W_tps) - (TTFT_Penalty)

// Values for the Default Unified Archetype:
W_reasoning = 0.50 
W_tps       = 0.30

TPS_normalized = min((TPS / Target_Max_TPS) * 100, 100)
// Extrapolation: 50 TPS is broadly targeted as instantaneous read speed per hardware setup constraint.

TTFT_Penalty = max(0, (TTFT_ms - Tolerance_Gap) * Penalty_Weight)
// Extrapolation: Tolerance is set to 800ms. Evert 100ms over adds a -1 point drop.
```

*When combined, a model serving rapid ~45 TPS streams with sub-600ms latency but moderate reasoning (around 70) would score a highly functional baseline, whereas a brilliant model serving 10 TPS dynamically tanks its overall utility index.*
