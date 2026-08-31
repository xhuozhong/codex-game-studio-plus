# Strip normalization

Run the bundled helper from any working directory with an absolute script path, or from the skill folder with `python scripts/sprite_strip.py`.

## Input contract

- One static PNG containing N equal-width slots in a single horizontal row.
- Background transparency must already exist. RGB artwork, uniformly opaque alpha and animated PNGs are refused rather than silently treated as clean sprites.
- Source width must be divisible by N. Slot boundaries are authoritative: the helper cannot repair artwork crossing a boundary.
- Alpha greater than zero defines the crop. Inspect faint stray pixels first; even nearly invisible pixels affect sizing.
- Default behavior rejects completely empty slots. Use `--allow-empty` only when blank frames are intentional. At least one slot must contain visible pixels.

## Options

| Argument | Meaning |
|---|---|
| `--input` | Source PNG; never modified |
| `--frames` | Number of horizontal slots, 1–256 |
| `--frame-width`, `--frame-height` | Each output cell, 1–2048 pixels |
| `--out-dir` | New directory; an existing file or directory is refused |
| `--padding` | Minimum border, default 2 pixels |
| `--fps` | Preview playback speed, 1–60; default 10 |
| `--resample` | `nearest` for pixel art (default), `lanczos` for smooth art |
| `--allow-upscale` | Permit a common scale greater than one |
| `--allow-empty` | Keep intentionally transparent frames in their original positions |

For visible crop widths `w[i]` and heights `h[i]`, the shared scale is the smaller of `(cell_width - 2 * padding) / max(w)` and `(cell_height - 2 * padding) / max(h)`. It is capped at one unless upscaling is requested. Integer rounding of raster dimensions can introduce at most a pixel of size quantization. Pixel art may need a chosen integer scale for an exact pixel-grid result.

Each resized crop is centered horizontally and ends at `cell_height - padding`. This intentionally discards the input crop's offset inside its slot. It is not a skeleton/foot tracker and does not preserve root motion. Frames with a different visible bottom, such as a trailing effect or a falling pose, may need manual anchors instead.

## Outputs

- `frame-001.png`, etc.: fixed-size transparent frames in input order.
- `atlas.png`: all frames in one row with no packing rotation or per-frame trim metadata.
- `preview.png`: labeled contact sheet on a checkerboard.
- `preview.gif`: looping checkerboard preview. GIF palette and timing are approximate; it may merge identical adjacent images while preserving their duration.
- `manifest.json`: original file name/SHA-256, source size, common scale, frame dimensions, source boxes, output placements and playback convention. It does not expose the source's absolute path.

The tool bounds input/output pixel counts and creates a new output directory exclusively. Input decoding and frame normalization happen before output creation. Files are written directly to avoid directory-renaming conflicts with Windows preview/indexing software. A write failure leaves partial output for inspection and exits with an error; `manifest.json` is written last, but a zero exit status is still required to declare success. Choose another new directory for a retry. The tool never recursively deletes, makes backups or alters existing game assets.

If the tool rejects the strip, use the reported reason to fix the input or change explicit options. Do not keep changing frame counts until one happens to fit; divisibility alone does not establish the correct animation layout.
