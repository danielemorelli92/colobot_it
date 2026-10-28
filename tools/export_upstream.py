#!/usr/bin/env python3
"""Export two standalone patches for the pinned official dev repositories."""
import argparse
import difflib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PINS = json.loads((ROOT/'upstream.json').read_text())

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--engine', type=Path, required=True)
p.add_argument('--data', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
a.output.mkdir(parents=True, exist_ok=False)
for name, repository in [('colobot', a.engine), ('colobot-data', a.data)]:
    pin = PINS[name]
    patch = (ROOT/'patches/colobot-dev-italian.patch').read_text() if name == 'colobot' else ''
    tracked = set(subprocess.check_output(['git', '-C', str(repository), 'ls-tree', '-r', '--name-only', pin], text=True).splitlines())
    catalogs = sorted(path for path in (ROOT/'translations'/name).rglob('*') if path.is_file())
    for catalog in catalogs:
        relative = catalog.relative_to(ROOT/'translations'/name).as_posix()
        before = subprocess.check_output(['git', '-C', str(repository), 'show', f'{pin}:{relative}'], text=True) if relative in tracked else ''
        patch += ''.join(difflib.unified_diff(before.splitlines(keepends=True), catalog.read_text().splitlines(keepends=True),
                                             fromfile=f'a/{relative}' if relative in tracked else '/dev/null', tofile=f'b/{relative}'))
    dest = a.output/f'{name}-italian.patch'
    dest.write_text(patch)
    print(f'{dest}: {len(catalogs)} translation/template files, base {pin}')
