"""Structural checks for finite Tiled JSON and LDtk levels; no engine execution."""
import argparse
import json
import math
from pathlib import Path, PureWindowsPath
import sys

def source_file(root, base, relative):
    if not isinstance(relative, str) or not relative or '\\' in relative or ':' in relative or PureWindowsPath(relative).is_absolute():
        raise ValueError('Expected relative resource path')
    target = base / relative
    for part in [target, *target.parents]:
        if part == root:
            break
        if part.is_symlink() or getattr(part, 'is_junction', lambda: False)():
            raise ValueError('Linked resource not supported: ' + relative)
    target = target.resolve(strict=True)
    if not target.is_relative_to(root) or not target.is_file():
        raise ValueError('Resource escapes project: ' + relative)
    return target

def layers(items):
    for layer in items:
        yield layer
        yield from layers(layer.get('layers', []))

def positive(value, label):
    if type(value) is not int or value < 1:
        raise ValueError(label + ' must be a positive integer')
    return value

def inspect(root, file, spawn_layer=None, collision_layer=None):
    root = Path(root).resolve(strict=True)
    path = source_file(root, root, file)
    data = json.loads(path.read_text(encoding='utf-8-sig'))
    errors, refs, objects = [], [], []
    def reference(base, rel):
        refs.append(source_file(root, base, rel).relative_to(root).as_posix())
    try:
        if data.get('type') == 'map':
            if data.get('infinite'):
                raise ValueError('Infinite/chunked Tiled maps are not supported by this checker')
            w, h = positive(data.get('width'), 'width'), positive(data.get('height'), 'height')
            tw, th = positive(data.get('tilewidth'), 'tilewidth'), positive(data.get('tileheight'), 'tileheight')
            ranges, sparse_gids = [], set()
            for tileset in data.get('tilesets', []):
                spec, base = tileset, path.parent
                if 'source' in tileset:
                    ref = source_file(root, base, tileset['source'])
                    refs.append(ref.relative_to(root).as_posix())
                    if ref.suffix.lower() not in ('.json', '.tsj'):
                        raise ValueError('Export external tilesets as JSON/TSJ; TSX is not parsed')
                    spec, base = json.loads(ref.read_text(encoding='utf-8-sig')), ref.parent
                if spec.get('image'):
                    reference(base, spec['image'])
                for tile in spec.get('tiles', []):
                    if tile.get('image'):
                        reference(base, tile['image'])
                start = positive(tileset.get('firstgid'), 'firstgid')
                count = positive(spec.get('tilecount'), 'tilecount')
                if spec.get('columns') == 0:
                    for tile in spec.get('tiles', []):
                        tid = tile.get('id')
                        if type(tid) is not int or tid < 0:
                            raise ValueError('Invalid image-collection tile id')
                        sparse_gids.add(start + tid)
                else:
                    ranges.append((start, start + count))
            all_layers = list(layers(data.get('layers', [])))
            ids = set()
            for layer in all_layers:
                if layer.get('type') == 'imagelayer' and layer.get('image'):
                    reference(path.parent, layer['image'])
                if layer.get('type') == 'tilelayer':
                    cells = layer.get('data')
                    lw, lh = positive(layer.get('width'), 'layer width'), positive(layer.get('height'), 'layer height')
                    if not isinstance(cells, list) or len(cells) != lw * lh:
                        raise ValueError('Expected uncompressed numeric tile array: ' + str(layer.get('name')))
                    for gid in cells:
                        if type(gid) is not int or not 0 <= gid <= 0xffffffff:
                            raise ValueError('Invalid tile GID')
                        actual = gid & 0x0fffffff
                        if actual and actual not in sparse_gids and not any(start <= actual < end for start, end in ranges):
                            raise ValueError('Tile GID is outside declared tilesets: ' + str(actual))
                for obj in layer.get('objects', []):
                    oid = obj.get('id')
                    if type(oid) is not int or oid < 1 or oid in ids:
                        raise ValueError('Missing/duplicate object id')
                    ids.add(oid)
                    if any(type(obj.get(k)) not in (int, float) or not math.isfinite(obj[k]) for k in ('x', 'y')):
                        raise ValueError('Object position is not finite')
                    objects.append({'id': oid, 'layer': layer.get('name')})
            if bool(spawn_layer) != bool(collision_layer):
                raise ValueError('Provide both --spawn-layer and --collision-layer')
            if spawn_layer:
                spawns = [l for l in all_layers if l.get('name') == spawn_layer]
                solids = [l for l in all_layers if l.get('name') == collision_layer]
                if len(spawns) != 1 or len(solids) != 1:
                    raise ValueError('Spawn and collision layers must each be unique')
                solid = solids[0]
                if solid.get('type') != 'tilelayer' or (solid['width'], solid['height']) != (w, h):
                    raise ValueError('Collision layer must match finite map dimensions')
                # This optional point check intentionally rejects transformed/grouped layers.
                if any(l.get('type') == 'group' or any(l.get(k, 0) for k in ('offsetx', 'offsety', 'x', 'y')) for l in all_layers):
                    raise ValueError('Point spawn checks require ungrouped, unshifted layers')
                if not spawns[0].get('objects'):
                    raise ValueError('No point spawns found')
                for obj in spawns[0]['objects']:
                    if obj.get('point') is not True:
                        raise ValueError('Spawn checker expects Tiled point objects')
                    x, y = math.floor(obj['x'] / tw), math.floor(obj['y'] / th)
                    if not (0 <= x < w and 0 <= y < h) or solid['data'][y * w + x] & 0x0fffffff:
                        raise ValueError('Spawn outside map or on a nonempty collision tile')
            kind = 'tiled-json'
        elif 'defs' in data and 'levels' in data:
            if spawn_layer or collision_layer:
                raise ValueError('Tiled point spawn options do not apply to LDtk')
            for tileset in data['defs'].get('tilesets', []):
                if tileset.get('relPath'):
                    reference(path.parent, tileset['relPath'])
            level_list = list(data['levels'])
            for world in data.get('worlds', []):
                level_list.extend(world.get('levels', []))
            ids = set()
            for level in level_list:
                if level.get('externalRelPath'):
                    external = source_file(root, path.parent, level['externalRelPath'])
                    refs.append(external.relative_to(root).as_posix())
                    level = json.loads(external.read_text(encoding='utf-8-sig'))
                if level.get('layerInstances') is None:
                    raise ValueError('Missing embedded or external level layers')
                for layer in level['layerInstances']:
                    grid = layer.get('intGridCsv', [])
                    if grid and len(grid) != layer['__cWid'] * layer['__cHei']:
                        raise ValueError('LDtk IntGrid dimensions differ from cell count')
                    for obj in layer.get('entityInstances', []):
                        iid = obj.get('iid')
                        if not isinstance(iid, str) or not iid or iid in ids:
                            raise ValueError('Missing/duplicate entity iid')
                        ids.add(iid)
                        objects.append({'id': iid, 'layer': layer.get('__identifier')})
            kind = 'ldtk'
        else:
            raise ValueError('Expected Tiled JSON map or LDtk project')
    except (ValueError, OSError, KeyError, TypeError, AttributeError) as exc:
        errors.append(str(exc))
        kind = 'invalid-or-unsupported'
    return {'ok': not errors, 'format': kind, 'references': refs, 'objects': objects, 'errors': errors,
            'limitation': 'Structural subset only; no pathfinding, shape collision, LDtk EntityRef resolution or engine import proof.'}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', required=True)
    p.add_argument('--map', required=True)
    p.add_argument('--spawn-layer')
    p.add_argument('--collision-layer')
    a = p.parse_args()
    try:
        result = inspect(a.root, a.map, a.spawn_layer, a.collision_layer)
    except (ValueError, OSError, TypeError, KeyError, AttributeError) as exc:
        result = {'ok': False, 'errors': [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['ok'] else 1

if __name__ == '__main__':
    sys.exit(main())
