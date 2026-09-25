@echo off
:: ============================================================
::  tools\load_env.bat — Load user environment from AppData\.env
::
::  CONTRACT:
::    - Do NOT wrap in SETLOCAL/ENDLOCAL — variables must
::      propagate back to the calling script's environment.
::    - Caller must already have ENABLEDELAYEDEXPANSION active.
::    - Sets ENV_LOAD_OK=1 on success, 0 on failure.
:: ============================================================

:: ── Step 1: Load app identity from committed config ──────────────────────
SET _DEFAULT_ENV=%~dp0.env.default

IF NOT EXIST "!_DEFAULT_ENV!" (
    echo [ERROR] tools\.env.default not found.
    echo         Ensure tools\.env.default is committed to the repo.
    SET ENV_LOAD_OK=0
    exit /b 1
)

FOR /F "usebackq tokens=1,* delims==" %%A IN ("!_DEFAULT_ENV!") DO (
    SET _LINE=%%A
    IF NOT "!_LINE:~0,1!"=="#" (
        SET "%%A=%%B"
    )
)

:: ── Step 2: Derive AppData .env path from loaded APP_AUTHOR and APP_NAME ─
SET _ENV_FILE=%LOCALAPPDATA%\!APP_AUTHOR!\!APP_NAME!\.env

IF NOT EXIST "!_ENV_FILE!" (
    echo [ERROR] User environment not found: !_ENV_FILE!
    echo         Run launch.bat first to generate it.
    SET ENV_LOAD_OK=0
    exit /b 1
)

:: ── Step 3: Load generated paths from AppData\.env ───────────────────────
FOR /F "usebackq tokens=1,* delims==" %%A IN ("!_ENV_FILE!") DO (
    SET _LINE=%%A
    IF NOT "!_LINE:~0,1!"=="#" (
        SET "%%A=%%B"
    )
)

SET ENV_LOAD_OK=1
