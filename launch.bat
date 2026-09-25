@echo off
SETLOCAL ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION

:: ── Project root ──────────────────────────────────────────────────────────
SET PROJECT_DIR=%~dp0
IF "!PROJECT_DIR:~-1!"=="\" SET PROJECT_DIR=!PROJECT_DIR:~0,-1!

SET BOOT_PYTHON=!PROJECT_DIR!\tools\boot\python.exe

:: ── Load app identity from .env.default ───────────────────────────────────
SET _DEFAULT_ENV=!PROJECT_DIR!\tools\.env.default

IF NOT EXIST "!_DEFAULT_ENV!" (
    echo [ERROR] tools\.env.default not found.
    echo         Ensure tools\.env.default is committed to the repo.
    pause & exit /b 1
)

FOR /F "usebackq tokens=1,* delims==" %%A IN ("!_DEFAULT_ENV!") DO (
    SET _LINE=%%A
    IF NOT "!_LINE:~0,1!"=="#" (
        SET "%%A=%%B"
    )
)

:: ── Derive venv Python path from loaded APP_AUTHOR and APP_NAME ───────────
SET VENV_PYTHON=%LOCALAPPDATA%\!APP_AUTHOR!\!APP_NAME!\.venv\scripts\python.exe

:: ── If venv exists, launch directly ──────────────────────────────────────
IF EXIST "!VENV_PYTHON!" (
    echo [INFO]  Using venv Python.
    "!VENV_PYTHON!" "!PROJECT_DIR!\tools\run.py"
    exit /b %ERRORLEVEL%
)

:: ── Venv not ready — run bootstrap ───────────────────────────────────────
IF NOT EXIST "!BOOT_PYTHON!" (
    echo [ERROR] tools\boot\python.exe not found.
    echo         Ensure the boot interpreter is present in tools\boot\
    pause
    exit /b 1
)

echo [INFO]  First run detected. Running setup for this user...
"!BOOT_PYTHON!" "!PROJECT_DIR!\tools\bootstrap.py"
IF !ERRORLEVEL! NEQ 0 (pause & exit /b 1)

:: ── Re-derive VENV_PYTHON after bootstrap ────────────────────────────────
SET VENV_PYTHON=%LOCALAPPDATA%\!APP_AUTHOR!\!APP_NAME!\.venv\Scripts\python.exe

echo.
echo [INFO]  Launching application...
"!VENV_PYTHON!" "!PROJECT_DIR!\tools\run.py"
ENDLOCAL
