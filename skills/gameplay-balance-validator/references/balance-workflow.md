# Compare policies without confusing the game and the instrument

Read the design goal first. Select policies that test that goal: no input, hold, periodic presses, rapid presses, a visible-state heuristic, a recorded player trace, or an exploratory search. Do not require every game to punish all simple policies.

## Establish the comparison contract

Use the actual update logic through a thin engine-local adapter where possible: reset(seed), step(publicInput), score(), ended(), and a declared visible-state snapshot. A separate forward model needs a small set of replay comparisons against the actual game before its results can support game claims.

Record game revision, configuration, initial conditions, input semantics, policy version, visibility fields, tick rate, time limit, RNG seeds, and exploration budget. Keep a seed set for development and another for evaluation. Replay the same seeds on both policies and before/after revisions. Fixed seed alone does not prove determinism: replay the same trace twice and compare state/event checkpoints. Account for independent RNG streams, physics ordering, asynchronous inputs, and floating-point differences.

Log actual input acceptance/rejection, spawns, scoring reasons/opportunity identities, hazards/deaths, elapsed ticks, and final state. Include applicable resource levels and active-entity counts. Explicitly identify a legitimately absent event category; a game with no deaths is different from a logger that forgot death events. Preserve raw traces rather than only a score summary.

## Validate the instrument before diagnosing balance

- Confirm the adapter delivers inputs and records the expected score-changing events.
- Confirm a replayed human or known-valid sequence can use the core mechanic. Inspect exploratory search history and engagement with opportunities. A flat search result can mean the searcher failed, not that varied play is inferior.
- Confirm all policies have the same legal action space and declared visible observations. Keep privileged oracle results separate.
- Check event accounting, seed/configuration pairing, run duration, crashes, timeouts, focus loss, throttling, and dropped samples. Do not count a harness error as a zero-scoring game loss.
- Run serially unless a calibration demonstrates that isolated parallel instances preserve relevant timing. State isolation alone does not prevent CPU/GPU contention or background-tab throttling.

Missing instrumentation blocks root-cause conclusions. Add the smallest probe that can distinguish the competing explanations, then rerun; do not redesign from an unexplained ratio.

## Read the results

Compare per-seed score differences and survival/end state alongside causal events: repeated scoring on one opportunity, input cadence near deaths, unavoidable spawn positions, indefinite safety, resource drain, or a multiplier preserved by a trivial policy. A strategy can trade score for safety intentionally.

If desired, report candidate/baseline score ratios only when the baseline is positive and scoring semantics make ratios meaningful. For zero or negative denominators report the raw scores and difference; never emit infinity as a win. Best-of-search scores depend on search budget and are not ordinary-player averages. Do not compare unequal search budgets without rerunning both conditions.

When deterministic execution is unavailable, predefine observation windows, run counts, sampling cadence, and exclusion rules; alternate or randomize policy order where feasible. Report all valid samples, distributions, and failures. Small-sample min/max bands are exploratory descriptions only. Non-overlap of a few bands does not establish significance, and overlap does not establish no effect. Use an experiment and uncertainty analysis appropriate to the claim; disclose limited power and multiple comparisons rather than inventing a universal minimum sample count.

## Repair and rerun

Trace the observed defect to a design promise or implementation mismatch. Use [invariants-workflow.md](invariants-workflow.md) for a focused rule repair. Numeric tuning is legitimate when the rules already implement the intended experience; structural changes are not automatically better. Preserve visible costs and readability.

Rerun the failure trace and comparable evaluation set after the change, then inspect the relevant behavior in the actual game. If the repair requires changing the user's core experience, report the conflict and propose a scoped design choice rather than quietly substituting another game. Withdraw an earlier conclusion if more evidence does not support it.
