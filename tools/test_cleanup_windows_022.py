#!/usr/bin/env python3
"""Verify backups and deletion boundaries before removing local build caches."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import polib

import cleanup_windows_022 as cleanup
from test_package_windows_022 import executable


class CleanupTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='colobot cleanup test ')
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.build = self.base / 'colobot-build-022'
        self.build.mkdir()
        self.destination = self.base / 'Desktop/Colobot-Italiano'
        self.legacy = self.base / 'msys/home/test/colobot-italiano-test/build'
        self.targets = [self.build / name for name in
                        ('engine', 'data', 'vcpkg', 'install', 'italiano/build')]+[self.legacy]
        for target in self.targets:
            target.mkdir(parents=True)
            (target / 'generated-file.txt').write_text('Only build output')
        for root in (self.build / 'italiano', self.legacy.parent):
            (root / '.git').mkdir()
            (root / '.git/HEAD').write_text('Keep source clone')
        self.saves = {
            self.build / 'install/saves/Pilot/progress.txt': 'MSVC progress',
            self.legacy / 'install/saves/Pilot/progress.txt': 'MSYS2 progress',
            self.legacy / 'unpacked-test/saves/Pilot/progress.txt': 'Old portable test progress',
        }
        for path, content in self.saves.items():
            path.parent.mkdir(parents=True)
            path.write_text(content)
        (self.build / 'keep-my-notes.txt').write_text('Unrelated file')
        (self.build / 'completamento.log').write_text('Build succeeded')
        self.profile = self.base / 'AppData/colobot/profile.txt'
        self.profile.parent.mkdir(parents=True)
        self.profile.write_text('Current game profile')
        names = cleanup.manifest()
        wanted = names | cleanup.italian_files(names)
        self.archives = []
        for suffix in ('.zip', '-sources.zip'):
            archive = self.build / (cleanup.PACKAGE_NAME+suffix)
            with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
                if suffix == '.zip':
                    for name in sorted(wanted):
                        bundle.writestr(cleanup.PACKAGE_NAME+'/'+name, 'Test resource '+name)
                else:
                    for name in ('colobot/LICENSE.txt', 'colobot-data/LICENSE.txt'):
                        bundle.writestr(cleanup.PACKAGE_NAME+'-sources/'+name, 'License fixture')
            archive.with_suffix('.zip.sha256').write_text(cleanup.digest(archive)+'  '+archive.name+'\n')
            self.archives.append(archive)
        report = self.build / (cleanup.PACKAGE_NAME+'-verification.json')
        report.write_text(json.dumps({'total_game_files': 4708, 'runtime_dlls_added': []}))
        output = contextlib.redirect_stdout(io.StringIO())
        output.__enter__()
        self.addCleanup(output.__exit__, None, None, None)

    def run_cleanup(self, **kwargs):
        return cleanup.clean(self.build, self.destination, self.legacy, **kwargs)

    def assert_builds_exist(self):
        self.assertTrue(all(target.is_dir() for target in self.targets))

    def existing_game(self):
        desktop = self.base / 'Desktop'
        desktop.mkdir()
        with zipfile.ZipFile(self.archives[0]) as archive:
            archive.extractall(desktop)
        game = desktop / cleanup.PACKAGE_NAME
        (game / 'colobot.exe').write_bytes(executable())
        po = polib.POFile()
        po.metadata = {'Language': 'it', 'Content-Type': 'text/plain; charset=UTF-8'}
        po.append(polib.POEntry(msgid='Missions', msgstr='Missioni'))
        po.save_as_mofile(str(game / 'lang/it/LC_MESSAGES/colobot.mo'))
        return game

    def remove_bundles(self):
        for archive in self.archives:
            archive.unlink()
            archive.with_suffix('.zip.sha256').unlink()
        (self.build / (cleanup.PACKAGE_NAME+'-verification.json')).unlink()

    def source_tree(self):
        prepared = self.build / 'italiano/build/release-022/prepared'
        for name in ('colobot', 'colobot-data', 'translation'):
            (prepared / name).mkdir(parents=True)
            (prepared / name / 'LICENSE.txt').write_text('Source license fixture')

    def test_preview_changes_nothing(self):
        self.assertEqual(self.run_cleanup(), {'applied': False})
        self.assert_builds_exist()
        self.assertFalse(self.destination.exists())

    def test_cleanup_keeps_game_archives_saves_and_unrelated_files(self):
        hashes = {path.name: cleanup.digest(path) for path in self.archives}
        result = self.run_cleanup(apply=True)
        self.assertFalse(any(target.exists() for target in self.targets))
        self.assertEqual(len(result['removed']), 6)
        self.assertEqual(result['failed'], [])
        for name, digest in hashes.items():
            self.assertEqual(cleanup.digest(self.destination / name), digest)
        backup = Path(result['test_saves_and_logs'])
        saved_contents = {path.read_text() for path in backup.rglob('progress.txt')}
        self.assertEqual(saved_contents, set(self.saves.values()))
        self.assertEqual((backup / 'compilazione/completamento.log').read_text(), 'Build succeeded')
        game = Path(result['game'])
        self.assertTrue((game / 'colobot.exe').is_file())
        self.assertEqual(sum(path.is_file() for path in game.rglob('*')), 4708)
        self.assertEqual(self.profile.read_text(), 'Current game profile')
        self.assertEqual((self.build / 'keep-my-notes.txt').read_text(), 'Unrelated file')
        self.assertTrue((self.build / 'italiano/.git/HEAD').is_file())
        self.assertTrue((self.legacy.parent / '.git/HEAD').is_file())
        self.assertTrue((self.destination / 'pulizia-report.json').is_file())
        again = self.run_cleanup(apply=True)
        self.assertEqual(again['removed'], [])

    def test_invalid_zip_checksum_prevents_all_deletion(self):
        self.archives[0].write_bytes(b'Corrupt archive')
        with self.assertRaisesRegex(ValueError, 'Checksum non valido'):
            self.run_cleanup(apply=True)
        self.assert_builds_exist()
        self.assertFalse(self.destination.exists())

    def test_backup_failure_prevents_all_deletion(self):
        with patch.object(cleanup, 'backup_item', side_effect=PermissionError('Backup failed')):
            with self.assertRaises(PermissionError):
                self.run_cleanup(apply=True)
        self.assert_builds_exist()
        self.assertTrue(all(path.exists() for path in self.archives))

    def test_failed_archive_move_is_detected_before_deletion(self):
        def corrupt_move(source, target):
            Path(target).write_bytes(b'Incomplete copy')
        with patch.object(cleanup.shutil, 'move', side_effect=corrupt_move):
            with self.assertRaisesRegex(ValueError, 'Verifica archivio spostato fallita'):
                self.run_cleanup(apply=True)
        self.assert_builds_exist()

    def test_existing_destination_is_not_overwritten(self):
        self.destination.mkdir(parents=True)
        path = self.destination / self.archives[0].name
        path.write_bytes(b'Another archive')
        with self.assertRaises(FileExistsError):
            self.run_cleanup(apply=True)
        self.assert_builds_exist()
        self.assertEqual(path.read_bytes(), b'Another archive')

    def test_destination_inside_build_tree_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'separata'):
            cleanup.clean(self.build, self.build / 'engine/safe-game', self.legacy, apply=True)
        self.assert_builds_exist()

    def test_linked_build_directory_is_rejected(self):
        target = self.build / 'engine'
        shutil.rmtree(target)
        try:
            target.symlink_to(self.profile.parent, target_is_directory=True)
        except OSError:
            self.skipTest('Symbolic links unavailable')
        with self.assertRaisesRegex(ValueError, 'Cartella collegata'):
            self.run_cleanup(apply=True)
        self.assertEqual(self.profile.read_text(), 'Current game profile')

    def test_existing_game_does_not_require_game_zip_or_report(self):
        game = self.existing_game()
        self.archives[0].unlink()
        self.archives[0].with_suffix('.zip.sha256').unlink()
        (self.build / (cleanup.PACKAGE_NAME+'-verification.json')).unlink()
        (game / 'saves/Pilot').mkdir(parents=True)
        (game / 'saves/Pilot/progress.txt').write_text('Current extracted game progress')
        before = {path.relative_to(game): cleanup.digest(path)
                  for path in game.rglob('*') if path.is_file()}
        result = self.run_cleanup(apply=True, game=game)
        self.assertEqual(result['game'], str(game))
        self.assertEqual(len(result['removed']), 6)
        self.assertFalse((self.destination / cleanup.PACKAGE_NAME).exists())
        after = {path.relative_to(game): cleanup.digest(path)
                 for path in game.rglob('*') if path.is_file()}
        self.assertEqual(before, after)
        self.assertTrue((self.destination / self.archives[1].name).is_file())

    def test_existing_game_recovers_missing_sources_before_cleanup(self):
        game = self.existing_game()
        self.remove_bundles()
        self.source_tree()
        result = self.run_cleanup(apply=True, game=game)
        sources = self.destination / self.archives[1].name
        with zipfile.ZipFile(sources) as archive:
            self.assertIsNone(archive.testzip())
            self.assertIn(cleanup.PACKAGE_NAME+'-sources/colobot/LICENSE.txt', archive.namelist())
        self.assertEqual(len(result['removed']), 6)
        self.assertTrue((game / 'colobot.exe').is_file())

    def test_missing_sources_and_preview_leave_all_builds_intact(self):
        game = self.existing_game()
        self.remove_bundles()
        self.source_tree()
        self.assertEqual(self.run_cleanup(game=game), {'applied': False})
        self.assert_builds_exist()
        self.assertFalse(self.destination.exists())
        self.assertFalse(self.archives[1].exists())

    def test_incomplete_existing_game_prevents_all_deletion(self):
        game = self.existing_game()
        (game / 'data/fonts/fonts.ini').unlink()
        with self.assertRaisesRegex(ValueError, 'Cartella del gioco incompleta'):
            self.run_cleanup(apply=True, game=game)
        self.assert_builds_exist()

    def test_game_inside_a_cleanup_target_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'fuori dalle cartelle'):
            self.run_cleanup(apply=True, game=self.build / 'install')
        self.assert_builds_exist()

    def test_missing_source_tree_prevents_deletion_when_archives_are_gone(self):
        game = self.existing_game()
        self.remove_bundles()
        with self.assertRaises(FileNotFoundError):
            self.run_cleanup(apply=True, game=game)
        self.assert_builds_exist()


if __name__ == '__main__':
    unittest.main()
