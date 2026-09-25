# tools\run.py — launched by launch.bat via venv Python
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from env import PROJECT_DIR, VENV_DIR, ENTRY_POINT

venv_python = VENV_DIR / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")

# Guards
if not venv_python.exists():
    print("[ERROR] Virtual environment not found. Run: launch.bat")
    sys.exit(1)

entry = PROJECT_DIR / ENTRY_POINT
if not entry.exists():
    print(f"[ERROR] Entry point not found: {entry}")
    sys.exit(1)

print(f"[INFO]  Running {ENTRY_POINT} ...")
print("=" * 60)
subprocess.run(
    [str(venv_python), str(entry)],
    cwd=str(PROJECT_DIR)              # ← ensures app always runs from project root
)
