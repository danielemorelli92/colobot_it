#!/usr/bin/env python3
"""Check portable packaging without requiring a Windows build or runner."""
from contextlib import redirect_stdout
import hashlib
import io
import os
from pathlib import Path
import struct
import tempfile
from unittest.mock import patch
import zipfile

from package_windows import PACKAGE_NAME, collect_dlls, package


def italian_catalog():
    originals = [b'', b'Missions']
    translations = [b'Language: it\nContent-Type: text/plain; charset=UTF-8\n', b'Missioni']
    original_data = b'\0'.join(originals) + b'\0'
    translated_data = b'\0'.join(translations) + b'\0'
    offset = 28 + 16 * len(originals)
    original_table = []
    for value in originals:
        original_table.append(struct.pack('<2I', len(value), offset))
        offset += len(value) + 1
    translation_table = []
    for value in translations:
        translation_table.append(struct.pack('<2I', len(value), offset))
        offset += len(value) + 1
    return (struct.pack('<7I', 0x950412de, 0, len(originals), 28, 28 + 8 * len(originals), 0, 0)
            + b''.join(original_table) + b''.join(translation_table) + original_data + translated_data)


with tempfile.TemporaryDirectory(prefix='colobot-portable-test-') as temporary:
    root = Path(temporary)
    install = root / 'install'
    install.mkdir()
    (install / 'colobot.exe').write_bytes(b'fake native test executable: Italiano\0it_IT.utf8\0')
    (install / 'installed.dll').write_bytes(b'installed game library')
    (install / 'unused.dll').write_bytes(b'unused old library')
    (install / 'Gioca-in-italiano.cmd').write_text('obsolete launcher')
    (install / 'sources').mkdir()
    (install / 'sources/old-build.txt').write_text('obsolete source files')
    (install / 'saves/savegame/Personal').mkdir(parents=True)
    (install / 'saves/savegame/Personal/private.txt').write_text('private progress')
    (install / 'saves/colobot.json').write_text('{"Gamer":{"LastName":"Personal"}}')
    (install / 'colobot.log').write_text('private paths')
    (install / 'lang/it/LC_MESSAGES').mkdir(parents=True)
    (install / 'lang/it/LC_MESSAGES/colobot.mo').write_bytes(italian_catalog())
    (install / 'data/help/I').mkdir(parents=True)
    (install / 'data/help/I/cbot.txt').write_text('Italian CBOT manual')
    runtime = root / 'ucrt64/bin'
    runtime.mkdir(parents=True)
    (runtime / 'first.dll').write_bytes(b'codec.dll\0')
    (runtime / 'second.dll').write_bytes(b'fake second DLL')
    (runtime / 'codec.dll').write_bytes(b'dynamically loaded codec')
    licenses = runtime.parent / 'share/licenses/fixture'
    licenses.mkdir(parents=True)
    (licenses / 'LICENSE').write_text('runtime license')
    system = root / 'Windows/System32'
    system.mkdir(parents=True)
    (system / 'KERNEL32.dll').write_bytes(b'Windows system DLL')
    for source in ['engine', 'data']:
        (root / source).mkdir()
        (root / source / 'CMakeLists.txt').write_text('test source fixture')

    imports = {'colobot.exe': ['FIRST.dll', 'installed.dll', 'KERNEL32.dll', 'api-ms-win-core-test.dll'],
               'first.dll': ['second.dll'], 'second.dll': ['first.dll'], 'codec.dll': [], 'installed.dll': []}

    def objdump(args, **kwargs):
        name = Path(args[-1]).name.casefold()
        return 'file format pei-x86-64\n' + ''.join('DLL Name: ' + dll + '\n' for dll in imports[name])

    with patch('package_windows.subprocess.check_output', side_effect=objdump):
        found = collect_dlls(install / 'colobot.exe', runtime, system, Path('objdump'))
        assert {p.name for p in found} == {'first.dll', 'second.dll', 'codec.dll', 'installed.dll'}
        imports['first.dll'].append('missing.dll')
        try:
            collect_dlls(install / 'colobot.exe', runtime, system, Path('objdump'))
        except FileNotFoundError as error:
            assert 'missing.dll' in str(error)
        else:
            raise AssertionError('Missing dependency accepted')
        imports['first.dll'].pop()
        output = root / 'portable.zip'
        with patch.dict(os.environ, {'SYSTEMROOT': str(system.parent)}), \
             patch('package_windows.shutil.which', return_value=None), redirect_stdout(io.StringIO()):
            game_zip, source_zip = package(install, output, root / 'engine', root / 'data', runtime, Path('objdump'))

    with zipfile.ZipFile(output) as archive:
        names = set(archive.namelist())
        assert archive.testzip() is None
        assert not any('Personal' in name or name.endswith('colobot.log') for name in names)
        assert not any('/saves/' in name or '/sources/' in name for name in names)
        assert not any(name.endswith(('.cmd', '.bat', 'colobot.json')) for name in names)
        assert archive.read(PACKAGE_NAME + '/colobot.exe') == (install / 'colobot.exe').read_bytes()
        for name in ['first.dll', 'second.dll', 'codec.dll', 'installed.dll', 'licenses/MSYS2-LICENSES.txt']:
            assert PACKAGE_NAME + '/' + name in names, name
        assert b'runtime license' in archive.read(PACKAGE_NAME + '/licenses/MSYS2-LICENSES.txt')
        assert PACKAGE_NAME + '/KERNEL32.dll' not in names
        assert PACKAGE_NAME + '/unused.dll' not in names
        assert {name.split('/')[1] for name in names} == {
            'colobot.exe', 'first.dll', 'second.dll', 'codec.dll', 'installed.dll',
            'data', 'lang', 'licenses', 'LICENSE', 'README.txt'}
    with zipfile.ZipFile(source_zip) as archive:
        assert archive.testzip() is None
        for name in ['colobot/CMakeLists.txt', 'colobot-data/CMakeLists.txt',
                     'italian-translation/upstream.json']:
            assert PACKAGE_NAME + '-sources/' + name in archive.namelist(), name
    for path in [game_zip, source_zip]:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert path.with_suffix('.zip.sha256').read_text().startswith(digest)
    assert (install / 'saves/savegame/Personal/private.txt').read_text() == 'private progress'
    (install / 'colobot.exe').write_bytes(b'old executable without native Italian support')
    try:
        package(install, root / 'bad.zip', root / 'engine', root / 'data', runtime, Path('objdump'))
    except ValueError as error:
        assert 'native Italian' in str(error)
    else:
        raise AssertionError('Executable without native Italian support accepted')

print('PASS: transitive DLLs and dynamic codecs included; system DLLs excluded; missing imports rejected.')
print('PASS: native executable and Italian catalog checked; no launchers, forced settings, profiles or development files in game ZIP.')
print('PASS: corresponding sources in a separate ZIP; licenses, both archive integrity checks and checksums verified.')
