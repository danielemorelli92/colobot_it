#!/usr/bin/env python3
"""Validate all Italian catalogs against pinned upstream templates and GNU gettext."""
import argparse
import gettext
from pathlib import Path
import subprocess
import tempfile
import polib
from localization_checks import check_translation
ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--engine', type=Path, required=True)
p.add_argument('--data', type=Path, required=True)
p.add_argument('--msgfmt', default='msgfmt')
p.add_argument('--require-complete', action='store_true')
a = p.parse_args()
total = translated = 0
with tempfile.TemporaryDirectory() as temp:
    for name, source in [('colobot', a.engine), ('colobot-data', a.data)]:
        overlay = ROOT/'translations'/name
        catalogs = sorted(overlay.rglob('it.po'))
        if a.require_complete:
            expected = {path.parent.relative_to(source) for path in source.rglob('*.pot')}
            actual = {path.parent.relative_to(overlay) for path in catalogs}
            if not expected or expected != actual:
                missing = sorted(str(path/'it.po') for path in expected - actual)
                extra = sorted(str(path/'it.po') for path in actual - expected)
                raise ValueError(f'{name}: catalog inventory mismatch; missing={missing}; extra={extra}')
        for path in catalogs:
            catalog = polib.pofile(str(path), check_for_duplicates=True)
            pots = list((source/path.relative_to(ROOT/'translations'/name).parent).glob('*.pot'))
            assert len(pots) == 1, path
            template = polib.pofile(str(pots[0]))
            assert {(e.msgctxt, e.msgid, e.msgid_plural) for e in catalog} == {(e.msgctxt, e.msgid, e.msgid_plural) for e in template}, path
            assert catalog.metadata['Language'] == 'it'
            if a.require_complete:
                assert not catalog.untranslated_entries(), path
                assert not catalog.fuzzy_entries(), path
            for entry in catalog.translated_entries():
                forms = [(entry.msgid, entry.msgstr)]
                if entry.msgid_plural:
                    assert set(entry.msgstr_plural) == {0, 1}, (path, entry.msgid)
                    forms = [(entry.msgid if index == 0 else entry.msgid_plural, text)
                             for index, text in entry.msgstr_plural.items()]
                for original_text, target in forms:
                    try:
                        check_translation(original_text, target, entry.flags)
                    except ValueError as error:
                        raise ValueError(f'{path}: {original_text}: {error}') from error
            mo = Path(temp)/'test.mo'
            subprocess.run([a.msgfmt, '--check', '--check-format', '-o', str(mo), str(path)], check=True)
            with mo.open('rb') as f:
                runtime = gettext.GNUTranslations(f)
            for entry in catalog.translated_entries():
                if not entry.msgctxt and not entry.msgid_plural:
                    assert runtime.gettext(entry.msgid) == entry.msgstr
                elif entry.msgid_plural and not entry.msgctxt:
                    for count, index in [(0, 1), (1, 0), (2, 1), (10, 1)]:
                        assert runtime.ngettext(entry.msgid, entry.msgid_plural, count) == entry.msgstr_plural[index]
            total += len(catalog)
            translated += len(catalog.translated_entries())
print(f'Validated: {total} entries, {translated} translated, {total-translated} untranslated; no fuzzy entries used.')
