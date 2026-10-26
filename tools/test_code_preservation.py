#!/usr/bin/env python3
"""Protect whole code examples, artwork names and generated CBot function names."""
from pathlib import Path
import polib
root=Path(__file__).resolve().parents[1]/'translations/colobot-data'
count=0
for path in root.rglob('it.po'):
    for entry in polib.pofile(str(path)):
        # The upstream extractor calls these three report headings 'Source code'
        # because they use the monospaced style. They are prose, not CBot.
        headings={'-> SURFACE<c/>':'-> SUPERFICIE<c/>',
                  '-> SUBSOIL<c/>':'-> SOTTOSUOLO<c/>',
                  '-> ADDITIONAL INFORMATION<c/>':'-> INFORMAZIONI AGGIUNTIVE<c/>'}
        if entry.msgid.startswith('   Write       and not'):
            assert entry.msgstr==entry.msgid.replace('Write','Scrivi').replace('and not','e non')
            continue
        if entry.msgid in headings:
            assert entry.msgstr==headings[entry.msgid]
            continue
        if any(kind in entry.comment for kind in ['type: Source code','type: Image filename','type: ScriptName-text']):
            assert entry.msgstr==entry.msgid,(path,entry.msgid)
            count+=1
print(f'PASS: {count} complete code examples, artwork references and ScriptName identifiers preserved.')
