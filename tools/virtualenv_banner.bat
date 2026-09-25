@echo off
:: ============================================================
::  scripts\virtualenv_banner.bat — Developer shell welcome banner
::
::  CONTRACT:
::    - Called by .shell_init.bat inside the spawned Developer Shell
::    - PROJECT_DIR, PORTABLE_DIR and VENV_DIR are already set
::      in the child shell environment before this is called
::    - Do NOT wrap in SETLOCAL/ENDLOCAL
:: ============================================================

echo.
echo ============================================================
echo   Developer Shell
echo ============================================================
echo   Python  : %PORTABLE_DIR%
echo   Venv    : %VENV_DIR%
echo   Project : %PROJECT_DIR%
echo ============================================================
echo   Useful commands:
echo     pip install -e .           Install / refresh dependencies
echo     python -m my_package       Run the application
echo     pip list                   List installed packages
echo     deactivate                 Exit the virtual environment
echo     python -m notebook         Launch jupyter notebook
echo     python -m ipykernel install --user --name=my-package --display-name "Python (.venv my-package)"
echo     import sys; print(sys.executable) - To verify path of .venv
echo ============================================================
echo.
