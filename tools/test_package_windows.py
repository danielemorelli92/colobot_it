#!/usr/bin/env python3
"""Check portable packaging without requiring a Windows build or runner."""
from contextlib import redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
from unittest.mock import patch
import zipfile

from package_windows import PACKAGE_NAME, collect_dlls, package


with tempfile.TemporaryDirectory(prefix='colobot-portable-test-') as temporary:
    root = Path(temporary)
    install = root / 'install'
    install.mkdir()
    (install / 'colobot.exe').write_bytes(b'fake test executable')
    (install / 'saves/savegame/Personal').mkdir(parents=True)
    (install / 'saves/savegame/Personal/private.txt').write_text('private progress')
    (install / 'saves/colobot.json').write_text('{"Gamer":{"LastName":"Personal"}}')
    (install / 'colobot.log').write_text('private paths')
    (install / 'lang/it/LC_MESSAGES').mkdir(parents=True)
    (install / 'lang/it/LC_MESSAGES/colobot.mo').write_bytes(b'catalog')
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

    imports = {'colobot.exe': ['FIRST.dll', 'KERNEL32.dll', 'api-ms-win-core-test.dll'],
               'first.dll': ['second.dll'], 'second.dll': ['first.dll'], 'codec.dll': []}

    def objdump(args, **kwargs):
        name = Path(args[-1]).name.casefold()
        return 'file format pei-x86-64\n' + ''.join('DLL Name: ' + dll + '\n' for dll in imports[name])

    with patch('package_windows.subprocess.check_output', side_effect=objdump):
        found = collect_dlls(install / 'colobot.exe', runtime, system, Path('objdump'))
        assert {p.name for p in found} == {'first.dll', 'second.dll', 'codec.dll'}
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
            package(install, output, root / 'engine', root / 'data', runtime, Path('objdump'))

    with zipfile.ZipFile(output) as archive:
        names = set(archive.namelist())
        assert archive.testzip() is None
        assert not any('Personal' in name or name.endswith('colobot.log') for name in names)
        config = json.loads(archive.read(PACKAGE_NAME + '/saves/colobot.json'))
        assert config == {'Language': {'Lang': 'it'}}
        for name in ['first.dll', 'second.dll', 'codec.dll', 'Gioca-in-italiano.cmd',
                     'sources/colobot/CMakeLists.txt', 'sources/colobot-data/CMakeLists.txt',
                     'licenses/msys2/fixture/LICENSE']:
            assert PACKAGE_NAME + '/' + name in names, name
        assert PACKAGE_NAME + '/KERNEL32.dll' not in names
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    assert output.with_suffix('.zip.sha256').read_text().startswith(digest)
    assert (install / 'saves/savegame/Personal/private.txt').read_text() == 'private progress'

print('PASS: transitive DLLs and dynamic codecs included; system DLLs excluded; missing imports rejected.')
print('PASS: personal profiles excluded; fresh Italian config, sources, licenses, ZIP integrity and checksum verified.')
