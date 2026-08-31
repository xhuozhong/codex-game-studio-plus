---
name: game-level-builder
description: "Build and integrate game levels from Tiled, LDtk or existing scene data, checking asset references, spawn points, collision and transitions. Use for actual level construction, not abstract game-loop design."
---

# Game level builder

Keep the project's editor, engine and map conventions. Identify its loader and supported format/version before importing; LDtk JSON is not Tiled JSON. Phaser supports a subset of Tiled exports, not every editor feature. Three.js and editor engines require their own scene/loader integration.

## Make an editable level

Agree on grid/world units, map origin, layer meanings, stable entity IDs, collision ownership, spawn/exit points and trigger references. Keep authored data separate from generated engine files. Make a small connected space that supports the intended player journey; test doors, return paths, saves and scene reload before making more rooms.

## Local structural preflight

The Python 3.10+ standard-library [level checker](scripts/level_audit.py) accepts finite Tiled numeric JSON maps (embedded or external JSON/TSJ tilesets) and LDtk project files. It checks local referenced files, tile ranges/array dimensions and object/entity IDs. The optional Tiled spawn check treats nonzero collision cells as solid and requires unshifted point objects and layers.

```text
python <skill-dir>/scripts/level_audit.py --root <project> --map assets/room.json
python <skill-dir>/scripts/level_audit.py --root <project> --map assets/room.json --spawn-layer Spawns --collision-layer Collision
```

Unsupported chunks, encoded arrays, TSX, transformed/grouped point-spawn setups must use an appropriate project loader check; do not convert them silently. The checker does not prove pathfinding, arbitrary collision shapes, LDtk EntityRef validity or successful engine import.

## Runtime acceptance

Run the actual importer; inspect missing images, flip flags, tile offsets, entity positions and collision layers. Traverse the intended route and an invalid route, enter/leave twice, restore a save and repeat the editor export. Verify stable IDs, no duplicated handlers/entities, no disappearing collision and no stale resource references. Use project performance budgets when adding streaming or dense scenes.

Read [format and license notes](references/formats.md) only for the selected editor. Deliver editable source, import configuration, changed asset references and evidence from the playable level.
