@echo off
setlocal
rem Run from an x64 Visual Studio 2022 Developer Command Prompt.
if /i not "%VSCMD_ARG_TGT_ARCH%"=="x64" (
    echo Open the x64 Native Tools Command Prompt for VS 2022 first.
    exit /b 1
)
if "%~1"=="" goto usage
if /i "%~1"=="configure" goto configure
if /i "%~1"=="build" goto build
if /i "%~1"=="all" goto all
goto usage

:all
call "%~f0" configure
if errorlevel 1 exit /b 1
call "%~f0" build
exit /b %errorlevel%

:configure
set "COLOBOT022_ROOT=C:\colobot-build-022"
set "COLOBOT022_PYTHON=C:\msys64\ucrt64\bin\python.exe"
set "COLOBOT022_PROJECT=%~dp0.."
set "PATH=%PATH%;C:\msys64\usr\bin;C:\msys64\ucrt64\bin"
set "PYTHONUTF8=1"
set "PYTHONPATH=%COLOBOT022_PROJECT%\build\python-deps"
set "VCPKG_FORCE_DOWNLOADED_BINARIES=1"
set "VCPKG_MAX_CONCURRENCY=2"
call :setup_pkgconfig
if errorlevel 1 exit /b 1
if not exist "%COLOBOT022_ROOT%\vcpkg\vcpkg.exe" (
    echo Missing vcpkg at %COLOBOT022_ROOT%\vcpkg
    exit /b 1
)
rem The 2023 executable rejects MSVC 14.4; keep its ports but update the tool.
"%COLOBOT022_ROOT%\vcpkg\vcpkg.exe" version | findstr /c:"2024-06-10-" >nul
if errorlevel 1 (
    echo Updating the vcpkg executable for MSVC 14.4 support...
    "%COLOBOT022_ROOT%\vcpkg\scripts\tls12-download.exe" github.com /microsoft/vcpkg-tool/releases/download/2024-06-10/vcpkg.exe "%COLOBOT022_ROOT%\vcpkg\vcpkg-2024-06-10.exe"
    if errorlevel 1 exit /b 1
    "%COLOBOT022_PYTHON%" -c "import hashlib,sys; from pathlib import Path; digest=hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(); sys.exit(0 if digest=='39f45d17cd4d2139fccd4da67c33d141cd384f3a781c5e6239283482fa568107' else 'vcpkg download checksum mismatch')" "%COLOBOT022_ROOT%\vcpkg\vcpkg-2024-06-10.exe"
    if errorlevel 1 exit /b 1
    move /y "%COLOBOT022_ROOT%\vcpkg\vcpkg-2024-06-10.exe" "%COLOBOT022_ROOT%\vcpkg\vcpkg.exe" >nul
    if errorlevel 1 exit /b 1
)
rem Manifest overrides refer to historical port trees absent in a shallow clone.
for /f "delims=" %%S in ('git -C "%COLOBOT022_ROOT%\vcpkg" rev-parse --is-shallow-repository') do (
    if /i "%%S"=="true" (
        echo Downloading vcpkg history required by the pinned library versions...
        git -C "%COLOBOT022_ROOT%\vcpkg" fetch --unshallow https://github.com/microsoft/vcpkg.git f6a5d4e8eb7476b8d7fc12a56dff300c1c986131
        if errorlevel 1 exit /b 1
    )
)
set "COLOBOT022_NINJA="
for /f "delims=" %%N in ('where ninja.exe 2^>nul') do if not defined COLOBOT022_NINJA set "COLOBOT022_NINJA=%%N"
if not defined COLOBOT022_NINJA (
    echo Ninja was not found. Open the x64 Visual Studio tools prompt.
    exit /b 1
)
if not exist "%COLOBOT022_PROJECT%\build\python-deps\polib.py" (
    "%COLOBOT022_PYTHON%" -m pip install --target "%COLOBOT022_PROJECT%\build\python-deps" -r "%COLOBOT022_PROJECT%\tools\requirements.txt"
    if errorlevel 1 exit /b 1
)
"%COLOBOT022_PYTHON%" "%COLOBOT022_PROJECT%\tools\prepare_022.py" --reuse
if errorlevel 1 exit /b 1
"%COLOBOT022_PYTHON%" "%COLOBOT022_PROJECT%\tools\prepare_windows_022_tools.py" --vcpkg "%COLOBOT022_ROOT%\vcpkg"
if errorlevel 1 exit /b 1
cmake -G Ninja ^
  -S "%COLOBOT022_PROJECT%\build\release-022\prepared\colobot" ^
  -B "%COLOBOT022_ROOT%\engine" ^
  -DCMAKE_MAKE_PROGRAM:FILEPATH="%COLOBOT022_NINJA%" ^
  -DCMAKE_C_COMPILER=cl.exe -DCMAKE_CXX_COMPILER=cl.exe ^
  -DCMAKE_TOOLCHAIN_FILE="%COLOBOT022_ROOT%/vcpkg/scripts/buildsystems/vcpkg.cmake" ^
  -DVCPKG_TARGET_TRIPLET=x64-windows-static ^
  -DVCPKG_OVERLAY_PORTS:PATH="%COLOBOT022_PROJECT%/build/release-022/overlay-ports" ^
  -DUSE_STATIC_RUNTIME=ON -DCBOT_STATIC=ON -DBOOST_STATIC=ON ^
  -DGLEW_STATIC=ON -DSNDFILE_STATIC=ON ^
  -DCMAKE_BUILD_TYPE=Release -DDEV_BUILD=OFF -DOFFICIAL_COLOBOT_BUILD=OFF ^
  -DPORTABLE=ON -DPORTABLE_SAVES=OFF -DHIDE_CONSOLE=ON ^
  -DTOOLS=OFF -DTESTS=OFF -DDESKTOP=ON ^
  -DGETTEXT_MSGFMT_EXECUTABLE=C:/msys64/ucrt64/bin/msgfmt.exe ^
  -DGETTEXT_MSGMERGE_EXECUTABLE=C:/msys64/ucrt64/bin/msgmerge.exe ^
  -DCMAKE_INSTALL_PREFIX="%COLOBOT022_ROOT%/install"
if errorlevel 1 exit /b 1
cmake -G Ninja ^
  -S "%COLOBOT022_PROJECT%\build\release-022\prepared\colobot-data" ^
  -B "%COLOBOT022_ROOT%\data" ^
  -DCMAKE_MAKE_PROGRAM:FILEPATH="%COLOBOT022_NINJA%" ^
  -DCMAKE_C_COMPILER=cl.exe -DCMAKE_CXX_COMPILER=cl.exe ^
  -DPython3_EXECUTABLE="%COLOBOT022_PYTHON%" ^
  -DTRANSLATIONS=ON -DMUSIC=OFF ^
  -DCOLOBOT_INSTALL_DATA_DIR="%COLOBOT022_ROOT%/install/data"
if errorlevel 1 exit /b 1
echo Configuration complete. Next: tools\build_windows_022.cmd build
exit /b 0

:build
set "COLOBOT022_ROOT=C:\colobot-build-022"
set "COLOBOT022_PROJECT=%~dp0.."
set "COLOBOT022_PYTHON=C:\msys64\ucrt64\bin\python.exe"
set "PATH=%PATH%;C:\msys64\usr\bin;C:\msys64\ucrt64\bin"
set "PYTHONUTF8=1"
set "PYTHONPATH=%COLOBOT022_PROJECT%\build\python-deps"
call :setup_pkgconfig
if errorlevel 1 exit /b 1
cmake --build "%COLOBOT022_ROOT%\engine" --parallel 2
if errorlevel 1 exit /b 1
cmake --build "%COLOBOT022_ROOT%\data" --parallel 2
if errorlevel 1 exit /b 1
"%COLOBOT022_PYTHON%" "%COLOBOT022_PROJECT%\build\release-022\prepared\translation\tools\test_complete_data.py" --build "%COLOBOT022_ROOT%\data" --source "%COLOBOT022_PROJECT%\build\release-022\prepared\colobot-data"
if errorlevel 1 exit /b 1
"%COLOBOT022_PYTHON%" "%COLOBOT022_PROJECT%\build\release-022\prepared\translation\tools\check_links.py" --data-build "%COLOBOT022_ROOT%\data"
if errorlevel 1 exit /b 1
cmake --install "%COLOBOT022_ROOT%\engine"
if errorlevel 1 exit /b 1
cmake --install "%COLOBOT022_ROOT%\data"
if errorlevel 1 exit /b 1
dumpbin /dependents "%COLOBOT022_ROOT%\install\colobot.exe"
if errorlevel 1 exit /b 1
echo Build installed in %COLOBOT022_ROOT%\install
echo Final packaging will reuse the original game's assets and music.
exit /b 0

:setup_pkgconfig
rem vcpkg supports a supplied pkg-config through this environment variable.
set "PKG_CONFIG=C:\msys64\ucrt64\bin\pkgconf.exe"
if not exist "%PKG_CONFIG%" (
    echo Missing %PKG_CONFIG%. Install mingw-w64-ucrt-x86_64-pkgconf in MSYS2.
    exit /b 1
)
if defined VCPKG_KEEP_ENV_VARS (
    set "VCPKG_KEEP_ENV_VARS=%VCPKG_KEEP_ENV_VARS%;PKG_CONFIG"
) else (
    set "VCPKG_KEEP_ENV_VARS=PKG_CONFIG"
)
echo Using installed pkg-config: %PKG_CONFIG%
"%PKG_CONFIG%" --version
exit /b %errorlevel%

:usage
echo Usage: tools\build_windows_022.cmd configure
echo        tools\build_windows_022.cmd build
echo        tools\build_windows_022.cmd all
exit /b 1
