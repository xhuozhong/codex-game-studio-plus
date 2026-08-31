# Animation backend selection

For sprite strips, use an explicit frame layout/pivot contract and the existing sprite pipeline when available. For packed atlases, preserve trim/source size and frame offsets; do not align jump frames by their changing visible bottom edge.

[Spine Runtimes](https://github.com/EsotericSoftware/spine-runtimes) is a 2D skeletal route with a [dedicated license](https://github.com/EsotericSoftware/spine-runtimes/blob/4.3/LICENSE). The relevant developer/editor licensing conditions must be met; this package does not redistribute Spine or grant its rights. Lock editor export/runtime versions and check backend-specific support. Reviewed TS 4.3 sources include Phaser 3/4 and Three backends; the Three backend does not support two-color tint. Do not assume Unity and TS version contracts match.

For 3D, use the actual project's Blender/editor and glTF/FBX import pipeline. Establish rest pose, axis mapping, root motion, skin weights, inverse bind matrices and socket names before retargeting. Baking can make a constraint animation portable but changes editability; retain the source rig. FBX/glTF export does not guarantee every editor constraint, material or animation feature survives.

Optional [Blender MCP](https://github.com/ahujasid/blender-mcp) is only a bridge, with default telemetry and Python execution to review before use. No editor, model service or retargeter is installed by this skill. Use the existing 3D optimizer only after animation and attachment contracts are stable; mesh/node merging or deduplication can alter bindings and must be inspected.
