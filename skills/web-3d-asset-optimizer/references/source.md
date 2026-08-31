# Source and license record

This folder is independently written for Codex Game Studio Plus. No upstream script, Skill body or reference file is copied. The upstream workflow informed the separation between asset preparation and runtime architecture.

Fixed upstream reference:

- Repository: [openai/plugins](https://github.com/openai/plugins).
- Commit: `cd0fccd4ed62dded584c16246685b232d7bfe7f6`.
- [web-3d-asset-pipeline/SKILL.md at that commit](https://github.com/openai/plugins/blob/cd0fccd4ed62dded584c16246685b232d7bfe7f6/plugins/game-studio/skills/web-3d-asset-pipeline/SKILL.md).
- [Game Studio manifest at that commit](https://github.com/openai/plugins/blob/cd0fccd4ed62dded584c16246685b232d7bfe7f6/plugins/game-studio/.codex-plugin/plugin.json): plugin version `0.1.2`, author name `OpenAI`, license identifier `MIT`.

The manifest's license identifier is observed metadata, not an invented upstream LICENSE body. No upstream copyright year is asserted. This folder's independently authored material is covered by [LICENSE](../LICENSE); it is not an upstream license copy.

Independent additions include a Python standard-library metadata inventory, explicit no-fetch behavior, output limitations, preservation of gameplay/animation contracts and a before/after acceptance report. Blender, glTF Transform, Three.js and encoders/decoders are external tools governed by their own licenses, not bundled components.
