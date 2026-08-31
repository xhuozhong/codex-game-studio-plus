# Attribution and adaptation

This Skill combines and adapts MIT-licensed workflows from [abagames/agentic-gamedev-skills](https://github.com/abagames/agentic-gamedev-skills), fixed at commit [9ad6a310c66f707405f23f5771e8b4bd139c7e62](https://github.com/abagames/agentic-gamedev-skills/commit/9ad6a310c66f707405f23f5771e8b4bd139c7e62), authored upstream by abagames (copyright 2026). The unmodified upstream license is included in [LICENSE](LICENSE). This upstream attribution does not imply endorsement of Codex Game Studio Plus.

Source materials: `evaluating-gameplay-balance/SKILL.md`, its `references/simulation-harness.md`, `implementing-gameplay-invariants/SKILL.md`, and its `references/invariant-patterns.md`, all under upstream `.agents/skills/`. Exact upstream paths, Git blob IDs, SHA-256 hashes and adaptation mapping are recorded in [source-provenance.json](source-provenance.json).

Adaptation replaces two separate Skills with one entry point and two progressively loaded workflows. It removes references to absent Godot/other sibling Skills, project-specific selection funnels and fixed repair limits. It scopes anti-idle/anti-spam rules to the game's declared design, uses appropriate feedback rather than a mandatory gauge for every rule, and removes the implication that small-sample min/max bands establish significance. No universal score ratio proves a game is fun or a design is defective.

`scripts/validate_telemetry.py` and its documented schema are new integration code, not an upstream simulator or upstream log format. The adaptations and new helper in this directory are distributed under the included MIT terms. Other directories in the larger package may have different licensing; this notice does not assign a license to the original 1+10 collection.
