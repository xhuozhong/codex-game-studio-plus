# Source and license record

This folder is independently written for Codex Game Studio Plus. Its helper script is original implementation; no upstream Python code, Skill body or reference file has been copied into this folder. The workflow was informed by the upstream concept of whole-strip generation and common-scale/anchor normalization.

Fixed upstream reference:

- Repository: [openai/plugins](https://github.com/openai/plugins).
- Commit: `cd0fccd4ed62dded584c16246685b232d7bfe7f6`.
- [sprite-pipeline/SKILL.md at that commit](https://github.com/openai/plugins/blob/cd0fccd4ed62dded584c16246685b232d7bfe7f6/plugins/game-studio/skills/sprite-pipeline/SKILL.md).
- [Game Studio manifest at that commit](https://github.com/openai/plugins/blob/cd0fccd4ed62dded584c16246685b232d7bfe7f6/plugins/game-studio/.codex-plugin/plugin.json): plugin version `0.1.2`, author name `OpenAI`, license identifier `MIT`.

The upstream manifest's MIT declaration is recorded as observed metadata. No upstream LICENSE body or copyright year is invented here. Upstream code is not redistributed. This independent folder's terms are in [LICENSE](../LICENSE); that file is not presented as an upstream license copy.

Changes in this independent implementation: a single portable CLI; explicitly constrained PNG input; no automatic background removal, image-generation calls or first-frame substitution; guarded new-directory output; shared-scale manifest; atlas and visual previews. Pillow is an external dependency and retains its own license.
