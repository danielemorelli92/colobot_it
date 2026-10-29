#!/usr/bin/env python3
"""Preserve the final game and test saves, then remove only Colobot build caches."""
import argparse
from datetime import datetime
import gettext
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile
import zipfile

from package_windows_022 import (PACKAGE_NAME, ROOT, check_executable,
                                 italian_files, manifest, source_files)


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def reject_links(path):
    for item in (path, *path.parents):
        if item.is_symlink() or getattr(item, 'is_junction', lambda: False)():
            raise ValueError(f'Cartella collegata: nessuna eliminazione consentita: {item}')


def remove_readonly(function, path, error):
    if not isinstance(error, PermissionError):
        raise error
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
    function(path)


def backup_item(source, target):
    if source.is_dir():
        for path in source.rglob('*'):
            reject_links(path)
        shutil.copytree(source, target, symlinks=True)
        files = [path for path in source.rglob('*') if path.is_file() and not path.is_symlink()]
        for path in files:
            if digest(path) != digest(target / path.relative_to(source)):
                raise ValueError(f'Verifica copia salvataggi fallita: {path}')
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        if digest(source) != digest(target):
            raise ValueError(f'Verifica copia impostazioni fallita: {source}')


def verify_game(game, names):
    missing = sorted(name for name in names if not (game / name).is_file())
    if missing:
        raise ValueError('Cartella del gioco incompleta: ' + ', '.join(missing[:3]))
    check_executable(game / 'colobot.exe')
    with (game / 'lang/it/LC_MESSAGES/colobot.mo').open('rb') as stream:
        catalog = gettext.GNUTranslations(stream)
    if catalog.info().get('language') != 'it' or catalog.gettext('Missions') != 'Missioni':
        raise ValueError('La cartella del gioco non contiene il catalogo italiano atteso.')


def recover_sources(build_root, game, names, apply):
    prepared = build_root / 'italiano/build/release-022/prepared'
    files = source_files(prepared, ROOT, build_root, game, names)
    print('Archivio sorgenti assente: verra conservato dai sorgenti della compilazione.', flush=True)
    if not apply:
        return None
    target = build_root / (PACKAGE_NAME+'-sources.zip')
    with tempfile.TemporaryDirectory(prefix='colobot-sorgenti-', dir=build_root) as temporary:
        staged = Path(temporary) / target.name
        with zipfile.ZipFile(staged, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for name, path in sorted(files.items()):
                archive.write(path, PACKAGE_NAME+'-sources/'+name)
        with zipfile.ZipFile(staged) as archive:
            if archive.testzip() is not None:
                raise ValueError('Verifica archivio dei sorgenti ricreato fallita.')
        staged.replace(target)
    target.with_suffix('.zip.sha256').write_text(
        digest(target)+'  '+target.name+'\n', encoding='utf-8', newline='\n')
    return target


def clean(build_root, destination, legacy_build=None, apply=False, game=None):
    reject_links(build_root.absolute())
    build_root, destination = build_root.resolve(), destination.resolve()
    targets = [build_root / name for name in ('engine', 'data', 'vcpkg', 'install', 'italiano/build')]
    if legacy_build:
        reject_links(legacy_build.absolute())
        legacy_build = legacy_build.resolve()
        if legacy_build.name != 'build' or legacy_build.parent.name != 'colobot-italiano-test':
            raise ValueError('Cartella di prova MSYS2 inattesa: pulizia interrotta.')
        targets.append(legacy_build)
    for target in targets:
        reject_links(target)
        if destination.is_relative_to(target) or target.is_relative_to(destination):
            raise ValueError('La destinazione deve essere separata dalle cartelle da eliminare.')
        if Path.cwd().resolve().is_relative_to(target):
            raise ValueError('Aprire il terminale nella cartella italiano, fuori dai file di compilazione.')
    if destination.is_relative_to(build_root):
        raise ValueError('La copia finale deve stare fuori dalla cartella di compilazione.')
    if game is not None:
        game = game.resolve()
        if any(game.is_relative_to(target) or target.is_relative_to(game) for target in targets):
            raise ValueError('Il gioco da conservare deve stare fuori dalle cartelle da eliminare.')
        original = manifest()
        verify_game(game, original | italian_files(original))
        print(f'Gioco italiano verificato e conservato nella posizione attuale: {game}', flush=True)

    def artifact(name, required=True):
        parents = [build_root, destination]
        if game is not None:
            parents.append(game.parent)
        for parent in parents:
            if (parent / name).is_file():
                return parent / name
        if required:
            raise FileNotFoundError(f'Archivio finale mancante: {name}. Nessuna cartella eliminata.')
        return None

    original = manifest()
    artifacts = {}
    for suffix in ('.zip', '-sources.zip'):
        name = PACKAGE_NAME+suffix
        archive_path = artifact(name, required=game is None)
        if archive_path is None:
            if suffix == '.zip':
                continue
            archive_path = recover_sources(build_root, game, original, apply)
            if archive_path is None:
                continue
        checksum_path = artifact(name+'.sha256', required=game is None)
        print(f'Verifica integrita: {name}', flush=True)
        if checksum_path is not None:
            fields = checksum_path.read_text(encoding='utf-8').split()
            expected = fields[0] if fields else ''
            if digest(archive_path) != expected:
                raise ValueError(f'Checksum non valido: {name}. Nessuna cartella eliminata.')
        with zipfile.ZipFile(archive_path) as archive:
            if archive.testzip() is not None:
                raise ValueError(f'Archivio danneggiato: {name}')
            if suffix == '.zip':
                wanted = {PACKAGE_NAME+'/'+path for path in original | italian_files(original)}
                if len(archive.infolist()) != 4708 or set(archive.namelist()) != wanted:
                    raise ValueError('Lo ZIP del gioco non corrisponde alla build finale da 4.708 file.')
            else:
                for license_path in ('colobot/LICENSE.txt', 'colobot-data/LICENSE.txt'):
                    if PACKAGE_NAME+'-sources/'+license_path not in archive.namelist():
                        raise ValueError('Archivio sorgenti finale incompleto.')
        artifacts[name] = archive_path
        if checksum_path is not None:
            artifacts[name+'.sha256'] = checksum_path
    report_name = PACKAGE_NAME+'-verification.json'
    report_path = artifact(report_name, required=game is None)
    if report_path is not None:
        report = json.loads(report_path.read_text(encoding='utf-8'))
        if report.get('total_game_files') != 4708 or report.get('runtime_dlls_added') != []:
            raise ValueError('Rapporto della build finale inatteso.')
        artifacts[report_name] = report_path
    hashes = {name: digest(source) for name, source in artifacts.items()}
    for name, source in artifacts.items():
        target = destination / name
        if target.exists() and digest(target) != digest(source):
            raise FileExistsError(f'File diverso gia presente: {target}. Nessun file sovrascritto.')

    candidates = []
    locations = [('build-msvc', build_root / 'install'), ('engine-msvc', build_root / 'engine'),
                 ('prove-msvc', build_root / 'italiano/build/install')]
    if legacy_build:
        locations.append(('prove-msys2', legacy_build / 'install'))
    for label, location in locations:
        for name in ('saves', 'native-profile', 'colobot.json', 'colobot.ini'):
            source = location / name
            if source.exists():
                reject_links(source)
                candidates.append((label+'/'+name, source))
    known = {path.resolve() for _, path in candidates}
    for target in targets:
        if target.name == 'vcpkg' or not target.is_dir():
            continue
        for name in ('saves', 'native-profile'):
            for source in target.rglob(name):
                if source.is_dir() and source.resolve() not in known:
                    reject_links(source)
                    candidates.append(('altri-salvataggi/'+str(len(known))+'/'+name, source))
                    known.add(source.resolve())
    logs = [('compilazione/completamento.log', build_root / 'completamento.log'),
            ('compilazione/host-tools-verification.json',
             build_root / 'italiano/build/release-022/host-tools-check/verification.json')]
    candidates.extend((label, path) for label, path in logs if path.is_file())

    print(f'Destinazione del gioco e degli archivi: {destination}', flush=True)
    for target in targets:
        if target.exists():
            print(f'Cartella di compilazione da eliminare: {target}', flush=True)
    if not apply:
        print('Anteprima: nessun file modificato. Usare --apply per eseguire la pulizia.', flush=True)
        return {'applied': False}

    destination.mkdir(parents=True, exist_ok=True)
    backup = None
    if candidates:
        backup = Path(tempfile.mkdtemp(prefix='salvataggi-e-verifiche-', dir=destination))
        for label, source in candidates:
            target = backup / label
            target.parent.mkdir(parents=True, exist_ok=True)
            backup_item(source, target)
        print(f'Salvataggi delle prove e verifiche copiati e controllati: {backup}', flush=True)
    for name, source in artifacts.items():
        target = destination / name
        if not target.exists():
            shutil.move(str(source), str(target))
        if digest(target) != hashes[name]:
            raise ValueError(f'Verifica archivio spostato fallita: {target}')
    existing_game = game is not None
    if game is None:
        game = destination / PACKAGE_NAME
    if not game.exists():
        with tempfile.TemporaryDirectory(prefix='.estrazione-colobot-', dir=destination) as temporary:
            with zipfile.ZipFile(destination / (PACKAGE_NAME+'.zip')) as archive:
                archive.extractall(temporary)
            (Path(temporary) / PACKAGE_NAME).rename(game)
    elif not game.is_dir():
        raise FileExistsError(f'La destinazione del gioco non e una cartella: {game}')
    if not (game / 'colobot.exe').is_file():
        raise FileNotFoundError(f'Il gioco nella destinazione finale e incompleto: {game}')
    if any(not (game / name).is_file() for name in original | italian_files(original)):
        raise ValueError(f'La cartella del gioco finale e incompleta: {game}')
    if existing_game:
        verify_game(game, original | italian_files(original))

    free_before = shutil.disk_usage(build_root).free
    removed, failed = [], []
    for target in targets:
        if not target.exists():
            continue
        reject_links(target)
        try:
            shutil.rmtree(target, onexc=remove_readonly)
            removed.append(str(target))
            print(f'Eliminata: {target}', flush=True)
        except OSError as error:
            failed.append({'path': str(target), 'error': str(error)})
            print(f'Cartella ancora in uso o non eliminabile: {target}', flush=True)
    for name in ('completamento.log', 'configure.log', 'build.log'):
        log = build_root / name
        if log.is_file() and not log.is_symlink():
            try:
                log.unlink()
            except OSError:
                pass
    result = {'applied': True, 'completed_at': datetime.now().astimezone().isoformat(),
              'game': str(game), 'saved_archives': str(destination),
              'test_saves_and_logs': str(backup) if backup else None,
              'backup_items': [{'source': str(source), 'backup': str(backup / label)}
                               for label, source in candidates] if backup else [],
              'removed': removed, 'failed': failed,
              'freed_gib': max(0, shutil.disk_usage(build_root).free-free_before)/1024**3}
    (destination / 'pulizia-report.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(f'Gioco pronto: {game / "colobot.exe"}', flush=True)
    print(f'Spazio recuperato dalle cartelle di compilazione: {result["freed_gib"]:.2f} GiB', flush=True)
    if failed:
        raise OSError('Alcune cartelle sono ancora in uso: chiudere gioco/terminali MSYS2 e ripetere il comando.')
    print('Pulizia completata. Gli strumenti MSYS2 e Visual Studio Build Tools possono essere\n'
          'disinstallati da Impostazioni > App se non vengono usati per altri progetti.', flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Esegui la pulizia; altrimenti mostra solo una anteprima')
    parser.add_argument('--destination', type=Path)
    parser.add_argument('--game', type=Path, help='Cartella del gioco gia estratto da conservare senza spostarla')
    args = parser.parse_args()
    if os.name != 'nt':
        parser.error('Eseguire questo comando su Windows.')
    home = Path(os.environ['USERPROFILE'])
    destination = args.destination or home / 'Desktop/Colobot-Italiano'
    legacy = Path('C:/msys64/home') / home.name / 'colobot-italiano-test/build'
    try:
        clean(Path('C:/colobot-build-022'), destination, legacy, apply=args.apply, game=args.game)
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        print(f'Pulizia interrotta: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
