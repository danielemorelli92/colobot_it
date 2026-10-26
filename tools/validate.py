#!/usr/bin/env python3
"""Validate all Italian catalogs against pinned upstream templates and GNU gettext."""
import argparse
import collections
import gettext
from pathlib import Path
import re
import subprocess
import tempfile
import polib
from localization_checks import check_translation
ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--engine', type=Path, required=True)
p.add_argument('--data', type=Path, required=True)
p.add_argument('--msgfmt', default='msgfmt')
a = p.parse_args()
total = translated = 0
with tempfile.TemporaryDirectory() as temp:
    for name, source in [('colobot', a.engine), ('colobot-data', a.data)]:
        for path in sorted((ROOT/'translations'/name).rglob('it.po')):
            catalog = polib.pofile(str(path), check_for_duplicates=True)
            pots = list((source/path.relative_to(ROOT/'translations'/name).parent).glob('*.pot'))
            assert len(pots) == 1, path
            template = polib.pofile(str(pots[0]))
            assert {(e.msgctxt, e.msgid, e.msgid_plural) for e in catalog} == {(e.msgctxt, e.msgid, e.msgid_plural) for e in template}, path
            assert catalog.metadata['Language'] == 'it'
            for entry in catalog.translated_entries():
                try:
                    check_translation(entry.msgid, entry.msgstr, entry.flags)
                except ValueError as error:
                    raise ValueError(f'{path}: {entry.msgid}: {error}') from error
            mo = Path(temp)/'test.mo'
            subprocess.run([a.msgfmt, '--check', '--check-format', '-o', str(mo), str(path)], check=True)
            with mo.open('rb') as f:
                runtime = gettext.GNUTranslations(f)
            for entry in catalog.translated_entries():
                if not entry.msgctxt and not entry.msgid_plural:
                    assert runtime.gettext(entry.msgid) == entry.msgstr
            total += len(catalog)
            translated += len(catalog.translated_entries())
print(f'Validated: {total} entries, {translated} translated, {total-translated} untranslated; no fuzzy entries used.')
