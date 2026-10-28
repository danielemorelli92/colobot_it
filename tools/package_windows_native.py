#!/usr/bin/env python3
"""Package a self-contained Windows test build and verify its DLLs without MSYS2 on PATH."""
import argparse
import collections
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--install', type=Path)
    p.add_argument('--runtime-bin', type=Path)
    p.add_argument('--engine-source', type=Path)
    p.add_argument('--data-source', type=Path)
    p.add_argument('--check-runtime', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    stage = args.output.resolve()
    if args.check_runtime:
        if os.name != 'nt':
            p.error('The portable runtime check must run on Windows')
        environment = os.environ.copy()
        windows = Path(environment.get('SystemRoot', r'C:\Windows'))
        environment['PATH'] = os.pathsep.join(map(str, [stage, windows/'System32', windows]))
        # Do not let inherited MSYS2 loader or locale settings hide packaging problems.
        for name in ['LANGUAGE', 'LANG', 'LC_ALL', 'LD_LIBRARY_PATH']:
            environment.pop(name, None)
        subprocess.run([str(args.check_runtime.resolve()), str(stage)], env=environment, cwd=stage, check=True)
        info_path = stage/'BUILD-INFO.json'
        info = json.loads(info_path.read_text(encoding='utf-8'))
        info['portable_runtime_check'] = 'passed on Windows with MSYS2 removed from PATH'
        info_path.write_text(json.dumps(info, indent=2)+'\n', encoding='utf-8')
        digests = {path.relative_to(stage).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                   for path in sorted(stage.rglob('*')) if path.is_file() and path.name != 'SHA256SUMS.json'}
        (stage/'SHA256SUMS.json').write_text(json.dumps(digests, indent=2)+'\n', encoding='utf-8')
        print(f'PASS portable package: {len(digests)} files verified')
        return

    if not all([args.install, args.runtime_bin, args.engine_source, args.data_source]):
        p.error('Packaging requires --install, --runtime-bin, --engine-source and --data-source')
    if stage.exists():
        p.error('Output directory already exists')
    shutil.copytree(args.install, stage)
    assert (stage/'colobot.exe').is_file(), 'colobot.exe missing'
    assert (stage/'lang/it/LC_MESSAGES/colobot.mo').is_file(), 'Italian MO missing'
    assert (stage/'data/help/I/cbot/searchall.txt').is_file(), 'Native Italian SatCom missing'
    music = list((stage/'data/music').glob('*.ogg'))
    assert music and all(path.stat().st_size > 64 for path in music), 'Optional music downloads are missing or empty'

    runtime = {path.name.lower(): path for path in args.runtime_bin.glob('*.dll')}
    available = {path.name.lower(): path for path in stage.glob('*.dll')}
    system = Path(os.environ.get('SystemRoot', r'C:\Windows'))/'System32'
    pending = collections.deque([*stage.glob('*.exe'), *stage.glob('*.dll')])
    inspected = set()
    while pending:
        binary = pending.popleft()
        if binary.name.lower() in inspected:
            continue
        inspected.add(binary.name.lower())
        report = subprocess.check_output(['objdump', '-p', str(binary)], text=True, errors='replace')
        assert 'pei-x86-64' in report, f'Not a 64-bit PE binary: {binary}'
        for name in re.findall(r'^\s*DLL Name:\s*(\S+)', report, re.M):
            key = name.lower()
            if key in available:
                pending.append(available[key])
            elif key in runtime:
                target = stage/runtime[key].name
                shutil.copyfile(runtime[key], target)
                available[key] = target
                pending.append(target)
            elif not key.startswith(('api-ms-', 'ext-ms-')) and not (system/name).is_file():
                raise RuntimeError(f'Missing dependency {name} imported by {binary.name}')

    # Portable saves keep the user's released-game profiles separate.
    (stage/'saves').mkdir(exist_ok=True)
    (stage/'saves/colobot.json').write_text(json.dumps({'Language': {'Lang': 'it'}}, indent=2)+'\n', encoding='utf-8')
    shutil.copyfile(ROOT/'LICENSE', stage/'LICENSE.txt')
    licenses = args.runtime_bin.parent/'share/licenses'
    if licenses.is_dir():
        shutil.copytree(licenses, stage/'licenses/third-party', dirs_exist_ok=True)
    shutil.copytree(args.engine_source, stage/'SOURCES/colobot', ignore=shutil.ignore_patterns('.git', '__pycache__'))
    shutil.copytree(args.data_source, stage/'SOURCES/colobot-data', ignore=shutil.ignore_patterns('.git', '__pycache__', '*.ogg'))
    (stage/'SOURCES').mkdir(exist_ok=True)
    shutil.copyfile(ROOT/'upstream.json', stage/'SOURCES/upstream.json')
    shutil.copyfile(ROOT/'.github/workflows/windows-native.yml', stage/'SOURCES/windows-native.yml')
    packages = ROOT/'build/msys2-packages.txt'
    if packages.is_file():
        shutil.copyfile(packages, stage/'SOURCES/msys2-packages.txt')
    (stage/'SOURCES/README.txt').write_text('''The Colobot and Colobot Data source trees used for this Windows build are included here.
Downloaded music is installed under ../data/music; its source music CMake file is included.
The Italian contribution is maintained at https://github.com/danielemorelli92/colobot_it
Exact upstream revisions are recorded in upstream.json and BUILD-INFO.json.
Build options: Windows UCRT64, C++20, Release, PORTABLE=ON, PORTABLE_SAVES=ON,
TESTS=ON, DESKTOP=OFF. See windows-native.yml for the complete build procedure.
Runtime DLLs come from MSYS2 UCRT64 packages listed in msys2-packages.txt.
Their licenses are in ../licenses/third-party; package sources and build recipes:
https://github.com/msys2/MINGW-packages and https://packages.msys2.org/
Colobot sources and the Italian contribution: GPL version 3 or later; see ../LICENSE.txt.
''', encoding='utf-8')
    info = {'upstream': json.loads((ROOT/'upstream.json').read_text()),
            'italian_commit': os.environ.get('GITHUB_SHA', 'local'),
            'platform': 'Windows 64 bit, UCRT64', 'portable_saves': True,
            'runtime_dlls': sorted(path.name for path in available.values()),
            'portable_runtime_check': 'pending'}
    (stage/'BUILD-INFO.json').write_text(json.dumps(info, indent=2)+'\n', encoding='utf-8')
    (stage/'LEGGIMI-WINDOWS.txt').write_text('''COLOBOT - PROVA NATIVA ITALIANA PER WINDOWS 64 BIT

1. Estrai TUTTO lo ZIP in una cartella nuova, diversa dal gioco attuale.
2. Avvia colobot.exe. La lingua iniziale e' Italiano.
3. In Opzioni > Gioco, controlla che sia selezionato Italiano.
4. Apri Missioni > Terra > Equipaggiamento e il SatCom.
5. Salva una partita di prova, chiudi il gioco e ricaricala.

Questa build di sviluppo usa i sorgenti dev con il supporto nativo italiano.
Configurazione e salvataggi sono nella sottocartella saves di questo pacchetto.
Conserva la cartella e non estrarre questo pacchetto sopra l'installazione esistente.
L'avvio e' diretto da colobot.exe: lo slot della lingua e' Italiano.
Per segnalare un problema indica cosa hai fatto, il messaggio e uno screenshot.
I log sono nella cartella saves. BUILD-INFO.json identifica i sorgenti della build.

Questa e' una compilazione di prova della comunita', non una release ufficiale.
Sorgenti e licenza sono inclusi in SOURCES/ e LICENSE.txt.
''', encoding='utf-8')
    print(f'Packaged Windows build with {len(available)} runtime DLLs')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        if os.environ.get('GITHUB_ACTIONS') == 'true':
            print('::error::'+str(error).replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A'))
        raise
