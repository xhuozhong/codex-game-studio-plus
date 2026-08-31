---
name: sprite-animation-pipeline
description: Normalize transparent horizontal sprite strips into consistent game animation frames, atlases and previews. Use for sprite slicing, common scale, grounded bottom-center anchors and animation delivery; image generation requires a separate available tool.
---

# Sprite animation pipeline

Turn an existing strip into inspectable game assets. Preserve the character's approved appearance and the project's frame contract. This skill includes a working normalization helper; it does not include an image generation service.

## Choose the operation

- For an existing strip, inspect it and confirm the number of equal horizontal slots, target frame dimensions and playback speed.
- For new artwork, first establish the reference character and required poses. If a generation tool is available, request a complete strip with the same character, facing and palette. Follow that tool's rules for creating or editing images. If unavailable, prepare the prompt and asset specification without claiming to have generated images.
- For multi-row sheets, packed atlases, opaque backgrounds, independent pose offsets or root-motion animation, do not guess a horizontal layout or remove a background automatically. Obtain an explicit layout or use an appropriate editor before normalization.

## Normalize safely

Use [scripts/sprite_strip.py](scripts/sprite_strip.py). It needs Python 3.10+ and Pillow, which are external dependencies listed in [requirements.txt](requirements.txt). It does not install packages or make network requests.

```text
python <skill-dir>/scripts/sprite_strip.py --input raw-walk.png --frames 6 --frame-width 64 --frame-height 64 --out-dir walk-v1 --padding 2 --fps 10
```

Replace `<skill-dir>` with the actual folder containing this file. Arguments work in PowerShell or other shells; quote paths containing spaces.

The helper crops each slot by alpha, computes one scale for the entire strip, and places each visible crop at the same bottom-center baseline. It creates individual RGBA PNGs, a horizontal atlas, a checkerboard contact sheet, an animated GIF preview and a JSON manifest. It refuses to replace an existing output directory. The source image remains unchanged.

Read [references/usage.md](references/usage.md) for sizing, empty-frame handling and output details. Bottom-center normalization is useful for grounded poses but removes deliberate vertical/horizontal displacement. Do not apply it to jumps, hovering or root motion without deciding how those offsets will be represented.

## Review before integration

Check the contact sheet and animation at actual game size, not just a magnified still. Look for clipped weapons/hair, foot sliding, unwanted scale changes, inconsistent facing and loop discontinuities. The PNGs preserve alpha; the GIF is a checkerboard preview, not a shipping transparent asset.

Import a candidate atlas alongside the current asset, using the manifest's fixed cell size. Check animation timing, origin, filtering and collision separately in the running game. Change the game's asset index only after the candidate is verified. Report what was checked visually and what remains untested.

## Delivery

Give the asset paths, frame count, size, FPS, common scale, anchor convention and any intentional blank frames. Keep the original strip and provenance. Consult [references/source.md](references/source.md) for the fixed upstream reference and licensing boundary.
