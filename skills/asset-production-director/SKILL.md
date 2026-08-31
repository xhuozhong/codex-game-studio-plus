---
name: asset-production-director
description: "Coordinate multi-category game assets with an art specification, provenance manifest, import contracts and runtime acceptance. Use when characters, scenes, UI, animation or audio must form a consistent playable deliverable."
---

# Asset production director

Own the handoff between art, content and implementation. Preserve the game's approved style and existing engine. For a single icon fix, keep the workflow proportionate; use a manifest when tracking a reusable batch or preparing assets for release.

## Define the batch

List the required assets, where players encounter them, dependencies and the stage that blocks the next playable feature. Establish a compact style reference: silhouettes, proportions, palette, camera, materials, lighting, UI typography and approved examples. Reuse licensed project assets before adding new tools or regenerating usable art.

Separate source, processed candidate and shipping asset. Agree on units, pivots, animation names, image dimensions, audio cues and target-device budgets before batch production. Do not impose a universal polygon or texture limit. Missing art can use clearly labelled placeholders, but placeholders must not be reported as finished art.

## Track and check

Use [the manifest contract](references/manifest.md) and the included Python 3.10+ standard-library checker. It reads only local files, never downloads or rewrites a manifest. A failed hash is a request to review the changed asset, not permission to regenerate approval records.

```text
python <skill-dir>/scripts/asset_manifest.py record --root <project> --file assets/hero.glb --id hero --kind model --source "self-authored character"
python <skill-dir>/scripts/asset_manifest.py audit --root <project> --manifest assets/manifest.json
python <skill-dir>/scripts/asset_manifest.py audit --root <project> --manifest assets/manifest.json --release
```

`record` emits a draft record to stdout with an unreviewed license. A release check requires declared license review, local license evidence and runtime evidence for each listed asset. It checks the files and declarations, not the truth of a legal claim or whether all game assets have been listed. Compare the manifest with the project's actual asset index and resource requests.

## Route production

Use an available image/model tool only for missing content; consult [provider boundaries](references/providers.md) when selecting one. Read the matching specialists only when needed: level construction, character animation, audio, localization, VFX, sprites or 3D optimization. These are task responsibilities, not an instruction to launch background agents.

At handoff, test one representative combined scene before multiplying the content. Inspect scale, style and materials, play every required animation, listen to sound in context, and repeat load/unload. Report separately: created, processed, imported, runtime-verified, or pending. A successful format checker does not promote an asset to runtime-verified.
