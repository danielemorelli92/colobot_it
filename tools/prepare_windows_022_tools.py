#!/usr/bin/env python3
"""Prepare the Windows tool cache and pinned Boost compatibility overlay."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import tarfile
import time
import urllib.request
import xml.etree.ElementTree as ET


TOOLS = ('7zip', '7zip_msi', 'cmake', 'git', 'ninja', 'powershell-core')
# Same upstream archives and hashes; only the download host changes.
MIRRORS = {
    '7zip': 'https://github.com/ip7z/7zip/releases/download/21.07/7z2107-extra.7z',
    '7zip_msi': 'https://github.com/ip7z/7zip/releases/download/21.07/7z2107-x64.msi',
}
BOOST_HELPER_TREE = '98f75b07bdab1080c9470eb115836035d7142397'
GNU_PORT_TREES = {
    'libiconv': '1f92b7d29ce3243d3d51e07686869eca63ece88a',
    'gettext-libintl': '25450f3473f6c62f28af9702a772d8b48a6170b7',
    'gettext': '0915f060ea0fb91c5a2356f2171de0a714e79437',
}
MSYS_PACKAGES = (
    'autoconf-wrapper', 'autoconf2.71', 'automake-wrapper', 'automake1.16', 'binutils',
    'libtool', 'make', 'pkgconf', 'which', 'gzip', 'coreutils', 'file',
    'gawk', 'grep', 'diffutils', 'sed',
)


def ensure_msys_tools(root):
    if os.name != 'nt':
        raise RuntimeError('The MSYS2/MSVC host check must run on Windows')
    bash = root / 'usr/bin/bash.exe'
    pacman = root / 'usr/bin/pacman.exe'
    if not bash.is_file() or not pacman.is_file():
        raise FileNotFoundError(f'Incomplete MSYS2 installation: {root}')
    env = dict(os.environ, MSYSTEM='MSYS', MSYS2_PATH_TYPE='inherit',
               WANT_AUTOCONF='2.71', WANT_AUTOMAKE='1.16')
    query = [str(pacman), '-Q', *MSYS_PACKAGES]
    result = subprocess.run(query, env=env, capture_output=True,
                            text=True, errors='replace')
    if result.returncode:
        print('Installing the required host tools with the existing MSYS2 package manager...', flush=True)
        subprocess.run([str(bash), '-lc',
                        'pacman -S --needed --noconfirm ' + ' '.join(MSYS_PACKAGES)],
                       env=env, check=True)
        result = subprocess.run(query, env=env, capture_output=True,
                                text=True, errors='replace', check=True)
    check = ('set -eu; for tool in autoconf automake libtool make pkgconf which '
             'gzip cp file gawk grep diff sed cygpath; do command -v "$tool" '
             '>/dev/null; done; test -f /usr/share/automake-1.16/compile')
    subprocess.run([str(bash), '--noprofile', '--norc', '-c', check], env=env, check=True)
    work = Path(__file__).resolve().parents[1] / 'build/release-022/host-tools-check'
    work.mkdir(parents=True, exist_ok=True)
    (work / 'probe.c').write_text('#include <stdio.h>\nint main(void) { return puts("MSVC/MSYS2 host check passed") < 0; }\n',
                                 encoding='utf-8', newline='\n')
    # Exercise exactly the GNU-style compiler wrapper needed by iconv/intl.
    for mode, flags in [('release', '-MT -O2'), ('debug', '-MTd -Od')]:
        print(f'Checking MSVC x64 {mode} through the Automake wrapper...', flush=True)
        commands = (f'set -eu; /usr/share/automake-1.16/compile cl.exe -nologo {flags} '
                    f'-c -o probe-{mode}.obj probe.c; '
                    f'/usr/share/automake-1.16/compile cl.exe -nologo {flags} '
                    f'-o probe-{mode}.exe probe-{mode}.obj')
        subprocess.run([str(bash), '--noprofile', '--norc', '-c', commands],
                       cwd=work, env=env, check=True)
        exe = work / f'probe-{mode}.exe'
        data = exe.read_bytes()
        pe = struct.unpack_from('<I', data, 0x3c)[0]
        if data[pe:pe + 4] != b'PE\0\0' or struct.unpack_from('<H', data, pe + 4)[0] != 0x8664:
            raise ValueError('The host compiler did not produce an x64 Windows executable')
        subprocess.run([str(exe)], check=True)
    report = {'msys_root': str(root), 'packages': result.stdout.splitlines(),
              'msvc_x64_compile_link_run': ['release', 'debug']}
    (work / 'verification.json').write_text(json.dumps(report, indent=2) + '\n',
                                           encoding='utf-8', newline='\n')
    print('Local MSYS2 tools and MSVC x64 compiler wrapper verified.', flush=True)


def prepare_msys_overlays(vcpkg, overlays):
    host = overlays / 'colobot-msys-tools'
    host.mkdir(parents=True, exist_ok=True)
    metadata = {'name': 'colobot-msys-tools', 'version': '0.2.2',
                'description': 'Use verified local MSYS2 tools for legacy GNU ports',
                'license': 'GPL-3.0-or-later'}
    (host / 'vcpkg.json').write_text(json.dumps(metadata, indent=2) + '\n',
                                    encoding='utf-8', newline='\n')
    (host / 'portfile.cmake').write_text(
        'set(VCPKG_POLICY_EMPTY_PACKAGE enabled)\n'
        'file(INSTALL "${CURRENT_PORT_DIR}/vcpkg-port-config.cmake" '
        'DESTINATION "${CURRENT_PACKAGES_DIR}/share/${PORT}")\n',
        encoding='utf-8', newline='\n')
    shutil.copyfile(Path(__file__).with_name('vcpkg_022_msys_config.cmake'),
                    host / 'vcpkg-port-config.cmake')
    for name, tree in GNU_PORT_TREES.items():
        blob = subprocess.check_output(['git', '-C', str(vcpkg), 'archive', tree])
        port = overlays / name
        port.mkdir(parents=True, exist_ok=True)
        with tarfile.open(fileobj=io.BytesIO(blob)) as archive:
            archive.extractall(port, filter='data')
        manifest = port / 'vcpkg.json'
        metadata = json.loads(manifest.read_text(encoding='utf-8'))
        metadata.setdefault('dependencies', []).append({'name': 'colobot-msys-tools', 'host': True})
        metadata['port-version'] = metadata.get('port-version', 0) + 1
        manifest.write_text(json.dumps(metadata, indent=2) + '\n',
                            encoding='utf-8', newline='\n')
    print('GNU port overlays ready: all iconv/gettext builds use the local MSYS2 tools.', flush=True)


def report_library_failure(vcpkg):
    manifest_log = vcpkg.parent / 'engine/vcpkg-manifest-install.log'
    if not manifest_log.is_file():
        return
    matches = re.findall(r'error: building ([a-z0-9-]+):',
                         manifest_log.read_text(encoding='utf-8', errors='replace'))
    if not matches:
        return
    port = matches[-1]
    logs = [path for path in (vcpkg / 'buildtrees' / port).rglob('*.log')
            if path.name.endswith(('-out.log', '-err.log')) and path.stat().st_size]
    logs.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    pattern = re.compile(r'\b(error|errore|fatal|failed|cannot|impossibile)\b', re.I)
    print(f'\nRecent diagnostic output for {port}:', flush=True)
    for path in logs[:4]:
        with path.open('rb') as stream:
            stream.seek(max(0, path.stat().st_size - 4000000))
            lines = stream.read().decode('utf-8', errors='replace').splitlines()
        found = [index for index, line in enumerate(lines) if pattern.search(line)]
        indices = sorted({i for index in found[-4:] for i in range(max(0, index - 2), min(len(lines), index + 6))})
        excerpt = '\n'.join(lines[index] for index in indices) if indices else '\n'.join(lines[-25:])
        print(f'\n{path}\n{excerpt[-3500:]}', flush=True)


def prepare_boost_overlay(vcpkg, overlays):
    # Start from the exact port used by the release; leave the registry intact.
    blob = subprocess.check_output(
        ['git', '-C', str(vcpkg), 'archive', BOOST_HELPER_TREE])
    port = overlays / 'boost-modular-build-helper'
    port.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(blob)) as archive:
        archive.extractall(port, filter='data')
    helper = port / 'boost-modular-build.cmake'
    text = helper.read_text(encoding='utf-8')
    anchor = '        string(REPLACE "-vc143-" "-vc140-" NEW_FILENAME ${NEW_FILENAME}) # To merge VS2022 and VS2015 binaries\n'
    if text.count(anchor) != 1:
        raise ValueError('Unexpected pinned Boost library naming rules')
    addition = '        string(REPLACE "-vc144-" "-vc140-" NEW_FILENAME ${NEW_FILENAME}) # MSVC 14.4 uses the same vcpkg library names\n'
    helper.write_text(text.replace(anchor, anchor + addition),
                      encoding='utf-8', newline='\n')
    manifest = port / 'vcpkg.json'
    metadata = json.loads(manifest.read_text(encoding='utf-8'))
    # Rebuild dependents such as Atomic instead of reusing the old vc144 names.
    metadata['port-version'] = 4
    manifest.write_text(json.dumps(metadata, indent=2) + '\n',
                        encoding='utf-8', newline='\n')
    print('Boost compatibility overlay ready: normalize vc144 library names.', flush=True)
    return port


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha512').hexdigest()


def cache_tool(tool, downloads):
    name = tool.attrib['name']
    url = MIRRORS.get(name, tool.findtext('url'))
    archive = tool.findtext('archiveName') or url.rsplit('/', 1)[-1]
    expected = tool.findtext('sha512').strip().lower()
    if len(expected) != 128 or Path(archive).name != archive:
        raise ValueError(f'Invalid pinned metadata for {name}')
    target = downloads / archive
    if target.is_file() and digest(target) == expected:
        print(f'Cached and verified: {name}', flush=True)
        return target
    partial = target.with_name(target.name + '.colobot-part')
    for attempt in range(3):
        try:
            print(f'Downloading: {name}', flush=True)
            with urllib.request.urlopen(url, timeout=60) as response, partial.open('wb') as stream:
                while block := response.read(1024 * 1024):
                    stream.write(block)
            if digest(partial) != expected:
                raise ValueError(f'SHA512 mismatch: {name}')
            partial.replace(target)
            print(f'Downloaded and verified: {name}', flush=True)
            return target
        except (OSError, ValueError):
            partial.unlink(missing_ok=True)
            if attempt == 2:
                raise
            time.sleep(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vcpkg', type=Path, required=True)
    parser.add_argument('--report-failure', action='store_true',
                        help='print the latest failed library logs without changing the build')
    parser.add_argument('--msys', type=Path,
                        help='verify/install local Windows host tools before preparing the build')
    parser.add_argument('--overlays', type=Path,
                        default=Path(__file__).resolve().parents[1] / 'build/release-022/overlay-ports')
    args = parser.parse_args()
    if args.report_failure:
        report_library_failure(args.vcpkg)
        return
    if args.msys:
        ensure_msys_tools(args.msys)
    tools = ET.parse(args.vcpkg / 'scripts/vcpkgTools.xml').getroot()
    selected = [next(tool for tool in tools.findall('tool')
                     if tool.attrib.get('name') == name
                     and tool.attrib.get('os') == 'windows') for name in TOOLS]
    downloads = args.vcpkg / 'downloads'
    downloads.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(lambda tool: cache_tool(tool, downloads), selected))
    print(f'Windows build tool archives ready: {len(results)} verified.', flush=True)
    prepare_boost_overlay(args.vcpkg, args.overlays)
    prepare_msys_overlays(args.vcpkg, args.overlays)


if __name__ == '__main__':
    main()
