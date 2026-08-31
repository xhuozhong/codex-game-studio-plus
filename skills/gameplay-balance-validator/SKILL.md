---
name: gameplay-balance-validator
description: Validate game rules and compare play policies using reproducible telemetry. Use for duplicate scoring, cooldown loopholes, risk/reward promises, or balance regressions; not for general engine setup or claims that metrics prove fun.
---

# Gameplay Balance Validator

Turn an agreed design promise into a measurable rule, then use actual game events to locate violations. Keep the user's genre and intended experience: idle rewards, automatic attacks, or safe waiting can be intentional. Do not import an anti-idle objective into a game that does not have one.

Choose the reference matching the task:

- **Diagnose or compare policies:** read [balance-workflow.md](references/balance-workflow.md). It covers reproducible adapters, visible-state inputs, instrument confidence, and before/after evidence.
- **Implement or review a specific rule:** read [invariants-workflow.md](references/invariants-workflow.md). It covers opportunity lifecycles, repeated scoring, cooldowns, resource constraints, and visible feedback.
- **Validate an exported event log:** read [telemetry.md](references/telemetry.md), then use `scripts/validate_telemetry.py` if its small schema fits the project. It does not run a game or replace the project's own tests.

Keep these distinctions explicit:

1. A broken adapter, dropped events, mismatched configuration, or a search policy unable to engage the mechanics is a **measurement failure**, not evidence of bad game design.
2. A rule can be specified, exercised in a simulator, and verified in the actual game at different times. Report the achieved level; do not imply unseen browser play or screenshot inspection.
3. Score differences and simple ratios are exploratory signals. They do not establish statistical significance, enjoyment, fairness, or a universally better strategy.
4. The policy may read only declared player-visible state. A separate diagnostic oracle must be labeled and excluded from ordinary-player comparisons. Instrumentation can observe hidden state for debugging without exposing it to the policy.

Deliver the design promise, test configuration, raw evidence location, detected rule or instrumentation failures, smallest justified change, rerun result, and unverified gaps. Retain failing seeds and input traces. Do not alter rules merely to satisfy a tester, add hidden agent-specific behavior, or replace the core game when a narrow repair was requested.

Adapted from two MIT-licensed abagames workflows. See [NOTICE.md](NOTICE.md), [LICENSE](LICENSE), and [source-provenance.json](source-provenance.json).
