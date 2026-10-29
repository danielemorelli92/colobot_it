#!/usr/bin/env python3
"""Configure, build and install the native Italian MSVC x64 release."""
import argparse
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
VCPKG_REF = 'f6a5d4e8eb7476b8d7fc12a56dff300c1c986131'
VCPKG_TOOL_VERSION = '2024-06-10'
VCPKG_TOOL_SHA256 = '39f45d17cd4d2139fccd4da67c33d141cd384f3a781c5e6239283482fa568107'


class WindowsBuild:
    def __init__(self, project=ROOT, root=Path('C:/colobot-build-022'),
                 msys=Path('C:/msys64'), runner=None, environment=None):
        self.project = project.resolve()
        self.root = root.resolve()
        self.msys = msys.resolve()
        self.python = Path(sys.executable)
        self.runner = runner or subprocess.run
        self.env = dict(os.environ if environment is None else environment)
        self.prepared = self.project / 'build/release-022/prepared'
        self.vcpkg = self.root / 'vcpkg'

    def run(self, *args, **kwargs):
        return self.runner([str(arg) for arg in args], env=self.env,
                           check=kwargs.pop('check', True), **kwargs)

    def setup(self):
        if self.env.get('VSCMD_ARG_TGT_ARCH', '').lower() != 'x64':
            raise RuntimeError('Open the x64 Native Tools Command Prompt for VS 2022 first.')
        self.env['PATH'] = os.pathsep.join(
            [self.env.get('PATH', ''), str(self.msys / 'usr/bin'), str(self.msys / 'ucrt64/bin')])
        self.env['PYTHONUTF8'] = '1'
        self.env['PYTHONPATH'] = str(self.project / 'build/python-deps')
        self.env['VCPKG_FORCE_DOWNLOADED_BINARIES'] = '1'
        self.env['VCPKG_MAX_CONCURRENCY'] = '2'
        pkgconfig = self.msys / 'ucrt64/bin/pkgconf.exe'
        if not pkgconfig.is_file():
            raise FileNotFoundError(f'Missing {pkgconfig}; install mingw-w64-ucrt-x86_64-pkgconf in MSYS2.')
        self.env['PKG_CONFIG'] = str(pkgconfig)
        self.env['COLOBOT022_MSYS_ROOT'] = str(self.msys)
        keep = self.env.get('VCPKG_KEEP_ENV_VARS', '').split(';')
        self.env['VCPKG_KEEP_ENV_VARS'] = ';'.join(dict.fromkeys(
            item for item in [*keep, 'PKG_CONFIG', 'COLOBOT022_MSYS_ROOT'] if item))
        for name in ('git', 'cmake', 'ninja', 'dumpbin'):
            tool = shutil.which(name, path=self.env['PATH'])
            if not tool:
                raise FileNotFoundError(f'{name} was not found in the Visual Studio x64 tools environment.')
            setattr(self, name, tool)
        print(f'Using installed pkg-config: {pkgconfig}', flush=True)
        self.run(pkgconfig, '--version')

    def configure(self):
        executable = self.vcpkg / 'vcpkg.exe'
        if not executable.is_file():
            raise FileNotFoundError(f'Missing {executable}')
        version = self.run(executable, 'version', capture_output=True, text=True, errors='replace').stdout
        if VCPKG_TOOL_VERSION + '-' not in version:
            print('Updating the vcpkg executable for MSVC 14.4 support...', flush=True)
            downloaded = self.vcpkg / f'vcpkg-{VCPKG_TOOL_VERSION}.exe'
            self.run(self.vcpkg / 'scripts/tls12-download.exe', 'github.com',
                     f'/microsoft/vcpkg-tool/releases/download/{VCPKG_TOOL_VERSION}/vcpkg.exe', downloaded)
            if hashlib.sha256(downloaded.read_bytes()).hexdigest() != VCPKG_TOOL_SHA256:
                raise RuntimeError('vcpkg download checksum mismatch')
            downloaded.replace(executable)
        shallow = self.run(self.git, '-C', self.vcpkg, 'rev-parse', '--is-shallow-repository',
                           capture_output=True, text=True, errors='replace').stdout.strip()
        if shallow == 'true':
            print('Downloading the vcpkg history required by the pinned library versions...', flush=True)
            self.run(self.git, '-C', self.vcpkg, 'fetch', '--unshallow',
                     'https://github.com/microsoft/vcpkg.git', VCPKG_REF)
        if not (self.project / 'build/python-deps/polib.py').is_file():
            self.run(self.python, '-m', 'pip', 'install', '--target',
                     self.project / 'build/python-deps', '-r', self.project / 'tools/requirements.txt')
        self.run(self.python, self.project / 'tools/prepare_022.py',
                 '--reuse', '--repair-data-newlines')
        self.run(self.python, self.project / 'tools/prepare_windows_022_tools.py',
                 '--vcpkg', self.vcpkg, '--msys', self.msys)
        print('Configuring native Italian Colobot 0.2.2 with MSVC x64...', flush=True)
        engine_options = {
            'CMAKE_MAKE_PROGRAM:FILEPATH': self.ninja,
            'CMAKE_C_COMPILER': 'cl.exe', 'CMAKE_CXX_COMPILER': 'cl.exe',
            'CMAKE_TOOLCHAIN_FILE': (self.vcpkg / 'scripts/buildsystems/vcpkg.cmake').as_posix(),
            'VCPKG_TARGET_TRIPLET': 'x64-windows-static',
            'VCPKG_OVERLAY_PORTS:PATH': (self.project / 'build/release-022/overlay-ports').as_posix(),
            'USE_STATIC_RUNTIME': 'ON', 'CBOT_STATIC': 'ON', 'BOOST_STATIC': 'ON',
            'GLEW_STATIC': 'ON', 'SNDFILE_STATIC': 'ON', 'CMAKE_BUILD_TYPE': 'Release',
            'DEV_BUILD': 'OFF', 'OFFICIAL_COLOBOT_BUILD': 'OFF', 'PORTABLE': 'ON',
            'PORTABLE_SAVES': 'OFF', 'HIDE_CONSOLE': 'ON', 'TOOLS': 'OFF',
            'TESTS': 'OFF', 'DESKTOP': 'ON',
            'GETTEXT_MSGFMT_EXECUTABLE': (self.msys / 'ucrt64/bin/msgfmt.exe').as_posix(),
            'GETTEXT_MSGMERGE_EXECUTABLE': (self.msys / 'ucrt64/bin/msgmerge.exe').as_posix(),
            'CMAKE_INSTALL_PREFIX': (self.root / 'install').as_posix(),
        }
        try:
            self.run(self.cmake, '-G', 'Ninja', '-S', self.prepared / 'colobot',
                     '-B', self.root / 'engine', *[f'-D{key}={value}' for key, value in engine_options.items()])
        except subprocess.CalledProcessError:
            self.run(self.python, self.project / 'tools/prepare_windows_022_tools.py',
                     '--vcpkg', self.vcpkg, '--report-failure', check=False)
            raise
        self.run(self.cmake, '-G', 'Ninja', '-S', self.prepared / 'colobot-data',
                 '-B', self.root / 'data', f'-DCMAKE_MAKE_PROGRAM:FILEPATH={self.ninja}',
                 '-DCMAKE_C_COMPILER=cl.exe', '-DCMAKE_CXX_COMPILER=cl.exe',
                 f'-DPython3_EXECUTABLE={self.python.as_posix()}',
                 '-DTRANSLATIONS=ON', '-DMUSIC=OFF',
                 f'-DCOLOBOT_INSTALL_DATA_DIR={(self.root / "install/data").as_posix()}')
        print('Configuration complete.', flush=True)

    def build(self):
        print('Building and checking the native Italian release...', flush=True)
        self.run(self.python, self.project / 'tools/prepare_022.py',
                 '--reuse', '--repair-data-newlines')
        self.run(self.cmake, '--build', self.root / 'engine', '--parallel', '2')
        self.run(self.cmake, '--build', self.root / 'data', '--parallel', '2')
        checks = self.prepared / 'translation/tools'
        self.run(self.python, checks / 'test_complete_data.py', '--build', self.root / 'data',
                 '--source', self.prepared / 'colobot-data')
        self.run(self.python, checks / 'check_links.py', '--data-build', self.root / 'data')
        self.run(self.cmake, '--install', self.root / 'engine')
        self.run(self.cmake, '--install', self.root / 'data')
        self.run(self.dumpbin, '/dependents', self.root / 'install/colobot.exe')
        print(f'Build installed in {self.root / "install"}', flush=True)
        print("Final packaging will reuse the original game's assets and music.", flush=True)

    def execute(self, phase):
        self.setup()
        if phase in ('configure', 'all'):
            self.configure()
        if phase in ('build', 'all'):
            self.build()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', type=str.lower, choices=('configure', 'build', 'all'))
    args = parser.parse_args()
    if os.name != 'nt':
        parser.error('Run this build on Windows from the Visual Studio x64 tools prompt.')
    try:
        WindowsBuild().execute(args.phase)
    except subprocess.CalledProcessError as error:
        for output in (error.stdout, error.stderr):
            if output:
                print(output, file=sys.stderr)
        print(f'Build stopped: {error.cmd[0]} exited with code {error.returncode}.', file=sys.stderr)
        return 1
    except (OSError, RuntimeError) as error:
        print(f'Build stopped: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
