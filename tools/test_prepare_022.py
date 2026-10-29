#!/usr/bin/env python3
"""Exercise Git archive newline handling and recovery of generated data."""
import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import prepare_022 as preparation


class PreparationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='colobot newline check ')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        self.git('init', '-q')
        self.git('config', 'core.autocrlf', 'true')
        self.english = 'help/generic/E/cbot.txt'
        self.catalog = 'help/generic/po/it.po'
        self.base_catalog = 'help/generic/po/de.po'
        self.source = b'\\b;Programming\nExample text\n'
        for rel, content in [(self.english, self.source),
                             (self.base_catalog, b'Original German catalog\n')]:
            target = self.repo / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        self.git('add', '.')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                 'commit', '-qm', 'Input with LF')
        self.commit = self.git('rev-parse', 'HEAD').strip()
        self.output = self.root / 'prepared'
        self.italian = b'msgid "Programming"\nmsgstr "Programmazione"\n'
        original = self.output / 'translation/translations/colobot-data' / self.catalog
        original.parent.mkdir(parents=True)
        original.write_bytes(self.italian)
        self.record = {'italian_files': {
            'colobot-data/' + self.catalog: hashlib.sha256(self.italian).hexdigest()}}
        pins = patch.dict(preparation.PINS, {'colobot-data': self.commit})
        pins.start()
        self.addCleanup(pins.stop)

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), *args],
                                       text=True, stderr=subprocess.PIPE)

    def damaged_data(self):
        target = self.output / 'colobot-data' / self.english
        target.parent.mkdir(parents=True)
        target.write_bytes(self.source.replace(b'\n', b'\r\n'))
        damaged = self.output / 'colobot-data' / self.catalog
        damaged.parent.mkdir(parents=True)
        damaged.write_bytes(b'msgid "Programming\\r"\nmsgstr ""\n')

    def test_archive_ignores_global_crlf_conversion(self):
        destination = self.root / 'archive'
        preparation.extract(self.repo, self.commit, destination)
        self.assertEqual((destination / self.english).read_bytes(), self.source)

    def test_repair_restores_catalogs_and_is_idempotent(self):
        self.damaged_data()
        self.assertTrue(preparation.repair_data_newlines(self.output, self.record, self.repo))
        data = self.output / 'colobot-data'
        self.assertEqual((data / self.english).read_bytes(), self.source)
        self.assertEqual((data / self.catalog).read_bytes(), self.italian)
        self.assertEqual((data / self.base_catalog).read_bytes(), b'Original German catalog\n')
        self.assertFalse(preparation.repair_data_newlines(self.output, self.record, self.repo))

    def test_repair_rejects_changed_original_italian_input(self):
        self.damaged_data()
        original = self.output / 'translation/translations/colobot-data' / self.catalog
        original.write_bytes(b'Unexpected modified translation')
        with self.assertRaisesRegex(ValueError, 'Original Italian input changed'):
            preparation.repair_data_newlines(self.output, self.record, self.repo)
        self.assertIn(b'\r\n', (self.output / 'colobot-data' / self.english).read_bytes())

    def test_failed_extraction_keeps_existing_data(self):
        self.damaged_data()
        with patch.object(preparation, 'extract', side_effect=RuntimeError('Interrupted extraction')):
            with self.assertRaisesRegex(RuntimeError, 'Interrupted extraction'):
                preparation.repair_data_newlines(self.output, self.record, self.repo)
        self.assertIn(b'\r\n', (self.output / 'colobot-data' / self.english).read_bytes())


if __name__ == '__main__':
    unittest.main()
