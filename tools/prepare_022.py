#!/usr/bin/env python3
"""Prepare the original 0.2.2 release with native, updated Italian catalogs.

This compatibility helper is kept on the windows-0.2.2 branch. It does not
change the development contribution or reuse a language slot from the game.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile

import polib

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    'colobot': 'e3addd66f6613174c1a61c373808046e7d49b320',
    'colobot-data': '910b0dd8cf722b0bafbdfe9a506a1ca21f0b8f06',
}
TRANSLATION_RELEASE = 'a175595a07ebee6094e726e461cd6d3efb811ca9'
PATCH = 'patches/colobot-0.2.2-alpha-italian.patch'
CHECKS = ('validate.py', 'localization_checks.py', 'review_rules.py',
          'code_comments.py', 'test_complete_data.py', 'check_links.py',
          'test_code_preservation.py')


def run(*args, **kwargs):
    return subprocess.run([str(arg) for arg in args], check=True, **kwargs)


def ensure_commit(repo, url, commit):
    if not (repo / '.git').exists():
        repo.mkdir(parents=True, exist_ok=True)
        run('git', 'init', '-q', repo)
    result = subprocess.run(
        ['git', '-C', str(repo), 'cat-file', '-e', commit + '^{commit}'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if result.returncode:
        run('git', '-C', repo, 'fetch', '--depth=1', url, commit)


def extract(repo, commit, dest, *paths):
    blob = subprocess.check_output(
        ['git', '-c', 'core.autocrlf=false', '-c', 'core.eol=lf',
         '-C', str(repo), 'archive', commit, *paths])
    dest.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(blob)) as archive:
        archive.extractall(dest, filter='data')


def key(entry):
    return entry.msgctxt, entry.msgid, entry.msgid_plural


def catalog_content(path):
    # GNU msgmerge updates dates, comments and ordering during normal builds.
    # Compare message content and flags while retaining the original input hash.
    catalog = polib.pofile(str(path))
    headers = {name: catalog.metadata.get(name) for name in
               ('Language', 'Plural-Forms', 'Content-Type', 'Content-Transfer-Encoding')}
    entries = sorted(json.dumps(
        [entry.msgctxt, entry.msgid, entry.msgid_plural, entry.msgstr,
         sorted(entry.msgstr_plural.items()), sorted(entry.flags), entry.obsolete],
        ensure_ascii=False) for entry in catalog)
    return headers, entries


def update_catalogs(project):
    changed = 0
    count = 0
    for old_path in sorted((project / 'translations').rglob('it.po')):
        catalog = polib.pofile(str(old_path))
        current_path = ROOT / old_path.relative_to(project)
        current = {key(entry): entry for entry in polib.pofile(str(current_path))}
        dirty = False
        for entry in catalog:
            replacement = current.get(key(entry))
            if replacement is None or not replacement.translated():
                continue
            if (entry.msgstr, entry.msgstr_plural) != (
                    replacement.msgstr, replacement.msgstr_plural):
                entry.msgstr = replacement.msgstr
                entry.msgstr_plural = dict(replacement.msgstr_plural)
                dirty = True
                changed += 1
        if dirty:
            with old_path.open('w', encoding='utf-8', newline='\n') as stream:
                stream.write(str(catalog))
        count += len(catalog)
    if count != 5172:
        raise ValueError(f'Unexpected 0.2.2 catalog inventory: {count}')
    print(f'0.2.2 catalogs: {count} entries; {changed} updated translations.', flush=True)


def validate(project, output, msgfmt):
    run(sys.executable, project / 'tools/validate.py', '--require-complete',
        '--engine', output / 'colobot', '--data', output / 'colobot-data',
        '--msgfmt', msgfmt)


def repair_data_newlines(output, recorded, repo):
    """Recover data catalogs damaged by generation from CRLF English input.

    The original i18n reader opens input with newline='\n', leaving a trailing
    '\r' in message IDs. Generation then also rewrites the PO files, so merely
    converting the English files is insufficient: restore the complete pinned
    data tree and its original, verified Italian inputs before rebuilding.
    """
    data = output / 'colobot-data'
    inputs = [*(data / 'help').rglob('E/*.txt'),
              *(data / 'levels').rglob('*.E.txt')]
    if not any(b'\r\n' in path.read_bytes() for path in inputs):
        return False
    for rel, digest in recorded['italian_files'].items():
        original = output / 'translation/translations' / rel
        if hashlib.sha256(original.read_bytes()).hexdigest() != digest:
            raise ValueError(f'Original Italian input changed: {rel}')
    ensure_commit(repo, 'https://github.com/colobot/colobot-data.git', PINS['colobot-data'])
    with tempfile.TemporaryDirectory(prefix='colobot-data-lf-', dir=output.parent) as temporary:
        staged = Path(temporary) / 'colobot-data'
        extract(repo, PINS['colobot-data'], staged)
        originals = output / 'translation/translations/colobot-data'
        for po in originals.rglob('it.po'):
            target = staged / po.relative_to(originals)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(po, target)
        backup = Path(temporary) / 'previous-data'
        data.rename(backup)
        try:
            staged.rename(data)
        except OSError:
            backup.rename(data)
            raise
    print('Restored pinned data sources with LF newlines and original Italian catalogs.', flush=True)
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'build/release-022/prepared')
    parser.add_argument('--engine', type=Path)
    parser.add_argument('--data', type=Path)
    parser.add_argument('--msgfmt', default='msgfmt')
    parser.add_argument('--reuse', action='store_true',
                        help='reuse only a completed, unchanged preparation')
    parser.add_argument('--repair-data-newlines', action='store_true',
                        help='restore pinned data and Italian catalogs if previous Git archives used CRLF')
    args = parser.parse_args()
    output = args.output.resolve()
    marker = output / 'preparation.json'
    if output.exists():
        if not args.reuse or not marker.is_file():
            raise FileExistsError(f'Refusing to overwrite {output}')
        recorded = json.loads(marker.read_text(encoding='utf-8'))
        if recorded['pins'] != PINS or recorded['translation_release'] != TRANSLATION_RELEASE:
            raise ValueError('Preparation uses different source revisions')
        if args.repair_data_newlines:
            repo = args.data.resolve() if args.data else ROOT / 'build/release-022/repos/colobot-data'
            repair_data_newlines(output, recorded, repo)
        refreshed = 0
        for rel, digest in recorded['italian_files'].items():
            original = output / 'translation/translations' / rel
            if hashlib.sha256(original.read_bytes()).hexdigest() != digest:
                raise ValueError(f'Original Italian input changed: {rel}')
            prepared = output / rel
            if hashlib.sha256(prepared.read_bytes()).hexdigest() != digest:
                if catalog_content(prepared) != catalog_content(original):
                    raise ValueError(f'Prepared Italian message content changed: {rel}')
                refreshed += 1
        if refreshed:
            print(f'Accepted gettext metadata/order updates in {refreshed} catalogs; message content verified.', flush=True)
        validate(output / 'translation', output, args.msgfmt)
        print(f'Reusing validated preparation: {output}', flush=True)
        return

    cache = ROOT / 'build/release-022/repos'
    ensure_commit(ROOT, 'https://github.com/danielemorelli92/colobot_it.git',
                  TRANSLATION_RELEASE)
    for name, provided in [('colobot', args.engine), ('colobot-data', args.data)]:
        repo = provided.resolve() if provided else cache / name
        ensure_commit(repo, f'https://github.com/colobot/{name}.git', PINS[name])
        if name == 'colobot':
            engine_repo = repo
        else:
            data_repo = repo

    output.mkdir(parents=True)
    project = output / 'translation'
    extract(ROOT, TRANSLATION_RELEASE, project, 'translations', PATCH)
    update_catalogs(project)
    (project / 'tools').mkdir()
    for script in CHECKS:
        shutil.copyfile(ROOT / 'tools' / script, project / 'tools' / script)
    extract(engine_repo, PINS['colobot'], output / 'colobot')
    extract(data_repo, PINS['colobot-data'], output / 'colobot-data')
    for name in PINS:
        for po in (project / 'translations' / name).rglob('it.po'):
            target = output / name / po.relative_to(project / 'translations' / name)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(po, target)
    run('git', 'apply', '--check', project / PATCH, cwd=output / 'colobot')
    run('git', 'apply', project / PATCH, cwd=output / 'colobot')
    validate(project, output, args.msgfmt)
    catalogs = [path for name in PINS for path in (output / name).rglob('it.po')]
    record = {
        'pins': PINS,
        'translation_release': TRANSLATION_RELEASE,
        'italian_files': {path.relative_to(output).as_posix():
                          hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in catalogs},
    }
    marker.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(f'Prepared native Italian 0.2.2 sources: {output}', flush=True)


if __name__ == '__main__':
    main()
