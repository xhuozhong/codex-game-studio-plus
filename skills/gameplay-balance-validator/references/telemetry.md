# Small telemetry checker contract

`scripts/validate_telemetry.py` is a Python 3.9+ standard-library helper. It reads exported JSON, checks event accounting, reports repeated opportunities, optionally checks a declared cap/cooldown, and pairs deterministic policy runs. It is not a simulator, statistical package, or universal game adapter. Adapt the game's export to this schema or use existing equivalent project tooling; do not reshape a game just to fit this helper.

Run from this Skill's directory:

```text
python scripts/validate_telemetry.py game-log.json --baseline hold --candidate timed
python scripts/validate_telemetry.py game-log.json --max-scores-per-opportunity 1 --cooldown-ticks 5
```

The optional cap applies to all score events per `opportunity_id`, and cooldown applies to all accepted inputs per `(actor, action)`. Do not use these options for mixed mechanics with different rules; export a focused probe or use a project-specific assertion. Cooldown requires full activation history since reset; a mid-run excerpt can miss a violation at its first event. Repeated opportunities without an explicit cap are observations, not automatic defects. Negative scoring events also count toward the event cap; choose a different assertion for reward/correction pairs.

Example completed run (a single run checks accounting but cannot compare policies):

```json
{
  "schema_version": 1,
  "runs": [{
    "run_id": "timed-seed-42",
    "policy": "timed",
    "policy_version": "1",
    "configuration_id": "revision-config-budget-identity",
    "seed": 42,
    "tick_rate": 60,
    "max_ticks": 600,
    "elapsed_ticks": 120,
    "status": "completed",
    "end_state": "game_over",
    "initial_score": 0,
    "score": 2,
    "coverage": {"input": "recorded", "spawn": "recorded", "score": "recorded", "death": "recorded"},
    "events": [
      {"id": "e1", "tick": 1, "type": "spawn", "entity_id": "target-1-generation-1"},
      {"id": "e2", "tick": 30, "type": "input", "actor": "player-1", "action": "pulse", "accepted": true},
      {"id": "e3", "tick": 30, "type": "score", "delta": 2, "opportunity_id": "player-1-target-1-generation-1", "reason": "timed_hit"},
      {"id": "e4", "tick": 120, "type": "death", "cause": "collision"}
    ]
  }]
}
```

Every completed run requires these fields. Additional fields are retained in the original input, not interpreted by the helper. Events are ordered by nonnegative tick; equal ticks are allowed. IDs are unique per run. Score sum tolerance is `1e-9` absolute/relative, so use game-specific exact arithmetic for large counters or currency. A finite nonzero initial score is allowed, but all subsequent changes must appear as deltas.

`coverage` requires all four categories set to `recorded` or `not_applicable`. A recorded category can have zero events in a valid run; an event marked not applicable is a contradiction. This declaration cannot prove instrumentation completeness, hidden-state restrictions, or honest causal opportunity IDs: verify those at the adapter and actual game.

Use `seed: null` for unseeded runs. They receive summaries but are excluded from deterministic pairing. `configuration_id` must identify settings, public input/visibility schema, initial state, engine/revision, and exploration budget; equality is supplied by the exporter and cannot be verified by the script. To compare revisions, export paired results under an explicitly documented equivalence configuration and preserve each actual revision separately in extra metadata. Never falsely equate changed rules/settings outside the intended experimental change.

Pairing requires identical configuration, typed seed (string `"42"` differs from integer `42`), tick rate and max ticks, with one run per policy per pair. Early game-over is allowed; elapsed duration need not match. Mixed policy versions or duplicated pairs invalidate the comparison. Missing counterparts are listed instead of silently counted as a win. No pairs yields a null median. The score ratio is null for a zero/negative baseline; the raw difference remains available.

A failed instrument run uses `status: "harness_error"`, an `error` string, and the four identity fields (`run_id`, `policy`, `policy_version`, `configuration_id`). It is excluded from comparisons and counted separately. A legitimate game loss remains `completed` with its actual end state. Run failures need investigation even if remaining telemetry passes.

Exit codes: `0` structurally valid telemetry with no requested rule violation, `1` requested cap/cooldown violation, `2` malformed/inconsistent telemetry or an invalid comparison. Code 0 does not mean the game, instrumentation, or balance passed. JSON on stdout is deterministic for the same data and options; save it using normal shell redirection if needed.
