#!/usr/bin/env bash
# Finds the first available Python and hands off to run.py
for py in python3 python; do
    if command -v "$py" &>/dev/null; then
        exec "$py" run.py
    fi
done
echo "[ERROR] Python not found. Install Python 3.12+ and retry."
exit 1
