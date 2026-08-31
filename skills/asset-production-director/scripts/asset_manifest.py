"""Offline asset provenance and release-evidence checks. Python 3.10+."""
import argparse
import hashlib
import json
from pathlib import Path, PureWindowsPath
import re
import sys

KINDS = {'image', 'texture', 'model', 'animation', 'audio', 'map', 'font', 'ui', 'data'}

def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'), object_pairs_hook=unique_object)

def local_file(root, relative):
    if not isinstance(relative, str) or not relative or '\\' in relative:
        raise ValueError('Expected a nonempty project-relative path with / separators')
    parts = relative.split('/')
    if PureWindowsPath(relative).drive or any(x in ('', '.', '..') for x in parts) or ':' in relative:
        raise ValueError('Unsafe relative path: ' + relative)
    root = Path(root).resolve(strict=True)
    candidate = root.joinpath(*parts)
    for part in [candidate, *candidate.parents]:
        if part == root:
            break
        if part.is_symlink() or getattr(part, 'is_junction', lambda: False)():
            raise ValueError('Links are not asset inputs: ' + relative)
    resolved = candidate.resolve(strict=True)
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise ValueError('Not a regular file inside project: ' + relative)
    return resolved

def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def audit(root, data, release=False):
    errors, rows, seen = [], [], set()
    if not isinstance(data, dict) or type(data.get('schema_version')) is not int or data.get('schema_version') != 1 or not isinstance(data.get('assets'), list):
        raise ValueError('Expected schema_version=1 and assets array')
    if release and not data['assets']:
        errors.append('A release manifest must contain assets')
    paths = set()
    for index, asset in enumerate(data['assets']):
        label = f'assets[{index}]'
        try:
            if not isinstance(asset, dict):
                raise ValueError('Asset must be an object')
            aid = asset.get('id')
            if not isinstance(aid, str) or not re.fullmatch(r'[a-z0-9][a-z0-9._-]*', aid):
                raise ValueError('Invalid asset id')
            label = aid
            if aid in seen:
                raise ValueError('Duplicate asset id')
            seen.add(aid)
            if asset.get('kind') not in KINDS:
                raise ValueError('Unknown asset kind')
            path = local_file(root, asset.get('path'))
            path_key = str(path).casefold()
            if path_key in paths:
                raise ValueError('Duplicate asset path, including case-only duplicates')
            paths.add(path_key)
            actual = digest(path)
            if asset.get('sha256') != actual:
                raise ValueError('SHA-256 mismatch; review the changed file before updating its record')
            source = asset.get('source')
            if not isinstance(source, str) or not source.strip():
                raise ValueError('Missing original source URL or self-authored description')
            license_info = asset.get('license')
            if not isinstance(license_info, dict) or not isinstance(license_info.get('id'), str) or not license_info['id'].strip():
                raise ValueError('Missing license object/id; use UNKNOWN while unresolved')
            status = asset.get('status')
            if status not in ('draft', 'processed', 'verified'):
                raise ValueError('Invalid status')
            deps = asset.get('depends_on', [])
            if not isinstance(deps, list) or any(not isinstance(d, str) for d in deps):
                raise ValueError('depends_on must be an array of asset ids')
            if aid in deps:
                raise ValueError('Asset cannot depend on itself')
            if 'evidence' in asset and not isinstance(asset['evidence'], list):
                raise ValueError('evidence must be a list of local files')
            for evidence in asset.get('evidence', []):
                local_file(root, evidence)
            if release:
                if license_info['id'].upper() in ('UNKNOWN', 'PENDING', 'NOASSERTION') or license_info.get('reviewed') is not True:
                    raise ValueError('License review is incomplete')
                local_file(root, license_info.get('evidence'))
                if status != 'verified' or not asset.get('evidence'):
                    raise ValueError('Runtime verification evidence is required for release')
            budget = asset.get('max_bytes')
            if budget is not None and (type(budget) is not int or budget < 1):
                raise ValueError('max_bytes must be a positive integer')
            size = path.stat().st_size
            if budget is not None and size > budget:
                raise ValueError(f'File exceeds project budget: {size} > {budget}')
            rows.append({'id': aid, 'bytes': size, 'sha256': actual, 'status': status})
        except (ValueError, OSError, TypeError) as exc:
            errors.append(f'{label}: {exc}')
    for asset in data['assets']:
        if isinstance(asset, dict) and isinstance(asset.get('depends_on', []), list):
            for dependency in asset.get('depends_on', []):
                if isinstance(dependency, str) and dependency not in seen:
                    errors.append(f"{asset.get('id')}: missing dependency {dependency}")
    return {'ok': not errors, 'release': release, 'checked': rows, 'errors': errors,
            'limitation': 'Evidence existence and declared review are checked, not legal validity, rendered quality or complete project coverage.'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    check = sub.add_parser('audit')
    check.add_argument('--root', required=True)
    check.add_argument('--manifest', required=True)
    check.add_argument('--release', action='store_true')
    record = sub.add_parser('record')
    record.add_argument('--root', required=True)
    record.add_argument('--file', required=True)
    record.add_argument('--id', required=True)
    record.add_argument('--kind', required=True, choices=sorted(KINDS))
    record.add_argument('--source', required=True)
    record.add_argument('--license', default='UNKNOWN')
    args = parser.parse_args()
    try:
        if args.command == 'audit':
            result = audit(args.root, read_json(local_file(args.root, args.manifest)), args.release)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result['ok'] else 1
        path = local_file(args.root, args.file)
        print(json.dumps({'id': args.id, 'kind': args.kind, 'path': args.file, 'source': args.source,
                         'sha256': digest(path), 'license': {'id': args.license, 'reviewed': False},
                         'status': 'draft', 'depends_on': [], 'evidence': []}, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, TypeError) as exc:
        print(json.dumps({'ok': False, 'errors': [str(exc)]}, ensure_ascii=False))
        return 1

if __name__ == '__main__':
    sys.exit(main())
