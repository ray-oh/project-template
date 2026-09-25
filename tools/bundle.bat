@echo off
SETLOCAL ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION

:: ── Project root derives from this file's location ───────────────────────
SET PROJECT_DIR=%~dp0..
FOR %%I IN ("!PROJECT_DIR!") DO SET PROJECT_DIR=%%~fI

:: ── Load app identity from .env.default ───────────────────────────────────
SET _DEFAULT_ENV=%~dp0.env.default

IF NOT EXIST "!_DEFAULT_ENV!" (
    echo [ERROR] scripts\.env.default not found.
    echo         Ensure scripts\.env.default is committed to the repo.
    pause & exit /b 1
)

FOR /F "usebackq tokens=1,* delims==" %%A IN ("!_DEFAULT_ENV!") DO (
    SET _LINE=%%A
    IF NOT "!_LINE:~0,1!"=="#" (
        SET "%%A=%%B"
    )
)

:: ── Load all paths from AppData\.env ─────────────────────────────────────
CALL "%~dp0load_env.bat"
IF NOT "!ENV_LOAD_OK!"=="1" (
    echo [ERROR] Could not load user environment.
    echo         Run launch.bat first to complete setup.
    pause & exit /b 1
)

:: ── Guards ────────────────────────────────────────────────────────────────
IF NOT EXIST "!PORTABLE_DIR!\python.exe" (
    echo [ERROR] Portable Python not found at: !PORTABLE_DIR!
    echo         Run launch.bat first to complete setup.
    pause & exit /b 1
)

IF NOT EXIST "!VENV_DIR!\Scripts\activate.bat" (
    echo [ERROR] Venv not found at: !VENV_DIR!
    echo         Run launch.bat first to complete setup.
    pause & exit /b 1
)

IF NOT EXIST "!PROJECT_DIR!\tools\bundle_generator.py" (
    echo [ERROR] tools\bundle_generator.py not found.
    echo         Ensure the bundle generator exists in the tools\ folder.
    pause & exit /b 1
)

:: ── Activate venv and run bundle generator ────────────────────────────────
SET PATH=!PORTABLE_DIR!;!PORTABLE_DIR!\Scripts;!PATH!
CALL "!VENV_DIR!\Scripts\activate.bat"

IF !ERRORLEVEL! NEQ 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause & exit /b 1
)

echo [INFO]  Generating code bundle...
python "!PROJECT_DIR!\tools\bundle_generator.py"

IF !ERRORLEVEL! NEQ 0 (
    echo [ERROR] Bundle generation failed.
    pause & exit /b 1
)

echo.
echo [INFO]  Done. Press any key to exit.
pause >nul

ENDLOCAL
