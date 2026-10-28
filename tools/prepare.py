#!/usr/bin/env python3
"""Prepare isolated, pinned upstream source trees with the Italian overlay."""
import argparse
from pathlib import Path
import subprocess
import tarfile
import io
import shutil
import json

ROOT = Path(__file__).resolve().parents[1]
PINS = json.loads((ROOT/'upstream.json').read_text())
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--engine', type=Path, required=True)
p.add_argument('--data', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
# Refuse to overwrite any existing files, including another prepared tree.
a.output.mkdir(parents=True, exist_ok=False)
for name, source in [('colobot', a.engine), ('colobot-data', a.data)]:
    dest = a.output / name
    dest.mkdir()
    blob = subprocess.check_output(['git', '-C', str(source), 'archive', PINS[name]])
    with tarfile.open(fileobj=io.BytesIO(blob)) as archive:
        archive.extractall(dest, filter='data')
    for po in (ROOT / 'translations' / name).rglob('*'):
        if not po.is_file():
            continue
        target = dest / po.relative_to(ROOT / 'translations' / name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(po, target)
subprocess.run(['git', 'apply', '--check', str(ROOT/'patches/colobot-dev-italian.patch')], cwd=a.output/'colobot', check=True)
subprocess.run(['git', 'apply', str(ROOT/'patches/colobot-dev-italian.patch')], cwd=a.output/'colobot', check=True)
print('Prepared', a.output.resolve())
