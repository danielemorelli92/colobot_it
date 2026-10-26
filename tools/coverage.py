#!/usr/bin/env python3
"""Report actual gettext coverage, distinguishing invariant text from translations."""
from pathlib import Path
import argparse
import json
import polib
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output', type=Path)
a=p.parse_args()
rows=[]
for path in sorted((ROOT/'translations').rglob('it.po')):
    po=polib.pofile(str(path))
    translated=po.translated_entries()
    rows.append({'catalog':path.relative_to(ROOT).as_posix(),'entries':len(po),
                 'nonempty':len(translated),
                 'identical_to_source':sum(e.msgstr==e.msgid for e in translated),
                 'untranslated':len(po.untranslated_entries()),'fuzzy':len(po.fuzzy_entries())})
report={'preview':'0.2','catalogs':len(rows),'entries':sum(r['entries'] for r in rows),
        'nonempty':sum(r['nonempty'] for r in rows),
        'identical_to_source':sum(r['identical_to_source'] for r in rows),
        'untranslated':sum(r['untranslated'] for r in rows),'details':rows}
text=json.dumps(report,indent=2)+'\n'
if a.output:a.output.write_text(text)
else:print(text,end='')
print(f"Coverage: {report['nonempty']}/{report['entries']}; {report['identical_to_source']} entries intentionally identical to source; {report['untranslated']} untranslated.")
