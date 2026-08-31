---
name: game-vfx-engineer
description: "Implement and validate game particles, shaders and post-processing with gameplay timing, quality tiers and measured rendering cost. Use for runtime visual effects, not static illustration or UI layout."
---

# Game VFX engineer

Identify the current renderer, backend and color pipeline before choosing an effect. Preserve the project's engine and WebGL/WebGPU route. For Three WebGL, postprocessing is one optional implementation; it does not directly cover WebGPU or other engines. Read [renderer boundaries](references/renderers.md) when adding a backend.

## Build the effect contract

Specify the event, duration, coordinate space, attachment point, blend mode, layer/depth behavior and cleanup. Use gameplay timing for the trigger and rendering time for its visual progression; a restarted animation must not trigger another hit. Respect readable combat silhouettes, text contrast and user settings for motion/flashes.

For shader/material work, distinguish color textures from data maps, normal convention, alpha mode, tone mapping and output color space. Check the material under more than one lighting condition. Do not mistake a pretty bloom screenshot for correct PBR textures or final art.

## Validate in the game

Compile/link using the real project renderer, inspect runtime errors, then trigger the effect at actual game scale and under rapid repeated use. Compare fixed camera/resolution scenes with and without the effect, recording frame time and quality settings. Test transparent sorting, resize, pause, scene teardown/reload and resource disposal. Design a lower-cost tier from measured bottlenecks; do not prescribe universal particle counts.

Deliver shader/effect source, required textures and licenses, runtime version, presets, trigger/cleanup integration and captured evidence. When the renderer cannot run, report code/preparation separately from visual and performance acceptance.
