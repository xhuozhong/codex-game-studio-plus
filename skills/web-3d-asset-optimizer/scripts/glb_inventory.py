#!/usr/bin/env python3
"""Read glTF/GLB structural metadata without loading external URIs (MIT)."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys

MAX_JSON_BYTES = 16 * 1024 * 1024
JSON_CHUNK = 0x4E4F534A


def read_document(path: Path) -> dict:
    if path.suffix.lower() == ".gltf":
        if path.stat().st_size > MAX_JSON_BYTES:
            raise ValueError("glTF JSON exceeds the 16 MiB inventory limit")
        text = path.read_text(encoding="utf-8-sig")
    elif path.suffix.lower() == ".glb":
        file_size = path.stat().st_size
        with path.open("rb") as stream:
            header = stream.read(12)
            if len(header) != 12:
                raise ValueError("Truncated GLB header")
            magic, version, length = struct.unpack("<4sII", header)
            if magic != b"glTF" or version != 2 or length != file_size:
                raise ValueError("Expected GLB version 2 with a matching declared length")
            text = None
            chunk_index = 0
            while stream.tell() < length:
                chunk_header = stream.read(8)
                if len(chunk_header) != 8:
                    raise ValueError("Truncated GLB chunk header")
                size, kind = struct.unpack("<II", chunk_header)
                if size % 4 or stream.tell() + size > length:
                    raise ValueError("Invalid GLB chunk length/alignment")
                if chunk_index == 0 and kind != JSON_CHUNK:
                    raise ValueError("GLB first chunk must be JSON")
                if kind == JSON_CHUNK:
                    if text is not None or size > MAX_JSON_BYTES:
                        raise ValueError("Duplicate or oversized GLB JSON chunk")
                    text = stream.read(size).decode("utf-8").rstrip(" \t\r\n")
                else:
                    stream.seek(size, 1)
                chunk_index += 1
            if text is None:
                raise ValueError("GLB has no JSON chunk")
    else:
        raise ValueError("Input extension must be .glb or .gltf")
    document = json.loads(text)
    if not isinstance(document, dict):
        raise ValueError("glTF JSON root must be an object")
    asset = document.get("asset")
    if not isinstance(asset, dict) or asset.get("version") != "2.0":
        raise ValueError("Expected glTF asset.version 2.0")
    return document


def inventory(path: Path) -> dict:
    document = read_document(path)
    keys = ("scenes", "nodes", "meshes", "materials", "textures", "images", "animations", "skins", "buffers")
    for key in keys:
        items = document.get(key, [])
        if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
            raise ValueError(f"{key} must be an array of objects")
    external_uris = []
    embedded_data_uris = 0
    for key in ("buffers", "images"):
        for index, item in enumerate(document.get(key, [])):
            uri = item.get("uri")
            if uri is None:
                continue
            if not isinstance(uri, str):
                raise ValueError(f"{key}[{index}].uri must be a string")
            if uri.startswith("data:"):
                embedded_data_uris += 1
            else:
                external_uris.append({"kind": key, "index": index, "uri": uri})
    primitive_count = 0
    for mesh in document.get("meshes", []):
        primitives = mesh.get("primitives", [])
        if not isinstance(primitives, list):
            raise ValueError("mesh.primitives must be an array")
        primitive_count += len(primitives)
    extensions = {}
    for key in ("extensionsUsed", "extensionsRequired"):
        value = document.get(key, [])
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            raise ValueError(f"{key} must be an array of strings")
        extensions[key] = value
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return {"file": path.name, "bytes": path.stat().st_size, "sha256": digest.hexdigest(),
            "asset_version": "2.0", "counts": {key: len(document.get(key, [])) for key in keys},
            "mesh_primitive_definitions": primitive_count, **extensions,
            "external_uris": external_uris, "embedded_data_uri_count": embedded_data_uris,
            "limitations": ["Metadata inventory, not a glTF specification validator",
                            "External resources were not fetched or read",
                            "No rendering, texture decoding or runtime performance measurement",
                            "Primitive definition count is not a measured draw-call count"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    try:
        result = inventory(Path(args.input).expanduser().resolve(strict=True))
    except (OSError, ValueError, struct.error) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
