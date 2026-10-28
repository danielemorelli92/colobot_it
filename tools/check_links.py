#!/usr/bin/env python3
"""Resolve every Italian SatCom hyperlink and named anchor in a native data build."""
from pathlib import PurePosixPath
import argparse
import re
from pathlib import Path

LINK = re.compile(r'\\u ([^;\n]+);')
MARKER = re.compile(r'\\m ([^;\n]+);')

def verify_links(files):
    overlay = {name: value.decode('utf-8') for name, value in files.items()}
    documents = {name: text for name, text in overlay.items()
                 if name.startswith('help/I/') or '/help/' in name}
    links = 0
    anchors = 0
    failures = []
    for name, text in documents.items():
        for match in LINK.finditer(text):
            parts = match[1].split()
            if not parts or len(parts) > 2:
                failures.append((name, match[1], 'invalid link syntax'))
                continue
            target = parts[0] + '.txt'
            # Mirror CLevelParser::InjectLevelPaths: level macros use data-root
            # paths; all other targets are relative to help/%lng%.
            original = target
            if '/help/' in name and name.startswith('levels/'):
                level = name.split('/help/', 1)[0]
                chapter, category = level.rsplit('/', 1)[0], level.split('/chapter', 1)[0]
                for macro, value in [('%lvl%', level), ('%chap%', chapter), ('%cat%', category)]:
                    target = target.replace(macro, value)
            if target == original:
                target = 'help/I/' + target
            target = str(PurePosixPath(target.replace('%lng%', 'I').replace('\\', '/')))
            links += 1
            if target not in overlay:
                failures.append((name, match[1], f'missing Italian page: {target}'))
            elif len(parts) == 2:
                anchors += 1
                if parts[1] not in MARKER.findall(overlay[target]):
                    failures.append((name, match[1], 'missing named anchor'))
    if failures:
        raise AssertionError('\n'.join(str(item) for item in failures))
    return {'documents': len(documents), 'links': links, 'named_anchors': anchors}

def regression_checks():
    sample = {'help/I/cbot.txt': b'\\l;move\\u cbot\\move;'
              b'\\l;notes\\u %lvl%/help/help.%lng% notes;',
              'help/I/cbot/move.txt': b'Help'}
    # The global page must not use a level-local macro without level context.
    try: verify_links(sample)
    except AssertionError: pass
    else: raise AssertionError('Unresolvable level macro accepted')
    sample['help/I/cbot.txt'] = b'\\l;move\\u cbot\\move;'
    sample['levels/missions/chapter001/level001/help/help.I.txt'] = b'\\l;notes\\u %lvl%/help/help.%lng% notes;\n\\m notes;'
    assert verify_links(sample) == {'documents': 3, 'links': 2, 'named_anchors': 1}
    for bad in [b'\\u cbot\\missing;', b'\\u cbot\\move missing;']:
        sample['help/I/cbot.txt'] = bad
        try: verify_links(sample)
        except AssertionError: pass
        else: raise AssertionError('Broken link or anchor accepted')

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data-build', type=Path)
    args = p.parse_args()
    regression_checks()
    if args.data_build:
        files = {}
        for category in (args.data_build/'help/po').iterdir():
            for path in (category/'I').rglob('*.txt'):
                files['help/I/'+path.relative_to(category/'I').as_posix()] = path.read_bytes()
        for path in (args.data_build/'levels/po').rglob('*.I.txt'):
            files['levels/'+path.relative_to(args.data_build/'levels/po').as_posix()] = path.read_bytes()
        result = verify_links(files)
        assert result['documents'] > 0 and result['links'] > 0
        print('PASS Italian SatCom links:', result)
    else:
        print('PASS: missing pages, missing anchors and invalid level macros rejected.')
