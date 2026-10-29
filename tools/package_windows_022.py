#!/usr/bin/env python3
"""Add native Italian to the original Windows 0.2.2 distribution layout."""
import argparse
import gettext
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import struct
import sys
import tempfile
import zipfile

from package_windows import write_zip

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_NAME = 'colobot-gold-0.2.2-alpha-win64-italiano'
ITALIAN = re.compile(rb'^(Title|Resume|ScriptName)\.I\s')
ENGLISH = re.compile(rb'^(Title|Resume|ScriptName)\.E\s')
SYSTEM_DLLS = {name.lower() for name in (
    'OPENGL32.dll', 'ole32.dll', 'KERNEL32.dll', 'USER32.dll', 'GDI32.dll',
    'SHELL32.dll', 'ADVAPI32.dll', 'WINMM.dll', 'IMM32.dll', 'OLEAUT32.dll',
    'VERSION.dll', 'SETUPAPI.dll', 'WS2_32.dll', 'CRYPT32.dll', 'COMDLG32.dll',
    'COMCTL32.dll', 'SHLWAPI.dll', 'WINHTTP.dll', 'WININET.dll', 'BCRYPT.dll',
    'NORMALIZ.dll', 'RPCRT4.dll', 'DINPUT8.dll', 'DXGI.dll', 'D3D11.dll',
    'UCRTBASE.dll', 'MSVCRT.dll', 'NTDLL.dll', 'WINTRUST.dll', 'DBGHELP.dll')}


def pe_imports(path):
    """Read normal PE32+ imports without requiring dumpbin or GNU tools."""
    data = path.read_bytes()
    try:
        pe = struct.unpack_from('<I', data, 0x3c)[0]
        if data[:2] != b'MZ' or data[pe:pe+4] != b'PE\0\0':
            raise ValueError('Missing PE signature')
        machine, count = struct.unpack_from('<HH', data, pe+4)
        optional_size = struct.unpack_from('<H', data, pe+20)[0]
        optional = pe+24
        if machine != 0x8664 or struct.unpack_from('<H', data, optional)[0] != 0x20b:
            raise ValueError('The executable is not Windows x64 PE32+')
        sections = [struct.unpack_from('<IIII', data, optional+optional_size+40*i+8)
                    for i in range(count)]

        def offset(rva):
            if rva < struct.unpack_from('<I', data, optional+60)[0]:
                return rva
            for size, address, raw_size, raw in sections:
                if address <= rva < address+max(size, raw_size):
                    return raw+rva-address
            raise ValueError(f'Invalid PE address: {rva:x}')

        address, size = struct.unpack_from('<II', data, optional+120)
        if not address or not size:
            raise ValueError('The executable has no import directory')
        imports = []
        for position in range(offset(address), offset(address)+size, 20):
            descriptor = struct.unpack_from('<5I', data, position)
            if not any(descriptor):
                break
            start = offset(descriptor[3])
            imports.append(data[start:data.index(b'\0', start)].decode('ascii'))
        if not imports:
            raise ValueError('Empty PE import directory')
        return imports
    except (struct.error, IndexError, UnicodeError) as error:
        raise ValueError(f'Invalid Windows executable: {path}') from error


def check_executable(path):
    imports = pe_imports(path)
    extra = [name for name in imports if name.lower() not in SYSTEM_DLLS
             and not name.lower().startswith(('api-ms-win-', 'ext-ms-win-'))]
    if extra:
        raise ValueError('This build needs additional runtime DLLs: ' + ', '.join(extra))
    data = path.read_bytes()
    for marker in (b'Italiano', b'it_IT.utf8', b'0.2.2-alpha'):
        if marker not in data:
            raise ValueError('Expected a native Italian 0.2.2 executable; missing ' + repr(marker))
    return imports


def manifest():
    names = (ROOT / 'tools/windows_022_manifest.txt').read_text(encoding='utf-8').splitlines()
    if len(names) != 4255 or len(set(names)) != len(names):
        raise ValueError('Invalid original distribution manifest')
    for name in names:
        path = PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts or '\\' in name:
            raise ValueError(f'Invalid manifest path: {name}')
    return set(names)


def merge_scene(original, translated):
    """Insert Italian lines before their English counterparts, preserving every original byte."""
    additions = {}
    for line in translated.splitlines():
        match = ITALIAN.match(line)
        if match:
            additions.setdefault(match[1], []).append(line)
    if not additions:
        raise ValueError('Missing Italian level title/summary')
    if any(ITALIAN.match(line) for line in original.splitlines()):
        raise ValueError('The original game already contains Italian level lines')
    newline = b'\r\n' if b'\r\n' in original else b'\n'
    merged = []
    for line in original.splitlines(keepends=True):
        match = ENGLISH.match(line)
        if match and match[1] in additions:
            merged.extend(value+newline for value in additions.pop(match[1]))
        merged.append(line)
    if additions:
        raise ValueError('Original level is missing an English title/summary counterpart')
    result = b''.join(merged)
    if b''.join(line for line in result.splitlines(keepends=True)
                if not ITALIAN.match(line)) != original:
        raise ValueError('Level merge changed non-Italian content')
    return result


def italian_files(names):
    additions = {'lang/it/LC_MESSAGES/colobot.mo'}
    for name in names:
        if name.startswith('data/help/E/'):
            additions.add(name.replace('data/help/E/', 'data/help/I/', 1))
        elif name.startswith('data/levels/') and name.endswith('.E.txt'):
            additions.add(name[:-6]+'.I.txt')
    if len(additions) != 453:
        raise ValueError('Unexpected Italian file inventory')
    return additions


def source_files(prepared, project, build_root, original, names):
    """Keep build sources, third-party sources and notices outside the playable game."""
    files = {}

    def add_tree(source, prefix):
        if not source.is_dir():
            return
        for path in sorted(source.rglob('*')):
            relative = path.relative_to(source)
            if path.is_file() and not path.is_symlink() and not any(
                    part in ('.git', '__pycache__') or part.endswith('.pyc') for part in relative.parts):
                files[prefix+'/'+relative.as_posix()] = path

    for name in ('colobot', 'colobot-data', 'translation'):
        if not (prepared / name).is_dir():
            raise FileNotFoundError(prepared / name)
        add_tree(prepared / name, name)
    add_tree(project / 'tools', 'build-tools')
    add_tree(project / 'build/release-022/overlay-ports', 'vcpkg-overlay-ports')
    add_tree(build_root / 'vcpkg/scripts', 'vcpkg-build-scripts')
    add_tree(build_root / 'vcpkg/triplets', 'vcpkg-triplets')
    add_tree(build_root / 'vcpkg/buildtrees/versioning', 'vcpkg-versioned-ports')
    for name in ('README.md', 'LICENSE'):
        files['italian-translation/'+name] = project / name
    for path, name in ((prepared / 'preparation.json', 'preparation.json'),
                       (build_root / 'engine/vcpkg_installed/vcpkg/status', 'dependency-versions.txt'),
                       (build_root / 'vcpkg/LICENSE.txt', 'vcpkg-LICENSE.txt')):
        if path.is_file():
            files[name] = path
    for package in sorted((build_root / 'vcpkg/buildtrees').glob('*')):
        add_tree(package / 'src', 'third-party-sources/'+package.name)
    shared = build_root / 'engine/vcpkg_installed/x64-windows-static/share'
    for path in sorted(shared.rglob('*')):
        if path.is_file() and path.name.lower().startswith(('copyright', 'license', 'copying')):
            files['third-party-notices/'+path.relative_to(shared).as_posix()] = path
    for name in names:
        if name.startswith('data/music/'):
            files['colobot-data/music/'+Path(name).name] = original / name
    return files


def package(original, install, output, prepared, project=ROOT, build_root=None):
    original, install, output, prepared = (path.resolve() for path in (original, install, output, prepared))
    build_root = build_root.resolve() if build_root else install.parent
    sources_zip = output.with_name(output.stem+'-sources.zip')
    report_file = output.with_name(output.stem+'-verification.json')
    for target in (output, sources_zip, report_file, output.with_suffix('.zip.sha256'),
                   sources_zip.with_suffix('.zip.sha256')):
        if target.exists():
            raise FileExistsError(f'Output already exists; choose a different --output filename: {target}')
        if target.is_relative_to(original) or target.is_relative_to(install):
            raise ValueError('Output must be outside the original and installed game folders')
    names = manifest()
    additions = italian_files(names)
    missing = sorted(name for name in names if not (original / name).is_file())
    if missing:
        raise FileNotFoundError('Original distribution files missing: ' + ', '.join(missing[:5]))
    for name in additions:
        if not (install / name).is_file():
            raise FileNotFoundError(install / name)
    imports = check_executable(install / 'colobot.exe')
    with (install / 'lang/it/LC_MESSAGES/colobot.mo').open('rb') as stream:
        catalog = gettext.GNUTranslations(stream)
    if catalog.info().get('language') != 'it' or catalog.gettext('Missions') != 'Missioni':
        raise ValueError('Invalid installed Italian interface catalog')
    output.parent.mkdir(parents=True, exist_ok=True)
    print('Building the original Windows 0.2.2 layout with native Italian...', flush=True)
    with tempfile.TemporaryDirectory(prefix='colobot-022-package-', dir=output.parent) as temporary:
        folder = Path(temporary)
        stage = folder / PACKAGE_NAME
        changed = []
        for name in sorted(names):
            target = stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            if name == 'colobot.exe':
                shutil.copy2(install / name, target)
            elif name.startswith('data/levels/') and name.endswith(('/scene.txt', '/chaptertitle.txt')):
                target.write_bytes(merge_scene((original / name).read_bytes(), (install / name).read_bytes()))
                changed.append(name)
            else:
                shutil.copy2(original / name, target)
            if name.startswith('data/music/') and target.read_bytes()[:4] != b'OggS':
                raise ValueError(f'Invalid original music file: {name}')
        for name in sorted(additions):
            target = stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(install / name, target)
        found = {path.relative_to(stage).as_posix() for path in stage.rglob('*') if path.is_file()}
        if found != names | additions or len(changed) != 173:
            raise ValueError('The packaged file layout differs from the original plus Italian')
        if any((stage / name).read_bytes() != (original / name).read_bytes()
               for name in names - {'colobot.exe', *changed}):
            raise ValueError('An original resource changed during packaging')
        report = {'original_files': len(names), 'italian_files_added': len(additions),
                  'total_game_files': len(found), 'localized_level_files': len(changed),
                  'original_resources_preserved': True, 'runtime_dlls_added': [],
                  'executable_imports': imports}
        staged_zip = folder / output.name
        game_hash = write_zip(stage, staged_zip)
        print('Creating the separate source and license archive...', flush=True)
        sources = source_files(prepared, project, build_root, original, names)
        staged_sources = folder / sources_zip.name
        prefix = PACKAGE_NAME+'-sources/'
        with zipfile.ZipFile(staged_sources, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for name, path in sorted(sources.items()):
                archive.write(path, prefix+name)
            archive.writestr(prefix+'README.txt',
                'Community build of Colobot Gold 0.2.2-alpha with native Italian support.\n'
                'The modified engine, data, translation, build scripts, locally retained third-party\n'
                'source trees and dependency copyright/license notices are included separately\n'
                'from the playable game. Third-party source directories correspond to vcpkg builds.\n'
                'See italian-translation/README.md for the MSVC build configuration.\n')
        with zipfile.ZipFile(staged_sources) as archive:
            if archive.testzip() is not None:
                raise ValueError('Source ZIP integrity check failed')
        with staged_sources.open('rb') as stream:
            source_hash = hashlib.file_digest(stream, 'sha256').hexdigest()
        for staged, target, digest in ((staged_zip, output, game_hash),
                                      (staged_sources, sources_zip, source_hash)):
            staged.replace(target)
            target.with_suffix('.zip.sha256').write_text(
                f'{digest}  {target.name}\n', encoding='utf-8', newline='\n')
        report_file.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(f'Created: {output}\nGame files: {len(found)}; additional runtime DLLs: 0.', flush=True)
    print(f'Separate sources and licenses: {sources_zip}', flush=True)
    return output, sources_zip, report_file


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original', required=True, type=Path, help='Original official Windows 0.2.2 game folder')
    parser.add_argument('--install', type=Path, default=Path('C:/colobot-build-022/install'))
    parser.add_argument('--prepared', type=Path, default=ROOT / 'build/release-022/prepared')
    parser.add_argument('--output', type=Path, default=Path('C:/colobot-build-022') / (PACKAGE_NAME+'.zip'))
    args = parser.parse_args()
    try:
        package(args.original, args.install, args.output, args.prepared)
    except (OSError, ValueError) as error:
        print(f'Packaging stopped: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
