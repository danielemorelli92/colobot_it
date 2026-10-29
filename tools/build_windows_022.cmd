@echo off
setlocal
set "PYTHONUTF8=1"
"C:\msys64\ucrt64\bin\python.exe" "%~dp0build_windows_022.py" %*
exit /b %errorlevel%
