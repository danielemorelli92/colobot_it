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
goto usage

:configure
set "COLOBOT022_ROOT=C:\colobot-build-022"
set "COLOBOT022_PYTHON=C:\msys64\ucrt64\bin\python.exe"
set "COLOBOT022_PROJECT=%~dp0.."
set "PATH=%PATH%;C:\msys64\usr\bin;C:\msys64\ucrt64\bin"
set "PYTHONUTF8=1"
set "PYTHONPATH=%COLOBOT022_PROJECT%\build\python-deps"
set "VCPKG_FORCE_DOWNLOADED_BINARIES=1"
set "VCPKG_MAX_CONCURRENCY=2"
if not exist "%COLOBOT022_ROOT%\vcpkg\vcpkg.exe" (
    echo Missing vcpkg at %COLOBOT022_ROOT%\vcpkg
    exit /b 1
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
cmake -G Ninja ^
  -S "%COLOBOT022_PROJECT%\build\release-022\prepared\colobot" ^
  -B "%COLOBOT022_ROOT%\engine" ^
  -DCMAKE_MAKE_PROGRAM:FILEPATH="%COLOBOT022_NINJA%" ^
  -DCMAKE_C_COMPILER=cl.exe -DCMAKE_CXX_COMPILER=cl.exe ^
  -DCMAKE_TOOLCHAIN_FILE="%COLOBOT022_ROOT%/vcpkg/scripts/buildsystems/vcpkg.cmake" ^
  -DVCPKG_TARGET_TRIPLET=x64-windows-static ^
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

:usage
echo Usage: tools\build_windows_022.cmd configure
echo        tools\build_windows_022.cmd build
exit /b 1
