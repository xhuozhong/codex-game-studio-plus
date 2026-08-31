"""Offline structural validation; no third-party dependency or network access."""
from pathlib import Path
import json
import re

def validate(root):
    manifest = json.loads((root / 'studio-manifest.json').read_text(encoding='utf-8'))
    assert manifest['schema_version'] == 1 and manifest['package'] == 'codex-game-studio-plus'
    assert re.fullmatch(r'\d+\.\d+\.\d+', manifest['version'])
    expected = manifest['skills']
    assert isinstance(expected,list) and expected and len(set(expected)) == len(expected), 'Duplicate/empty Skill list'
    assert all(isinstance(n,str) and len(n)<=64 and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',n) for n in expected), 'Unsafe Skill name'
    assert manifest['entrypoint'] == 'game-studio-director' and manifest['entrypoint'] in expected
    assert (root/'VERSION').read_text().strip() == manifest['version']
    entries = list((root/'skills').iterdir())
    assert all(p.is_dir() and not p.is_symlink() for p in entries), 'Unexpected skills entry'
    assert {p.name for p in entries} == set(expected), 'Skill folders differ from manifest'
    for name in expected:
        folder = root/'skills'/name
        text = (folder/'SKILL.md').read_text(encoding='utf-8')
        front = re.match(r'\A---\n(.*?)\n---\n',text,re.S)
        assert front, name+' frontmatter'
        assert re.search(r'^name: '+re.escape(name)+r'$',front[1],re.M), name+' name'
        assert re.search(r'^description: \S.+$',front[1],re.M), name+' description'
        ui = (folder/'agents/openai.yaml').read_text(encoding='utf-8')
        assert re.search(r'^interface:$',ui,re.M) and re.search(r'^  short_description: ".+"$',ui,re.M), name+' UI'
    for item in ['README.md','NOTICE.md','VERSION','INSTALL_WINDOWS.cmd','REPAIR_WINDOWS.cmd','UNINSTALL_WINDOWS.cmd']:
        assert (root/item).is_file(), 'Missing '+item
    return len(expected)

if __name__ == '__main__':
    count = validate(Path(__file__).resolve().parents[1])
    print(f'PASS: {count} Skills; manifest, frontmatter subset, UI and required files')
