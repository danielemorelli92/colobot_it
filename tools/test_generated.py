#!/usr/bin/env python3
"""Functional assertions against files produced by the official data generator."""
from pathlib import Path
import argparse
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('build',type=Path)
a=p.parse_args()
level=a.build/'levels/po/missions/chapter001/level001'
assert 'Title.I text="Equipaggiamento"' in (level/'scene.txt').read_text()
help=(level/'help/help.I.txt').read_text()
solution=(level/'help/soluce.I.txt').read_text()
assert 'Dal centro di addestramento della NASA' in help
assert '\\key help;' in help and '\\button 63;' in help
assert '\\u object\\huston;' in help
assert '\\u object\\Huston;' not in help
assert 'Al primo incrocio gira verso est (a sinistra).' in solution
assert (a.build/'help/po/cbot/I/cbot/abstime.txt').is_file()
print('PASS: Italian scene title, briefing, walkthrough, key/button/link markup and CBot help output.')

# Every translated campaign entry must occur in this build, after the same
# pseudo-HTML conversion as the official generator. This detects stale output
# and missing Italian help files across all nine planets, not just mission 1.
import sys
import polib
source=Path(__file__).resolve().parents[1]/'translations/colobot-data'
# Load the official converter from a supplied, pinned data-source tree.
# Prepared data source lives next to its build sibling in README examples;
# an explicit environment variable supports other build directory layouts.
import os
converter_source=Path(os.environ.get('COLOBOT_DATA_SOURCE', 'build/prepared/colobot-data'))
sys.path.insert(0,str(converter_source/'i18n-tools/scripts'))
from translate_help import convert_tag_syntax_to_escape_syntax
seen=0
for catalog in sorted((source/'levels/missions').rglob('it.po')):
    po=polib.pofile(str(catalog))
    assert not po.untranslated_entries(), catalog
    relative=catalog.parent.parent.relative_to(source/'levels/missions')
    output=a.build/'levels/po/missions'/relative
    if relative==Path('.'):
        files=list(output.glob('chapter*/chaptertitle.txt'))
    else:
        files=[output/'scene.txt', *sorted((output/'help').glob('*.I.txt'))]
    text='\n'.join(path.read_text() for path in files)
    for entry in po.translated_entries():
        expected=convert_tag_syntax_to_escape_syntax(entry.msgstr).strip()
        assert expected in text,(catalog,entry.msgid)
        seen+=1
print(f'PASS: all {seen} campaign entries found in generated Italian output.')
