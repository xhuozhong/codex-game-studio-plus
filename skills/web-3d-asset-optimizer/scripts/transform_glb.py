"""Run a supplied, already installed glTF Transform CLI on a new GLB candidate."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

def check_links(path):
    for item in [path, *path.parents]:
        if item.is_symlink() or getattr(item, 'is_junction', lambda: False)():
            raise ValueError('Symlinks/junctions are not supported: ' + str(item))

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def run(args):
    original, destination = Path(args.input).absolute(), Path(args.output).absolute()
    cli, node = Path(args.cli_js).resolve(strict=True), Path(args.node).resolve(strict=True)
    for path in (original, destination):
        check_links(path)
    if original.suffix.lower() != '.glb' or destination.suffix.lower() != '.glb':
        raise ValueError('Only self-contained GLB input/output is supported')
    if destination.exists() or not destination.parent.is_dir():
        raise ValueError('Output must be new and its parent directory must exist')
    if not cli.is_file() or not node.is_file() or not original.is_file():
        raise ValueError('Node, installed CLI JavaScript and input must exist')
    raw = original.read_bytes()
    if len(raw) < 20 or raw[:4] != b'glTF' or int.from_bytes(raw[4:8], 'little') != 2 or int.from_bytes(raw[8:12], 'little') != len(raw):
        raise ValueError('Invalid GLB v2 container')
    if raw[16:20] != b'JSON':
        raise ValueError('GLB first chunk must be JSON')
    meta = json.loads(raw[20:20 + int.from_bytes(raw[12:16], 'little')].decode('utf-8'))
    for entry in meta.get('buffers', []) + meta.get('images', []):
        if entry.get('uri') and not entry['uri'].startswith('data:'):
            raise ValueError('External URIs are not allowed; create a self-contained GLB first')
    if args.width < 1 or args.height < 1:
        raise ValueError('Resize dimensions must be positive')
    def invoke(parts):
        proc = subprocess.run([str(node), str(cli), *parts], shell=False, capture_output=True, text=True,
                              encoding='utf-8', errors='replace', timeout=args.timeout)
        if proc.returncode:
            raise ValueError('CLI failed: ' + (proc.stderr or proc.stdout)[-4000:])
        return proc.stdout.strip()
    version = invoke(['--version'])
    before = sha(original)
    with tempfile.TemporaryDirectory(prefix='studio-gltf-', dir=destination.parent) as temporary:
        if Path(temporary).resolve().parent != destination.parent.resolve():
            raise ValueError('Temporary output escaped its intended parent')
        candidate = Path(temporary) / 'candidate.glb'
        command = [args.operation, str(original), str(candidate)]
        if args.operation == 'resize':
            command.extend(['--width', str(args.width), '--height', str(args.height)])
        log = invoke(command)
        if not candidate.is_file() or candidate.stat().st_size < 20:
            raise ValueError('CLI did not produce a GLB candidate')
        validation = invoke(['validate', str(candidate), '--format', 'csv'])
        if before != sha(original):
            raise ValueError('Source changed during transformation; candidate not promoted')
        # Exclusive creation prevents overwriting a file created after preflight.
        with destination.open('xb') as stream, candidate.open('rb') as source:
            shutil.copyfileobj(source, stream)
        return {'ok': True, 'operation': args.operation, 'cli_version': version,
                'input_bytes': original.stat().st_size, 'output_bytes': destination.stat().st_size,
                'input_sha256': before, 'output_sha256': sha(destination), 'log': log[-2000:],
                'validator_log': validation[-2000:], 'runtime_verified': False,
                'validator_scope': 'Supported glTF features only',
                'unsupported_extension_reported': 'UNSUPPORTED_EXTENSION' in validation,
                'limitation': 'Candidate transformed and CLI-validated; visual, animation and runtime decoder tests remain required.'}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--node', required=True)
    p.add_argument('--cli-js', required=True)
    p.add_argument('--operation', choices=['dedup', 'resize', 'meshopt'], default='dedup')
    p.add_argument('--width', type=int, default=1024)
    p.add_argument('--height', type=int, default=1024)
    p.add_argument('--timeout', type=int, default=120)
    a = p.parse_args()
    try:
        if a.timeout < 1:
            raise ValueError('Timeout must be positive')
        result = run(a)
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        result = {'ok': False, 'errors': [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['ok'] else 1

if __name__ == '__main__':
    sys.exit(main())
