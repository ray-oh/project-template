# tools\bootstrap.py — run via: tools\boot\python.exe tools\bootstrap.py
#                         or via: launch.bat (which calls this automatically)
import sys
import subprocess
import zipfile
import shutil
import os
from pathlib import Path

# ── Bootstrap ─────────────────────────────────────────────────────────────
# __file__ is tools\bootstrap.py so parent is tools\
# env.py is in the same tools\ folder
sys.path.insert(0, str(Path(__file__).parent))
from env import (
    PROJECT_DIR, PYTHON_ZIP, PYTHON_ZIP_NAME,
    PORTABLE_DIR, VENV_DIR, ENTRY_PATH,
    BOOT_PYTHON,
    PYTHON_MIN, APP_NAME, APP_AUTHOR,
    write_env_file
)

# ── Helpers ───────────────────────────────────────────────────────────────

def info(msg: str)  -> None: print(f"[INFO]  {msg}")
def setup(msg: str) -> None: print(f"[SETUP] {msg}")
def error(msg: str) -> None: print(f"[ERROR] {msg}"); sys.exit(1)

def run(*cmd, **kwargs) -> None:
    """Run a subprocess command, exit on failure."""
    result = subprocess.run(cmd, **kwargs)
    if result.returncode != 0:
        error(f"Command failed: {' '.join(str(c) for c in cmd)}")

def venv_bin(name: str) -> Path:
    """Resolve a binary path inside the venv, cross-platform."""
    sub = "Scripts" if sys.platform == "win32" else "bin"
    ext = ".exe"    if sys.platform == "win32" else ""
    return VENV_DIR / sub / f"{name}{ext}"

# ── Write .env to AppData ─────────────────────────────────────────────────
# Must happen first so all bat files can read paths immediately after setup.

write_env_file()
info("Environment file written to AppData.")

# ── Step 0: Confirm boot interpreter is present ───────────────────────────

if not BOOT_PYTHON.exists():
    error(
        f"Boot interpreter not found: {BOOT_PYTHON}\n"
        f"        Ensure tools/boot/ contains a valid embeddable Python."
    )
info(f"Boot interpreter: {BOOT_PYTHON}")

# ── Step 1: Python version guard ──────────────────────────────────────────

major, minor = sys.version_info[:2]
if (major, minor) < PYTHON_MIN:
    error(f"Python {PYTHON_MIN[0]}.{PYTHON_MIN[1]}+ required. Found: {major}.{minor}")
info(f"Boot Python OK: {major}.{minor}")

# ── Step 2: Unpack portable Python zip ────────────────────────────────────

portable_python = PORTABLE_DIR / "python.exe"

if portable_python.exists():
    info(f"Portable Python already unpacked at {PORTABLE_DIR}")
else:
    if not PYTHON_ZIP.exists():
        error(
            f"Portable Python zip not found: {PYTHON_ZIP}\n"
            f"        Place {PYTHON_ZIP_NAME} in the project root and retry."
        )
    setup(f"Unpacking {PYTHON_ZIP_NAME} into {PORTABLE_DIR} ...")
    PORTABLE_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(PYTHON_ZIP, "r") as zf:
        zf.extractall(PORTABLE_DIR)
    if not portable_python.exists():
        error(
            "python.exe not found after unpack.\n"
            "        Ensure the zip contains python.exe at its root level."
        )
    setup("Portable Python unpacked successfully.")

# ── Step 3: Virtual environment ───────────────────────────────────────────

if venv_bin("python").exists():
    info(f"Virtual environment already exists at {VENV_DIR}")
else:
    if VENV_DIR.exists():
        setup("Removing incomplete virtual environment ...")
        shutil.rmtree(VENV_DIR)
        setup("Incomplete venv removed.")
    setup("Creating virtual environment from portable Python ...")
    setup(f"  Source : {portable_python}")
    setup(f"  Target : {VENV_DIR}")
    run(str(portable_python), "-m", "venv", str(VENV_DIR), "--copies")
    if not venv_bin("python").exists():
        error("Venv creation failed — python.exe not found inside venv.")
    setup("Virtual environment created.")

# ── Step 3b: Seed pip into venv via ensurepip ────────────────────────────
# Portable Python distributions may not seed pip into the venv automatically.

if not venv_bin("pip").exists():
    setup("Seeding pip into venv via ensurepip ...")
    run(str(venv_bin("python")), "-m", "ensurepip", "--upgrade")
    if not venv_bin("pip").exists():
        error("pip seeding failed — pip.exe not found after ensurepip.")
    setup("pip seeded successfully.")
else:
    info("pip already present in venv.")

# ── Step 4: Upgrade pip & setuptools ─────────────────────────────────────

setup("Upgrading pip and setuptools ...")
run(
    str(venv_bin("python")), "-m", "pip",
    "install", "--upgrade", "pip", "setuptools", "--quiet"
)
setup("pip and setuptools are up to date.")

# ── Step 5: Install package + dependencies ────────────────────────────────

setup("Installing package and dependencies ...")
run(
    str(venv_bin("python")), "-m", "pip",
    "install", "-e", str(PROJECT_DIR), "--quiet"
)
setup("All packages installed successfully.")

# ── Step 6: Playwright browsers (optional) ────────────────────────────────
# Only runs if playwright is listed in pyproject.toml dependencies.
# Marker file prevents re-downloading on subsequent runs.

marker = VENV_DIR / ".playwright_installed"
if marker.exists():
    info("Playwright browsers already installed.")
else:
    result = subprocess.run(
        [str(venv_bin("python")), "-m", "pip", "show", "playwright"],
        capture_output=True
    )
    if result.returncode == 0:
        setup("Installing Playwright browsers ...")
        run(str(venv_bin("playwright")), "install", "chromium")
        marker.touch()
        setup("Playwright browsers installed.")
    else:
        info("Playwright not in dependencies — skipping.")

# ── Step 7: Pre-create runtime directories ────────────────────────────────
# Delegates to venv Python where platformdirs is now installed.
# APP_NAME and APP_AUTHOR passed via environment to handle spaces safely.

setup("Initialising runtime directories ...")
run(
    str(venv_bin("python")), "-c",
    "import os; from platformdirs import PlatformDirs; "
    "d = PlatformDirs(os.environ['APP_NAME'], os.environ['APP_AUTHOR']); "
    "[p.mkdir(parents=True, exist_ok=True) for p in "
    "(d.user_config_path, d.user_data_path, d.user_log_path)]; "
    "print(f'  Config : {d.user_config_path}'); "
    "print(f'  Data   : {d.user_data_path}'); "
    "print(f'  Logs   : {d.user_log_path}')",
    env={**os.environ, "APP_NAME": APP_NAME, "APP_AUTHOR": APP_AUTHOR}
)
setup("Runtime directories ready.")

# ── Done ──────────────────────────────────────────────────────────────────

print()
print("=" * 60)
print("  Setup complete. Launch with: launch.bat")
print("=" * 60)
