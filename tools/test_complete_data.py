#!/usr/bin/env python3
"""Verify every catalog entry is present in a fresh official Italian data build."""
import argparse
from pathlib import Path
import sys
import polib
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--build',type=Path,required=True)
p.add_argument('--source',type=Path,required=True)
a=p.parse_args()
sys.path.insert(0,str(a.source/'i18n-tools/scripts'))
from translate_help import convert_tag_syntax_to_escape_syntax
root=Path(__file__).resolve().parents[1]/'translations/colobot-data'
checked=0
missing=[]
for path in sorted(root.rglob('it.po')):
    po=polib.pofile(str(path))
    assert not po.untranslated_entries(),path
    rel=path.relative_to(root).parts
    if rel[0]=='help':
        files=sorted((a.build/'help/po'/rel[1]/'I').rglob('*.txt'))
    else:
        target=a.build/'levels/po'/Path(*rel[1:-2])
        if len(rel)==4:
            files=sorted(target.glob('chapter*/chaptertitle.txt'))
        else:
            files=[target/'scene.txt',*sorted((target/'help').glob('*.I.txt'))]
    assert files,(path,'no Italian output')
    text='\n'.join(f.read_text(encoding='utf-8') for f in files)
    for entry in po:
        native=convert_tag_syntax_to_escape_syntax(entry.msgstr).strip()
        code='\n'.join(r'\s;'+line for line in convert_tag_syntax_to_escape_syntax(entry.msgstr).split('\n')).strip()
        if native not in text and code not in text:
            missing.append((str(path.relative_to(root)),entry.msgid))
        checked+=1
for path,message in missing:
    print('MISSING',path,repr(message))
assert not missing,f'{len(missing)} entries missing from generated output'
print(f'PASS: all {checked} data catalog entries found in generated Italian files.')
