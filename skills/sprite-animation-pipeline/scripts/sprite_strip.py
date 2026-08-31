#!/usr/bin/env python3
"""Normalize equal-slot transparent PNG strips; original project helper (MIT)."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

try:
    from PIL import Image, ImageDraw
except ImportError:
    raise SystemExit("Pillow is required. Install this skill's requirements.txt in your chosen Python environment.")

MAX_PIXELS = 32_000_000


def checker(size: tuple[int, int]) -> Image.Image:
    image = Image.new("RGB", size, (226, 229, 233))
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], 8):
        for x in range(0, size[0], 8):
            if (x // 8 + y // 8) % 2:
                draw.rectangle((x, y, x + 7, y + 7), fill=(184, 190, 200))
    return image


def normalize(args: argparse.Namespace) -> dict:
    if not 1 <= args.frames <= 256:
        raise ValueError("--frames must be between 1 and 256")
    if not all(1 <= n <= 2048 for n in (args.frame_width, args.frame_height)):
        raise ValueError("Frame dimensions must be between 1 and 2048")
    if not 1 <= args.fps <= 60:
        raise ValueError("--fps must be between 1 and 60")
    if args.padding < 0 or 2 * args.padding >= min(args.frame_width, args.frame_height):
        raise ValueError("Padding must leave at least one usable pixel in each dimension")
    if args.frames * args.frame_width * args.frame_height > MAX_PIXELS:
        raise ValueError("Output atlas exceeds the 32 million pixel limit")

    source = Path(args.input).expanduser().resolve(strict=True)
    destination = Path(args.out_dir).expanduser().absolute()
    if destination.exists() or destination.is_symlink():
        raise ValueError("Output path already exists; choose a new directory")
    if not destination.parent.is_dir():
        raise ValueError("Output parent directory must already exist")
    digest = hashlib.sha256()
    with source.open("rb") as source_stream:
        for block in iter(lambda: source_stream.read(1024 * 1024), b""):
            digest.update(block)
    source_sha = digest.hexdigest()
    with Image.open(source) as opened:
        if opened.format != "PNG" or getattr(opened, "n_frames", 1) != 1:
            raise ValueError("Input must be a single, non-animated PNG")
        if opened.width * opened.height > MAX_PIXELS:
            raise ValueError("Input exceeds the 32 million pixel limit")
        if "A" not in opened.getbands() and "transparency" not in opened.info:
            raise ValueError("Input needs existing alpha transparency; no background removal is performed")
        strip = opened.convert("RGBA")
    if strip.getchannel("A").getextrema()[0] == 255:
        raise ValueError("Input is completely opaque; provide a transparent strip")
    if strip.width % args.frames:
        raise ValueError("Input width is not divisible by the specified slot count")
    slot_width = strip.width // args.frames
    boxes, crops = [], []
    for i in range(args.frames):
        slot = strip.crop((i * slot_width, 0, (i + 1) * slot_width, strip.height))
        box = slot.getchannel("A").getbbox()
        if box is None and not args.allow_empty:
            raise ValueError(f"Slot {i + 1} is empty; use --allow-empty only for intentional blank frames")
        boxes.append(box)
        crops.append(slot.crop(box) if box else None)
    visible = [c for c in crops if c is not None]
    if not visible:
        raise ValueError("At least one slot must contain visible pixels")
    scale = min((args.frame_width - 2 * args.padding) / max(c.width for c in visible),
                (args.frame_height - 2 * args.padding) / max(c.height for c in visible))
    if not args.allow_upscale:
        scale = min(scale, 1.0)
    resample = Image.Resampling.NEAREST if args.resample == "nearest" else Image.Resampling.LANCZOS
    frame_size = (args.frame_width, args.frame_height)
    frames, records = [], []
    for i, crop in enumerate(crops):
        frame = Image.new("RGBA", frame_size)
        placement = None
        if crop is not None:
            width = max(1, min(args.frame_width - 2 * args.padding, round(crop.width * scale)))
            height = max(1, min(args.frame_height - 2 * args.padding, round(crop.height * scale)))
            resized = crop.resize((width, height), resample)
            x = (args.frame_width - width) // 2
            y = args.frame_height - args.padding - height
            frame.alpha_composite(resized, (x, y))
            placement = [x, y, width, height]
        frames.append(frame)
        records.append({"file": f"frame-{i + 1:03d}.png", "source_box_in_slot": boxes[i],
                        "placement_xywh": placement, "empty": crop is None})
    manifest = {
        "schema_version": 1, "source_file": source.name, "source_sha256": source_sha,
        "source_size": list(strip.size), "source_slot_width": slot_width,
        "frame_count": args.frames, "frame_size": list(frame_size), "common_scale": scale,
        "anchor": "visible-bottom-center", "bottom_exclusive": args.frame_height - args.padding,
        "padding": args.padding, "resample": args.resample, "fps": args.fps,
        "gif_frame_duration_ms": max(10, round(100 / args.fps) * 10),
        "atlas": {"file": "atlas.png", "columns": args.frames, "rows": 1}, "frames": records,
        "limitations": ["No background removal or pose tracking", "Input slot offsets are discarded",
                        "GIF preview is opaque and timing is rounded to GIF centiseconds"],
    }
    # Exclusive creation prevents overwrite and avoids Windows directory-rename
    # failures when preview files are briefly held by background indexers.
    destination.mkdir()
    stage = destination
    try:
        atlas = Image.new("RGBA", (args.frame_width * args.frames, args.frame_height))
        columns = min(8, args.frames)
        rows = math.ceil(args.frames / columns)
        preview = checker((columns * args.frame_width, rows * (args.frame_height + 20)))
        draw = ImageDraw.Draw(preview)
        animated = []
        for i, frame in enumerate(frames):
            frame.save(stage / records[i]["file"])
            atlas.paste(frame, (i * args.frame_width, 0))
            x, y = i % columns * args.frame_width, i // columns * (args.frame_height + 20)
            preview.paste(frame, (x, y), frame.getchannel("A"))
            draw.text((x + 2, y + args.frame_height + 3), str(i + 1), fill=(20, 25, 35))
            animated_frame = checker(frame_size)
            animated_frame.paste(frame, (0, 0), frame.getchannel("A"))
            animated.append(animated_frame)
        atlas.save(stage / "atlas.png")
        preview.save(stage / "preview.png")
        animated[0].save(stage / "preview.gif", save_all=True, append_images=animated[1:],
                         duration=manifest["gif_frame_duration_ms"], loop=0, disposal=2)
        (stage / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    except OSError as exc:
        raise OSError(f"Output write failed; partial files remain in {destination}: {exc}") from exc
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--frames", required=True, type=int)
    parser.add_argument("--frame-width", required=True, type=int)
    parser.add_argument("--frame-height", required=True, type=int)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--padding", type=int, default=2)
    parser.add_argument("--fps", type=int, default=10)
    parser.add_argument("--resample", choices=("nearest", "lanczos"), default="nearest")
    parser.add_argument("--allow-upscale", action="store_true")
    parser.add_argument("--allow-empty", action="store_true")
    try:
        result = normalize(parser.parse_args())
    except (OSError, ValueError, Image.DecompressionBombError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"ok": True, "frame_count": result["frame_count"],
                      "frame_size": result["frame_size"], "common_scale": result["common_scale"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
