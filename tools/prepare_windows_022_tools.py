#!/usr/bin/env python3
"""Prepare the Windows tool cache and pinned Boost compatibility overlay."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import io
import json
from pathlib import Path
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
    parser.add_argument('--overlays', type=Path,
                        default=Path(__file__).resolve().parents[1] / 'build/release-022/overlay-ports')
    args = parser.parse_args()
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


if __name__ == '__main__':
    main()
