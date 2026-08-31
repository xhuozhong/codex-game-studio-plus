---
name: web-3d-asset-optimizer
description: Audit and optimize GLB or glTF assets for browser games, including export contracts, texture and geometry budgets, decoder compatibility and runtime verification. Use for shipping 3D assets, not general game-loop or scene architecture.
---

# Web 3D asset optimizer

Prepare assets for the project's existing renderer. Keep a recoverable source and compare every candidate against the original at the same camera, lighting and device settings.

## Establish a measurable contract

Identify the asset, intended use, screen coverage, animation clips, attachments/collision requirements and target devices. Record current transfer size, load/decode time and representative runtime cost when those measurements are available. Agree on a budget from the project; do not invent a universal triangle or texture limit.

The included [scripts/glb_inventory.py](scripts/glb_inventory.py) is a **read-only structural inventory**, using Python 3.10+ standard libraries. It reads `.glb` or `.gltf` metadata and reports counts, extensions, external URIs and SHA-256. It does not load external resources, download anything, optimize geometry, validate the full glTF specification or prove an asset renders correctly.

```text
python <skill-dir>/scripts/glb_inventory.py --input candidate.glb
```

Replace `<skill-dir>` with this skill's actual directory. For an inventory plus real transformations, read [references/workflow.md](references/workflow.md).

## Tool boundary

Blender, Node.js, glTF Transform, texture encoders and runtime decoders are **not bundled**. Discover installed versions and command help before using them. Use an existing project toolchain where possible; do not silently change global packages or install another engine. If a needed tool is unavailable, identify the missing operation and deliver the completed inspection or plan without claiming optimization occurred.

## Apply only justified changes

Work on a new candidate path. Choose operations from measured bottlenecks. Geometry compression, texture compression, simplification and merging address different problems; a smaller file can still decode slowly or draw inefficiently. Avoid combining several lossy operations before inspecting the first result.

Do not flatten hierarchies, merge meshes, rename nodes, remove unused-looking data or apply transforms blindly when animations, skins, attachment lookup, collider conventions or gameplay scripts depend on them. Treat asset contracts as part of the game interface.

Compression is a joint asset/runtime decision. Confirm support for every required glTF extension and serve its decoder assets correctly before switching the shipping URL. Preserve the uncompressed fallback until the chosen device/browser matrix is verified.

## Verify and deliver

Use [references/runtime-checklist.md](references/runtime-checklist.md) for the acceptance checks and report structure. Run every required clip; inspect silhouettes, normals, alpha edges, materials, pivots and collision alignment. Check transfer, decoder requests, console errors and performance in the real game.

Return the original and candidate sizes/hashes, exact tool versions/commands, changed features, measurements and remaining limitations. If no real renderer test was possible, label the result “prepared, runtime validation pending,” not “production ready.” Fixed upstream attribution is in [references/source.md](references/source.md).

## Executable candidate transformation (Plus 4)

The new [transform helper](scripts/transform_glb.py) calls an **already installed, explicitly supplied** glTF Transform CLI using Node, without shell execution or package installation. Supported operations are `dedup`, `resize` and `meshopt`; it accepts self-contained GLB v2 only, validates the candidate through that CLI, preserves the source and refuses an existing output. It does not measure runtime performance or automatically update game asset URLs.

```text
python <skill-dir>/scripts/transform_glb.py --input source.glb --output candidate.glb --node <node-executable> --cli-js <installed-cli/bin/cli.js> --operation dedup
```

Check installed CLI version/help before use; reviewed integration targets glTF Transform 4.4.2 and Node>=20. `resize` accepts `--width`/`--height`; `meshopt` requires a compatible runtime decoder. Test animation, attachments, materials and target runtime after every candidate. Third-party tools remain external dependencies under their own licenses.
