#!/usr/bin/env python3
"""Package a locally built native Windows game for portable Italian play."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_NAME = 'Colobot-Italiano-Windows64'
PRIVATE_FILES = {'saves', 'screenshots', 'logs', 'colobot.json', 'colobot.ini', 'colobot.log'}


def collect_dlls(executable, dll_directory, system_directory, objdump):
    """Follow PE imports recursively; exclude Windows system DLLs."""
    local = {p.name.casefold(): p for p in executable.parent.glob('*.dll')}
    runtime = {p.name.casefold(): p for p in dll_directory.glob('*.dll')}
    pending = [executable]
    seen = set()
    result = {}
    env = dict(os.environ, LC_ALL='C')
    while pending:
        binary = pending.pop()
        output = subprocess.check_output([str(objdump), '-p', str(binary)],
                                         text=True, encoding='utf-8', errors='replace', env=env)
        if 'file format pei-x86-64' not in output:
            raise ValueError(f'Not a Windows 64-bit executable or DLL: {binary}')
        imports = re.findall(r'^\s*DLL Name:\s*(\S+)\s*$', output, re.M)
        # SDL_image and other libraries can load codecs at runtime instead of
        # listing them in the PE import table. Include embedded DLL names when
        # they resolve to an installed runtime, then follow their imports too.
        optional = [name.decode('ascii') for name in
                    re.findall(rb'[A-Za-z0-9_-]+\.dll', binary.read_bytes(), re.I)]
        optional = [name for name in optional if name.casefold() in local or name.casefold() in runtime]
        for name in imports + optional:
            key = name.casefold()
            if key in seen:
                continue
            seen.add(key)
            dependency = local.get(key) or runtime.get(key)
            if dependency is not None:
                result[key] = dependency
                pending.append(dependency)
            elif key.startswith(('api-ms-', 'ext-ms-')) or (system_directory / name).is_file():
                continue
            else:
                raise FileNotFoundError(f'Missing DLL imported by {binary.name}: {name}')
    return sorted(result.values(), key=lambda p: p.name.casefold())


def stage_game(install, destination):
    """Copy the installation and seed a fresh Italian profile."""
    for source in install.iterdir():
        if source.name.casefold() in PRIVATE_FILES or source.suffix.casefold() == '.log':
            continue
        target = destination / source.name
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)
    (destination / 'saves').mkdir()
    (destination / 'saves/colobot.json').write_text(
        json.dumps({'Language': {'Lang': 'it'}}, indent=2) + '\n', encoding='utf-8')
    launcher = ('@echo off\r\nsetlocal\r\npushd "%~dp0"\r\n'
                '"%~dp0colobot.exe"\r\nset "GAME_EXIT=%ERRORLEVEL%"\r\n'
                'popd\r\nexit /b %GAME_EXIT%\r\n')
    (destination / 'Gioca-in-italiano.cmd').write_bytes(launcher.encode('ascii'))


def package(install, output, engine_source, data_source, dll_directory, objdump):
    install, output = install.resolve(), output.resolve()
    checksum = output.with_suffix(output.suffix + '.sha256')
    if output.exists() or checksum.exists():
        raise FileExistsError(f'Choose a new output filename: {output}')
    if output.is_relative_to(install):
        raise ValueError('The ZIP must be outside the installed game directory.')
    for path in [install / 'colobot.exe', install / 'lang/it/LC_MESSAGES/colobot.mo',
                 engine_source / 'CMakeLists.txt', data_source / 'CMakeLists.txt']:
        if not path.is_file():
            raise FileNotFoundError(path)
    if not (install / 'data/help/I/cbot.txt').is_file():
        raise FileNotFoundError('Installed Italian game data is missing.')
    output.parent.mkdir(parents=True, exist_ok=True)
    system = Path(os.environ['SYSTEMROOT']) / 'System32'
    with tempfile.TemporaryDirectory(prefix='colobot-package-', dir=output.parent) as temporary:
        stage = Path(temporary) / PACKAGE_NAME
        stage.mkdir()
        print('Copying the installed game, excluding personal profiles...', flush=True)
        stage_game(install, stage)
        for music in (stage / 'data/music').glob('*.ogg'):
            with music.open('rb') as stream:
                if stream.read(4) != b'OggS':
                    raise ValueError(f'Invalid music download; download it again before packaging: {music.name}')
        dependencies = collect_dlls(stage / 'colobot.exe', dll_directory, system, objdump)
        for dependency in dependencies:
            target = stage / dependency.name
            if dependency.resolve() != target.resolve():
                shutil.copy2(dependency, target)
        # Resolve again using only the staged files, so PATH cannot hide missing DLLs.
        collect_dlls(stage / 'colobot.exe', stage, system, objdump)
        print(f'Included {len(dependencies)} runtime DLLs.', flush=True)

        sources = stage / 'sources'
        sources.mkdir()
        ignore = shutil.ignore_patterns('.git', '__pycache__', '*.pyc')
        for name, source in [('colobot', engine_source), ('colobot-data', data_source)]:
            print(f'Including corresponding {name} sources...', flush=True)
            shutil.copytree(source, sources / name, ignore=ignore)
        translation = sources / 'italian-translation'
        translation.mkdir()
        for name in ['translations', 'patches', 'tools', 'docs']:
            shutil.copytree(ROOT / name, translation / name, ignore=ignore)
        for name in ['LICENSE', 'README.md', 'upstream.json']:
            shutil.copy2(ROOT / name, translation / name)
        shutil.copy2(ROOT / 'LICENSE', stage / 'LICENSE')
        licenses = dll_directory.parent / 'share/licenses'
        if not licenses.is_dir():
            raise FileNotFoundError(f'MSYS2 license directory not found: {licenses}')
        shutil.copytree(licenses, stage / 'licenses/msys2')
        pacman = shutil.which('pacman')
        if pacman:
            packages = subprocess.check_output([pacman, '-Q'], text=True, encoding='utf-8')
            (stage / 'sources/msys2-packages.txt').write_text(packages, encoding='utf-8', newline='\n')
        (stage / 'sources/README.txt').write_text(
            'Game, data and Italian translation sources are included in this directory.\n'
            'Runtime DLL license texts are in ../licenses/msys2.\n'
            'MSYS2 dependency package sources and build recipes:\n'
            'https://repo.msys2.org/mingw/sources/\n'
            'https://github.com/msys2/MINGW-packages\n', encoding='utf-8')
        readme = ('Colobot: Gold Edition - Italiano - Windows 64 bit\n\n'
                  '1. Estrai tutta la cartella dallo ZIP.\n'
                  '2. Avvia Gioca-in-italiano.cmd. Non serve installare MSYS2.\n'
                  '3. Crea il tuo profilo e gioca: Italiano e gia selezionato.\n\n'
                  'I salvataggi di questa copia sono nella cartella saves.\n'
                  'Questo pacchetto non include salvataggi o impostazioni personali del creatore.\n\n'
                  'Build comunitaria di sviluppo di Colobot Gold, non una release ufficiale.\n'
                  'Traduzione: https://github.com/danielemorelli92/colobot_it\n'
                  'Sorgenti inclusi in sources; licenze in LICENSE e licenses.\n')
        if not (stage / 'data/music/Intro1.ogg').is_file():
            readme += '\nQuesta copia non include la musica; gli effetti sonori sono presenti.\n'
        (stage / 'LEGGIMI.txt').write_text(readme, encoding='utf-8', newline='\n')
        temporary_zip = Path(temporary) / output.name
        files = sorted(p for p in stage.rglob('*') if p.is_file())
        print(f'Compressing {len(files)} files; this may take a few minutes...', flush=True)
        with zipfile.ZipFile(temporary_zip, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for path in files:
                archive.write(path, path.relative_to(stage.parent).as_posix())
        with zipfile.ZipFile(temporary_zip) as archive:
            bad = archive.testzip()
            if bad:
                raise ValueError(f'ZIP integrity check failed: {bad}')
        with temporary_zip.open('rb') as stream:
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        temporary_zip.replace(output)
        checksum.write_text(f'{digest}  {output.name}\n', encoding='utf-8', newline='\n')
    print(f'Created: {output}\nSize: {output.stat().st_size / 1024**2:.1f} MiB\nSHA256: {digest}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', type=Path, default=ROOT / 'build/install')
    parser.add_argument('--output', type=Path, default=ROOT / f'build/{PACKAGE_NAME}.zip')
    parser.add_argument('--engine-source', type=Path, default=ROOT / 'build/prepared/colobot')
    parser.add_argument('--data-source', type=Path, default=ROOT / 'build/prepared/colobot-data')
    args = parser.parse_args()
    if sys.platform != 'win32':
        parser.error('Run this tool in the MSYS2 UCRT64 shell on Windows.')
    objdump = shutil.which('objdump')
    if objdump is None:
        parser.error('objdump is missing; use the MSYS2 UCRT64 shell used to build the game.')
    package(args.install, args.output, args.engine_source, args.data_source,
            Path(objdump).parent, Path(objdump))


if __name__ == '__main__':
    main()
