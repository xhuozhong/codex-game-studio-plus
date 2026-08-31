---
name: character-animation-integrator
description: "Integrate game character animations, skeletons, attachments and animation events across existing 2D or 3D runtimes. Use for clip transitions, skinning, retargeting or equipment, not one-off static sprite art."
---

# Character animation integrator

First distinguish a sprite strip, a 2D bone rig and a 3D skinned character. A generated mesh is not an animation-ready character. Keep the project runtime and preserve the source skeleton, animation IDs and attachment conventions.

## Establish the animation contract

Record rest pose, units/axes, skeleton and clip versions, in-place versus root motion, state transitions, loop policy, blend durations, interruption rules, gameplay event IDs and equipment sockets. Choose which system owns movement; do not apply both root displacement and controller movement accidentally.

For existing sprite strips, use the available sprite pipeline with an explicit layout. Grounding all frames removes deliberate jump/hover offsets; preserve those offsets or let the gameplay transform represent them. Multirow or packed atlases need their real frame rectangles and pivots.

For 2D skeletons, match the editor export and runtime versions. Spine is an optional licensed dependency, not a bundled free editor/runtime. For 3D rigs, inspect weights, bind pose, bone axes and rest-pose mapping before retargeting. Do not flatten or rename nodes that gameplay/attachments reference. Read [runtime boundaries](references/runtimes.md) for the chosen route.

## Integrate and verify

Play every required clip in the actual engine. Check idle/move/action/hit/death or the project's equivalent transitions, interruptions, mirrored facing and equipment attachments. Fire gameplay effects from a defined event source; replay/loop/transition must not duplicate damage or sound. Save/load and network reconciliation, if present, must preserve the intended state without re-firing past events.

Inspect silhouette, feet, hands, deformation, alpha edges, bounds/culling and blend artifacts at actual game scale. Test pause/resume and scene teardown. Runtime support differs among backends; a viewer screenshot alone does not prove attachment, physics or gameplay integration.

Deliver source and shipping rig/atlas, version/clip mapping, event contract, attachment tests and runtime evidence. If no compatible editor or runtime is available, report inspected facts and missing steps instead of claiming a completed rig.
