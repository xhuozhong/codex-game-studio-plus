# Convert design promises into observable rules

Start from the project's actual rules, not a generic preference against idle, holding, or repeated input. Separate an intentional clicker/idle reward from an accidental repeat reward on a consumed target.

For each disputed mechanic, record:

| Field | What to specify |
| --- | --- |
| Promise | The desired player outcome and its source in the design |
| Scope | Per actor, action, target, opportunity lifecycle, resource, or time window |
| Rule | Precise condition and consequence, including boundary ticks |
| Readout | Feedback that lets players anticipate or understand the rule |
| Evidence | Input trace, event fields, initial state, and pass/fail condition |

## Opportunity identity and score accounting

A scoring object needs an explicit lifecycle: created, eligible, consumed/scored, expired; define whether and how a new lifecycle may score again. Use stable actor and opportunity identifiers, including a generation/cycle when IDs can be reused. A projectile hitting two targets is not a duplicate merely because the projectile ID repeats. Conversely, issuing a new logger event ID on each frame does not make one target a new opportunity.

For a once-per-opportunity rule, perform eligibility, consumption, and reward as one logical state transition. In multiplayer, check that the authority applies the transition once despite client retries or duplicate delivery. Log rejected attempts as inputs/diagnostics, not as accepted score events. Track score changes including penalties; reconcile final score with the initial value and all score deltas. Reset/round bonuses require explicit events or separate runs.

Probe a normal hit, a repeated collision next frame, two inputs in the same tick, expiration, ID reuse with a new lifecycle, and scene/round restart. Choose score caps and event identities from the rule, not from the observed data.

## Cooldowns, pulses, and resources

- **Cooldown:** define the clock, action/actor scope, and inclusive boundary. If the rule is nextAllowedTick = lastAcceptedTick + N, tick N is legal and N-1 is not. Rejected attempts must not accidentally refresh a cooldown unless that is explicitly intended. Test pause/resume, restart, and time scaling where relevant.
- **Pulse/reflection/AoE:** limit scoring by real opportunities; independently bound effect lifetime and cleanup. A cooldown alone may still allow rescoring one long-lived target. Track both accepted activations and score per opportunity.
- **Resources:** when holding safety is intended to cost energy, test depletion, recovery, simultaneous actions, and underflow. When safety with passive rewards is intentional, verify those intended bounds instead of adding punishment.
- **Combos:** specify the exact events that advance/reset the multiplier and when the player sees its state. Do not replace a missing rule with an unexplained increase in enemy speed.

Avoid hidden rules that only target a test policy. A constraint that changes player decisions needs appropriate visible or audible feedback early enough to act. A persistent gauge is useful for accumulating pressure, but not mandatory for every discrete rule. Verify feedback with actual gameplay/screenshots; arithmetic tests cannot establish readability.

## Evidence before broad comparisons

Write a small counterexample that fails when the rule is broken: two accepted actions inside a cooldown, two rewards for one consumed opportunity, a resource going below zero, or an unbounded object count. Exercise exact boundaries and the legitimate exception cases. A synthetic fixture proves a validator can detect the defect; it does not prove the game is instrumented correctly.

Then rerun the relevant policies under the [comparison contract](balance-workflow.md). If no runtime or adapter is available, deliver the invariant and a concrete manual check, labeled specified but unverified. Do not claim the rule improves enjoyment merely because the score comparison changes.
