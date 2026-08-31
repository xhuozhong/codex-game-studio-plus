#!/usr/bin/env python3
"""Synthetic asset behavior tests. Requires Python 3.10+ and Pillow 10–12.

From a checkout: python tests/test_assets.py --scratch-parent /existing/scratch
Without --scratch-parent, a new evidence directory is created in system temp.
No source assets, repository files or existing output directories are modified.
Evidence is retained on both success and failure; this test never deletes it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import traceback

try:
    from PIL import Image, ImageDraw
except ImportError:
    raise SystemExit("Pillow is required. Install the sprite skill's requirements.txt in your chosen environment.")

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
SPRITE = SKILLS / "sprite-animation-pipeline"
GLB = SKILLS / "web-3d-asset-optimizer"


def call(script, *args, ok=True):
    environment = os.environ.copy()
    environment["PYTHONUTF8"] = "1"
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    process = subprocess.run(
        [sys.executable, str(script), *map(str, args)], capture_output=True,
        text=True, encoding="utf-8", errors="replace", timeout=60, env=environment,
    )
    expected = 0 if ok else 2
    assert process.returncode == expected, (process.args, process.returncode, process.stdout, process.stderr)
    return json.loads(process.stdout) if ok else process.stderr


def run_sprite(source, out, *, frames=4, width=32, height=40, extra=(), ok=True):
    return call(SPRITE / "scripts/sprite_strip.py", "--input", source, "--frames", frames,
                "--frame-width", width, "--frame-height", height, "--out-dir", out, *extra, ok=ok)


def check_assets(scratch: Path, passed: list[str]) -> None:
    strip = Image.new("RGBA", (320, 80))
    draw = ImageDraw.Draw(strip)
    sizes = [(20, 30), (30, 50), (10, 60), (40, 40)]
    colors = [(220, 20, 60, 255), (20, 200, 80, 255), (30, 80, 230, 255), (240, 180, 30, 255)]
    for i, ((w, h), color) in enumerate(zip(sizes, colors)):
        x, y = i * 80 + 7 + i, 4 + i
        draw.rectangle((x, y, x + w - 1, y + h - 1), fill=color)
    raw = scratch / "raw.png"
    strip.save(raw)
    before_hash = hashlib.sha256(raw.read_bytes()).hexdigest()
    out = scratch / "normalized"
    result = run_sprite(raw, out)
    assert result["common_scale"] == 0.6
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["source_sha256"] == before_hash
    assert manifest["source_file"] == "raw.png"
    assert str(scratch) not in (out / "manifest.json").read_text(encoding="utf-8")
    atlas = Image.open(out / "atlas.png")
    assert atlas.size == (128, 40)
    for i, (w, h) in enumerate(sizes):
        frame = Image.open(out / f"frame-{i+1:03}.png")
        assert frame.mode == "RGBA" and frame.size == (32, 40)
        box = frame.getchannel("A").getbbox()
        expected_w, expected_h = round(w * .6), round(h * .6)
        assert box == ((32 - expected_w) // 2, 38 - expected_h, (32 - expected_w) // 2 + expected_w, 38)
        assert frame.tobytes() == atlas.crop((i * 32, 0, (i + 1) * 32, 40)).tobytes()
        assert set(frame.getpixel((x, y)) for y in range(frame.height) for x in range(frame.width)) <= {(0, 0, 0, 0), colors[i]}
    assert Image.open(out / "preview.png").size == (128, 60)
    gif = Image.open(out / "preview.gif")
    assert gif.n_frames == 4
    durations = []
    for i in range(gif.n_frames):
        gif.seek(i)
        durations.append(gif.info["duration"])
    assert sum(durations) == 400
    assert hashlib.sha256(raw.read_bytes()).hexdigest() == before_hash
    passed.append("4-frame strip: common scale, fixed frame size, bottom-center baseline, palette, atlas, previews, source hash")

    sentinel = out / "keep.txt"
    sentinel.write_text("preserve", encoding="utf-8")
    run_sprite(raw, out, ok=False)
    assert sentinel.read_text(encoding="utf-8") == "preserve"
    assert "divisible" in run_sprite(raw, scratch / "bad-count", frames=3, ok=False)
    assert not (scratch / "bad-count").exists()
    run_sprite(raw, scratch / "bad-padding", width=4, height=4, ok=False)
    assert not (scratch / "bad-padding").exists()
    passed.append("Existing output, wrong slot count and impossible padding refuse without replacing outputs")

    empty = Image.new("RGBA", (40, 20))
    ImageDraw.Draw(empty).rectangle((2, 2, 15, 15), fill=(100, 90, 80, 255))
    empty.save(scratch / "one-empty.png")
    run_sprite(scratch / "one-empty.png", scratch / "empty-refused", frames=2, ok=False)
    run_sprite(scratch / "one-empty.png", scratch / "empty-kept", frames=2, extra=("--allow-empty",))
    blank = Image.open(scratch / "empty-kept/frame-002.png")
    assert blank.getchannel("A").getbbox() is None
    Image.new("RGB", (40, 20), "white").save(scratch / "opaque.png")
    run_sprite(scratch / "opaque.png", scratch / "opaque-refused", frames=2, ok=False)
    passed.append("Intentional blank frames preserved only with flag; opaque input rejected")

    semi = Image.new("RGBA", (20, 12))
    ImageDraw.Draw(semi).rectangle((4, 1, 15, 8), fill=(160, 80, 40, 127))
    semi.save(scratch / "semi.png")
    result = run_sprite(scratch / "semi.png", scratch / "semi-out", frames=1, width=32, height=32)
    assert result["common_scale"] == 1.0
    assert Image.open(scratch / "semi-out/frame-001.png").getchannel("A").getextrema() == (0, 127)
    result = run_sprite(scratch / "semi.png", scratch / "upscale", frames=1, width=32, height=32,
                        extra=("--allow-upscale", "--resample", "lanczos"))
    assert result["common_scale"] > 1
    assert not list(scratch.glob(".sprite-strip-*"))
    passed.append("Semi-transparent alpha preserved; no default upscaling; explicit smooth upscale succeeds; no staging leftovers")

    document = {"asset": {"version": "2.0"}, "scenes": [{"nodes": [0]}], "nodes": [{"mesh": 0}],
                "meshes": [{"primitives": [{"attributes": {"POSITION": 0}}]}],
                "accessors": [{"bufferView": 0, "componentType": 5126, "count": 3, "type": "VEC3", "min": [0, 0, 0], "max": [1, 1, 0]}],
                "bufferViews": [{"buffer": 0, "byteOffset": 0, "byteLength": 36}], "buffers": [{"byteLength": 36}]}
    payload = json.dumps(document).encode()
    payload += b" " * (-len(payload) % 4)
    binary = struct.pack("<9f", 0, 0, 0, 1, 0, 0, 0, 1, 0)
    glb_bytes = struct.pack("<4sII", b"glTF", 2, 12 + 8 + len(payload) + 8 + len(binary))
    glb_bytes += struct.pack("<II", len(payload), 0x4E4F534A) + payload
    glb_bytes += struct.pack("<II", len(binary), 0x004E4942) + binary
    model = scratch / "triangle.glb"
    model.write_bytes(glb_bytes)
    report = call(GLB / "scripts/glb_inventory.py", "--input", model)
    assert report["counts"]["meshes"] == 1 and report["mesh_primitive_definitions"] == 1
    assert report["sha256"] == hashlib.sha256(glb_bytes).hexdigest()
    assert not report["external_uris"]
    assert model.read_bytes() == glb_bytes
    passed.append("Synthetic GLB triangle inventoried without modifying bytes; counts and SHA-256 match")

    external = {"asset": {"version": "2.0"}, "buffers": [{"byteLength": 36, "uri": "does-not-exist.bin"}],
                "images": [{"uri": "https://example.invalid/never-fetched.png"}, {"uri": "data:image/png;base64,AA=="}],
                "extensionsRequired": ["scratch_example"]}
    gltf = scratch / "external.gltf"
    gltf.write_text(json.dumps(external), encoding="utf-8")
    report = call(GLB / "scripts/glb_inventory.py", "--input", gltf)
    assert len(report["external_uris"]) == 2 and report["embedded_data_uri_count"] == 1
    assert report["extensionsRequired"] == ["scratch_example"]
    (scratch / "broken.glb").write_bytes(glb_bytes[:-4])
    call(GLB / "scripts/glb_inventory.py", "--input", scratch / "broken.glb", ok=False)
    (scratch / "bad-root.gltf").write_text("[]", encoding="utf-8")
    call(GLB / "scripts/glb_inventory.py", "--input", scratch / "bad-root.gltf", ok=False)
    passed.append("Missing/remote URI metadata listed without reads; malformed GLB and non-object JSON refused")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--scratch-parent", type=Path,
                        help="Existing directory outside the repository; defaults to system temp")
    args = parser.parse_args()
    if not __debug__:
        parser.error("Do not run tests with Python -O; assertions must stay enabled")
    parent = args.scratch_parent if args.scratch_parent is not None else Path(tempfile.gettempdir())
    try:
        parent = parent.expanduser().resolve(strict=True)
    except OSError as exc:
        parser.error(str(exc))
    if not parent.is_dir():
        parser.error("--scratch-parent must name an existing directory")
    if parent == ROOT or ROOT in parent.parents:
        parser.error("The evidence directory must be outside the repository")
    scratch = Path(tempfile.mkdtemp(prefix="assets-test-", dir=parent))
    print(f"Evidence retained at: {scratch}", file=sys.stderr, flush=True)
    passed: list[str] = []
    summary = {
        "test_directory": str(scratch), "python": sys.version.split()[0],
        "pillow": Image.__version__, "passed": passed,
        "not_tested": ["Image-generation service", "Real game import/playback",
                       "Blender/glTF Transform conversion", "Browser GLB render/decode performance"],
    }
    try:
        check_assets(scratch, passed)
        summary["ok"] = True
    except Exception as exc:
        summary["ok"] = False
        summary["error"] = str(exc)
        traceback.print_exc()
    (scratch / "test-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
