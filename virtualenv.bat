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

:: ── Derive .env path from loaded APP_AUTHOR and APP_NAME ─────────────────
SET _ENV_FILE=%LOCALAPPDATA%\!APP_AUTHOR!\!APP_NAME!\.env

:: ── If .env missing run bootstrap first ──────────────────────────────────
IF NOT EXIST "!_ENV_FILE!" (
    echo [INFO]  User environment not found. Running setup first...
    IF NOT EXIST "!BOOT_PYTHON!" (
        echo [ERROR] tools\boot\python.exe not found.
        echo         Ensure the boot interpreter is present in tools\boot\
        pause & exit /b 1
    )
    "!BOOT_PYTHON!" "!PROJECT_DIR!\tools\bootstrap.py"
    IF !ERRORLEVEL! NEQ 0 (pause & exit /b 1)
)

:: ── Load all paths from AppData\.env ─────────────────────────────────────
CALL "!PROJECT_DIR!\tools\load_env.bat"
IF NOT "!ENV_LOAD_OK!"=="1" (
    echo [ERROR] Could not load user environment even after setup.
    pause & exit /b 1
)

:: ── Guards ────────────────────────────────────────────────────────────────
IF NOT EXIST "!PORTABLE_DIR!\python.exe" (
    echo [ERROR] Portable Python not found at: !PORTABLE_DIR!
    echo         Run launch.bat to repair setup.
    pause & exit /b 1
)

IF NOT EXIST "!VENV_DIR!\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found at: !VENV_DIR!
    echo         Run launch.bat to repair setup.
    pause & exit /b 1
)

:: ── Write shell init script ───────────────────────────────────────────────
:: This file is gitignored and overwritten fresh on every run.
:: It is intentionally not deleted — cmd /K cannot delete a file
:: it is currently executing (Windows file lock).
SET _INIT=!PROJECT_DIR!\tools\.shell_init.bat

(
    echo @echo off
    echo SET "PROJECT_DIR=!PROJECT_DIR!"
    echo SET "PORTABLE_DIR=!PORTABLE_DIR!"
    echo SET "VENV_DIR=!VENV_DIR!"
    echo SET "PATH=!PORTABLE_DIR!;!PORTABLE_DIR!\Scripts;!PATH!"
    echo CALL "!VENV_DIR!\Scripts\activate.bat"
    echo cd /d "!PROJECT_DIR!"
    echo CALL "!PROJECT_DIR!\tools\virtualenv_banner.bat"
) > "!_INIT!"

:: ── Open pre-activated developer shell ───────────────────────────────────
:: Double-quote the init path so cmd /K handles spaces in the path correctly
start "Developer Shell" cmd /K ""!_INIT!""

ENDLOCAL
