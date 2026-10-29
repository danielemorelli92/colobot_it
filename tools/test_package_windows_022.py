#!/usr/bin/env python3
"""Check the original 4,255-file layout, Italian-only changes and clean ZIPs."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import struct
import tempfile
import unittest
import zipfile

import polib

import package_windows_022 as packager


def executable(imports=('KERNEL32.dll', 'USER32.dll'), machine=0x8664):
    data = bytearray(0x800)
    data[:2] = b'MZ'
    struct.pack_into('<I', data, 0x3c, 0x80)
    data[0x80:0x84] = b'PE\0\0'
    struct.pack_into('<HH', data, 0x84, machine, 1)
    struct.pack_into('<H', data, 0x94, 240)
    optional = 0x98
    struct.pack_into('<H', data, optional, 0x20b)
    struct.pack_into('<I', data, optional+60, 0x200)
    struct.pack_into('<II', data, optional+120, 0x1000, 20*(len(imports)+1))
    struct.pack_into('<IIII', data, optional+240+8, 0x600, 0x1000, 0x600, 0x200)
    position = 0x300
    for index, name in enumerate(imports):
        struct.pack_into('<5I', data, 0x200+20*index, 0, 0, 0, 0x1000+position-0x200, 0)
        encoded = name.encode('ascii')+b'\0'
        data[position:position+len(encoded)] = encoded
        position += len(encoded)
    markers = b'Italiano\0it_IT.utf8\0Colobot: Gold Edition 0.2.2-alpha\0'
    data[0x500:0x500+len(markers)] = markers
    return data


class PackageTests(unittest.TestCase):
    def test_pe_headers_imports_and_runtime_rejection(self):
        with tempfile.TemporaryDirectory() as temporary:
            exe = Path(temporary) / 'colobot.exe'
            exe.write_bytes(executable())
            self.assertEqual(packager.check_executable(exe), ['KERNEL32.dll', 'USER32.dll'])
            exe.write_bytes(executable(imports=('KERNEL32.dll', 'libgcc_s_seh-1.dll')))
            with self.assertRaisesRegex(ValueError, 'additional runtime DLLs'):
                packager.check_executable(exe)
            exe.write_bytes(executable(machine=0x14c))
            with self.assertRaisesRegex(ValueError, 'x64'):
                packager.check_executable(exe)
            exe.write_bytes(executable().replace(b'0.2.2-alpha', b'0.3.0-alpha'))
            with self.assertRaisesRegex(ValueError, 'native Italian 0.2.2'):
                packager.check_executable(exe)

    def test_scene_merge_preserves_every_other_byte(self):
        original = b'Title.E text="English"\r\nTitle.F text="French"\r\nCreateObject type=Me\r\n'
        translated = b'Title.I text="Italiano"\nCreateObject type=AlienQueen\n'
        result = packager.merge_scene(original, translated)
        self.assertEqual(result, b'Title.I text="Italiano"\r\n'+original)
        self.assertNotIn(b'AlienQueen', result)
        with self.assertRaisesRegex(ValueError, 'already contains Italian'):
            packager.merge_scene(result, translated)
        with self.assertRaisesRegex(ValueError, 'Missing Italian'):
            packager.merge_scene(original, b'Title.E text="English"\n')

    def test_complete_original_layout_and_private_file_exclusion(self):
        with tempfile.TemporaryDirectory(prefix='colobot original package ') as temporary:
            root = Path(temporary)
            original, install, prepared = (root / name for name in ('original', 'install', 'prepared'))
            names = packager.manifest()
            additions = packager.italian_files(names)
            scenes = {name for name in names if name.startswith('data/levels/')
                      and name.endswith(('/scene.txt', '/chaptertitle.txt'))}
            for name in names:
                target = original / name
                target.parent.mkdir(parents=True, exist_ok=True)
                content = b'Original resource, unchanged.\n'
                if name in scenes:
                    content = b'Title.E text="English"\r\nTitle.F text="French"\r\n'
                    destination = install / name
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(b'Title.I text="Italiano"\n')
                elif name.startswith('data/music/'):
                    content = b'OggS original music test fixture'
                target.write_bytes(content)
            for name in additions:
                path = install / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b'Italian document\n')
            (install / 'colobot.exe').write_bytes(executable())
            po = polib.POFile()
            po.metadata = {'Language': 'it', 'Content-Type': 'text/plain; charset=UTF-8'}
            po.append(polib.POEntry(msgid='Missions', msgstr='Missioni'))
            po.save_as_mofile(str(install / 'lang/it/LC_MESSAGES/colobot.mo'))
            for parent in (original, install):
                (parent / 'saves/Personal').mkdir(parents=True)
                (parent / 'saves/Personal/private.txt').write_text('private progress')
                (parent / 'Gioca-in-italiano.cmd').write_text('unwanted launcher')
                (parent / 'unwanted.dll').write_bytes(b'unwanted library')
            for name in ('colobot', 'colobot-data', 'translation'):
                (prepared / name).mkdir(parents=True)
                (prepared / name / 'LICENSE.txt').write_text('test license')
            dependency_source = root / 'vcpkg/buildtrees/libfixture/src/unpacked/source.c'
            dependency_source.parent.mkdir(parents=True)
            dependency_source.write_text('third-party source fixture')
            notice = root / 'engine/vcpkg_installed/x64-windows-static/share/libfixture/copyright'
            notice.parent.mkdir(parents=True)
            notice.write_text('third-party license fixture')
            output = root / 'game.zip'
            with contextlib.redirect_stdout(io.StringIO()):
                game, sources, report = packager.package(original, install, output, prepared)
            with zipfile.ZipFile(game) as archive:
                self.assertIsNone(archive.testzip())
                prefix = packager.PACKAGE_NAME+'/'
                self.assertEqual(set(archive.namelist()), {prefix+name for name in names | additions})
                self.assertEqual(len(archive.namelist()), 4708)
                for name in names - {'colobot.exe'} - scenes:
                    self.assertEqual(archive.read(prefix+name), (original / name).read_bytes(), name)
                for name in scenes:
                    content = archive.read(prefix+name)
                    self.assertEqual(content, b'Title.I text="Italiano"\r\n'+(original / name).read_bytes())
                self.assertEqual(archive.read(prefix+'colobot.exe'), (install / 'colobot.exe').read_bytes())
            with zipfile.ZipFile(sources) as archive:
                self.assertIsNone(archive.testzip())
                self.assertTrue(any(name.endswith('/colobot/LICENSE.txt') for name in archive.namelist()))
                self.assertTrue(any(name.endswith('/third-party-sources/libfixture/unpacked/source.c')
                                    for name in archive.namelist()))
                self.assertTrue(any(name.endswith('/third-party-notices/libfixture/copyright')
                                    for name in archive.namelist()))
            self.assertEqual(json.loads(report.read_text())['total_game_files'], 4708)
            for path in (game, sources):
                self.assertIn(hashlib.sha256(path.read_bytes()).hexdigest(), path.with_suffix('.zip.sha256').read_text())
            self.assertEqual((original / 'saves/Personal/private.txt').read_text(), 'private progress')
            with self.assertRaises(FileExistsError):
                packager.package(original, install, output, prepared)
            (original / 'data/fonts/fonts.ini').unlink()
            with self.assertRaisesRegex(FileNotFoundError, 'Original distribution files missing'):
                packager.package(original, install, root / 'invalid.zip', prepared)
            self.assertFalse((root / 'invalid.zip').exists())


if __name__ == '__main__':
    unittest.main()
