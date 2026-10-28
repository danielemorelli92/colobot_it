#!/usr/bin/env python3
"""Cache checksum-verified Windows build tools for the pinned vcpkg release."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
from pathlib import Path
import time
import urllib.request
import xml.etree.ElementTree as ET


TOOLS = ('7zip', '7zip_msi', 'cmake', 'git', 'ninja', 'powershell-core')
# Same upstream archives and hashes; only the download host changes.
MIRRORS = {
    '7zip': 'https://github.com/ip7z/7zip/releases/download/21.07/7z2107-extra.7z',
    '7zip_msi': 'https://github.com/ip7z/7zip/releases/download/21.07/7z2107-x64.msi',
}


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


if __name__ == '__main__':
    main()
