@echo off
REM Start LensFit in development mode: backend + frontend
REM
REM This is a thin Windows wrapper around scripts/dev.py, which is the canonical
REM cross-platform launcher.  Run `python scripts/dev.py` for full options.

setlocal
set "SCRIPT_DIR=%~dp0"
python "%SCRIPT_DIR%dev.py" %*
endlocal
