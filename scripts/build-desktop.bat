@echo off
REM Build OptiBench desktop application (sidecar + Tauri bundle)
REM
REM This is a thin Windows wrapper around scripts/build-desktop.py, which is the
REM canonical cross-platform build script.  Run `python scripts/build-desktop.py`
REM for full options.

setlocal
set "SCRIPT_DIR=%~dp0"
python "%SCRIPT_DIR%build-desktop.py" %*
endlocal
