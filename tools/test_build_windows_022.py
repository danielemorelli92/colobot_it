#!/usr/bin/env python3
"""Check build orchestration and failure handling without a Windows compiler."""
import contextlib
import hashlib
import io
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import build_windows_022 as driver


class WindowsBuildTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='colobot build check ')
        self.addCleanup(temporary.cleanup)
        base = Path(temporary.name)
        self.project, self.root, self.msys = base / 'project', base / 'build root', base / 'msys tools'
        for path, content in [
            (self.root / 'vcpkg/vcpkg.exe', b'original vcpkg'),
            (self.project / 'build/python-deps/polib.py', b''),
            (self.msys / 'ucrt64/bin/pkgconf.exe', b'local pkg-config'),
        ]:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        self.calls = []
        self.version = driver.VCPKG_TOOL_VERSION + '-test'
        self.shallow = 'false'
        self.failure = lambda args: False
        self.payload = b'MZ test vcpkg replacement'
        self.build = driver.WindowsBuild(self.project, self.root, self.msys,
                                        runner=self.run_command,
                                        environment={'VSCMD_ARG_TGT_ARCH': 'x64', 'PATH': 'existing-tools'})
        search = patch.object(driver.shutil, 'which', side_effect=lambda name, path: f'/visual studio tools/{name}.exe')
        search.start()
        self.addCleanup(search.stop)
        output = contextlib.redirect_stdout(io.StringIO())
        output.__enter__()
        self.addCleanup(output.__exit__, None, None, None)

    def run_command(self, args, env, check, **kwargs):
        self.calls.append((args, dict(env), kwargs))
        if self.failure(args):
            if check:
                raise subprocess.CalledProcessError(7, args)
            return subprocess.CompletedProcess(args, 7, '', '')
        if Path(args[0]).name == 'tls12-download.exe':
            Path(args[-1]).write_bytes(self.payload)
        stdout = ''
        if Path(args[0]).name == 'vcpkg.exe' and args[1:] == ['version']:
            stdout = self.version
        elif 'rev-parse' in args:
            stdout = self.shallow + '\n'
        return subprocess.CompletedProcess(args, 0, stdout, '')

    def commands(self):
        return [call[0] for call in self.calls]

    def test_all_orders_prepare_configure_build_checks_and_install(self):
        self.build.execute('all')
        sequence = []
        for args in self.commands():
            is_cmake = Path(args[0]).name == 'cmake.exe'
            if is_cmake and '-S' in args:
                sequence.append('configure ' + Path(args[args.index('-S') + 1]).name)
            elif is_cmake and '--build' in args:
                sequence.append('build ' + Path(args[args.index('--build') + 1]).name)
            elif is_cmake and '--install' in args:
                sequence.append('install ' + Path(args[args.index('--install') + 1]).name)
            else:
                sequence.extend(Path(arg).name for arg in args
                                if arg.endswith(('.py', 'dumpbin.exe')))
        self.assertEqual(sequence, [
            'prepare_022.py', 'prepare_windows_022_tools.py', 'configure colobot',
            'configure colobot-data', 'prepare_022.py', 'build engine', 'build data',
            'test_complete_data.py', 'check_links.py', 'install engine',
            'install data', 'dumpbin.exe',
        ])
        engine = next(args for args in self.commands() if '-DVCPKG_TARGET_TRIPLET=x64-windows-static' in args)
        for option in ['-DUSE_STATIC_RUNTIME=ON', '-DCBOT_STATIC=ON', '-DBOOST_STATIC=ON',
                       '-DGLEW_STATIC=ON', '-DSNDFILE_STATIC=ON', '-DDESKTOP=ON', '-DMUSIC=OFF']:
            self.assertTrue(any(option in args for args in self.commands()), option)
        self.assertIn('-DCMAKE_BUILD_TYPE=Release', engine)
        self.assertIn(f'-DCMAKE_INSTALL_PREFIX={(self.root / "install").as_posix()}', engine)
        for args in self.commands():
            if str(self.project / 'tools/prepare_022.py') in args:
                self.assertIn('--repair-data-newlines', args)
        for args, env, kwargs in self.calls:
            self.assertEqual(env['PKG_CONFIG'], str(self.msys / 'ucrt64/bin/pkgconf.exe'))
            self.assertEqual(env['COLOBOT022_MSYS_ROOT'], str(self.msys))
            self.assertIn('COLOBOT022_MSYS_ROOT', env['VCPKG_KEEP_ENV_VARS'].split(';'))
            self.assertEqual(env['VCPKG_FORCE_DOWNLOADED_BINARIES'], '1')

    def test_failed_host_preparation_stops_before_cmake(self):
        self.failure = lambda args: any(Path(arg).name == 'prepare_windows_022_tools.py' for arg in args)
        with self.assertRaises(subprocess.CalledProcessError):
            self.build.execute('all')
        self.assertFalse(any(Path(args[0]).name == 'cmake.exe' for args in self.commands()))

    def test_failed_configuration_prints_diagnostics_and_never_builds(self):
        self.failure = lambda args: '-S' in args and str(self.build.prepared / 'colobot') in args
        with self.assertRaises(subprocess.CalledProcessError) as caught:
            self.build.execute('all')
        self.assertEqual(caught.exception.returncode, 7)
        self.assertIn('--report-failure', self.commands()[-1])
        self.assertFalse(any('--build' in args for args in self.commands()))

    def test_failed_engine_build_stops_before_data_and_install(self):
        self.failure = lambda args: '--build' in args
        with self.assertRaises(subprocess.CalledProcessError):
            self.build.execute('build')
        self.assertFalse(any('--install' in args for args in self.commands()))
        self.assertEqual(sum('--build' in args for args in self.commands()), 1)

    def test_rejected_download_keeps_original_vcpkg(self):
        self.version = '2023-06-15-old'
        with self.assertRaisesRegex(RuntimeError, 'checksum mismatch'):
            self.build.execute('all')
        self.assertEqual((self.root / 'vcpkg/vcpkg.exe').read_bytes(), b'original vcpkg')
        self.assertFalse(any('-S' in args for args in self.commands()))

    def test_verified_tool_update_and_full_history_fetch(self):
        self.version, self.shallow = '2023-06-15-old', 'true'
        with patch.object(driver, 'VCPKG_TOOL_SHA256', hashlib.sha256(self.payload).hexdigest()):
            self.build.execute('configure')
        self.assertEqual((self.root / 'vcpkg/vcpkg.exe').read_bytes(), self.payload)
        fetch = next(args for args in self.commands() if '--unshallow' in args)
        self.assertEqual(fetch[-1], driver.VCPKG_REF)

    def test_non_x64_prompt_stops_before_running_commands(self):
        self.build.env['VSCMD_ARG_TGT_ARCH'] = 'x86'
        with self.assertRaisesRegex(RuntimeError, 'x64 Native Tools'):
            self.build.execute('all')
        self.assertFalse(self.calls)

    def test_build_only_reuses_prepared_installation(self):
        self.build.execute('build')
        self.assertFalse(any('-S' in args or 'fetch' in args for args in self.commands()))
        self.assertTrue(any('--repair-data-newlines' in args for args in self.commands()))
        self.assertEqual(Path(self.commands()[-1][0]).name, 'dumpbin.exe')


if __name__ == '__main__':
    unittest.main()
