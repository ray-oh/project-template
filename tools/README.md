
# 🧰 Python Project Template — Windows Scaffolding

A portable, self-contained Python project scaffold for Windows.
Designed for environments where system-level Python installation
is restricted or unavailable. One double-click is all it takes
to go from a clean machine to a running application.

---

## ✨ Features

- 📦 **Modern packaging** via `pyproject.toml` — no `setup.py`
- 🐍 **Portable Python** — unpacked from a `.zip`, no installer needed
- 🔁 **Idempotent setup** — safe to re-run at any time
- 🧪 **Editable install** — code changes reflected immediately
- 🖥️ **One-command launch** via `launch.bat`
- 🐚 **Pre-configured dev shell** via `virtualenv.bat`
- 🔌 **Optional Playwright** support built-in

---

## 📁 Project Structure

```text
project-root/
├── tools/
│   ├── .env.default           # ← ONLY file you edit to configure the template
│   ├── bootstrap.py           # Setup orchestrator — do not modify
│   ├── env.py                 # Path resolver — do not modify
│   ├── run.py                 # App launcher — do not modify
│   ├── load_env.bat           # Env loader — do not modify
│   ├── bundle.bat             # Code bundle generator
│   ├── virtualenv_banner.bat  # Dev shell banner
│   └── boot/                  # Committed boot interpreter — do not modify
│       └── python.exe
├── src/
│   └── my_package/            # Your application code (src layout)
│       ├── __init__.py
│       └── __main__.py
├── .gitignore
├── CLAUDE.md                  # Persistent context for Claude Code sessions
├── README.md
├── pyproject.toml             # Build config and dependency declaration
├── launch.bat                 # One-command setup + launch
└── virtualenv.bat             # Open a pre-activated developer terminal
```

---

## 🚀 Getting Started

### Step 1 — Provide a Portable Python

Download the **embeddable zip** for Windows from:
https://www.python.org/downloads/windows/

Place the `.zip` file in the **project root** (same folder as `launch.bat`).

> The zip must have `python.exe` at its root level — not nested inside a subfolder.

---

### Step 2 — Configure `tools\.env.default`

Open `tools\.env.default` and edit the four values:

```bat
APP_AUTHOR=YourOrg
APP_NAME=YourAppName
ENTRY_POINT=src/my_package/__main__.py
PYTHON_ZIP_NAME=python-3.12.0-embed-amd64.zip
```

All runtime paths (portable Python, venv, config, logs, data) are derived
automatically from these four values. This is the **only file** you edit
to configure the template identity.

---

### Step 3 — Configure `pyproject.toml`

Update the project metadata and dependencies:

```toml
[project]
name            = "my-package"
version         = "1.0.0"
description     = "Short description of what this project does"
requires-python = ">=3.12"

dependencies = [
    # "requests>=2.31.0",
    # "PyYAML>=6.0.1",
]

[project.scripts]
"my-package" = "my_package.__main__:main"

[tool.setuptools.packages.find]
where   = ["src"]
include = ["my_package*"]
```

---

### Step 4 — Run Setup

Double-click or run from a terminal:

```bat
launch.bat
```

This will automatically:

1. Read `tools\.env.default` to load app identity
2. Unpack portable Python from the zip into `%LOCALAPPDATA%\<APP_AUTHOR>\python\` (first run only)
3. Create a virtual environment under `%LOCALAPPDATA%\<APP_AUTHOR>\<APP_NAME>\.venv\`
4. Upgrade `pip` and `setuptools`
5. Install your package in editable mode (`pip install -e .`)
6. Install Playwright browsers if `playwright` is in your dependencies
7. Pre-create runtime directories (config, data, logs) via `platformdirs`
8. Launch the application

---

### Step 5 — Subsequent Runs

```bat
launch.bat
```

All setup steps are skipped automatically. The app launches directly.

---

## 🏗️ Adapting to Your Project

### Single-Package Project

```text
my-project/
├── tools/
│   ├── .env.default
│   └── virtualenv_banner.bat
├── src/
│   └── my_app/
│       ├── __init__.py
│       ├── __main__.py
│       ├── core.py
│       └── utils.py
├── .gitignore
├── pyproject.toml
├── launch.bat
└── virtualenv.bat
```

`tools\.env.default`:
```ini
APP_AUTHOR=YourOrg
APP_NAME=MyApp
ENTRY_POINT=src/my_app/__main__.py
PYTHON_ZIP_NAME=python-3.12.0-embed-amd64.zip
```

`pyproject.toml`:
```toml
[project]
name            = "my-app"
version         = "0.1.0"
description     = "My application"
requires-python = ">=3.12"
dependencies    = ["requests>=2.31.0"]

[project.scripts]
"my-app" = "my_app.__main__:main"

[tool.setuptools.packages.find]
where   = ["src"]
include = ["my_app*"]
```

---

### Multi-Package Project

Ideal when your project is split into a core library plus one or more
service or UI layers.

```text
my-project/
├── tools/
│   ├── .env.default
│   └── virtualenv_banner.bat
├── src/
│   ├── my_core/               # Shared library
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── utils.py
│   ├── my_service/            # Service / business logic layer
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   └── api.py
│   └── my_ui/                 # GUI layer (e.g. PySide6)
│       ├── __init__.py
│       └── app.py
├── .gitignore
├── pyproject.toml
├── launch.bat
└── virtualenv.bat
```

`tools\.env.default`:
```ini
APP_AUTHOR=YourOrg
APP_NAME=MyProject
ENTRY_POINT=src/my_service/__main__.py
PYTHON_ZIP_NAME=python-3.12.0-embed-amd64.zip
```

`pyproject.toml`:
```toml
[project]
name            = "my-project"
version         = "0.1.0"
description     = "My multi-package project"
requires-python = ">=3.12"
dependencies    = [
    "requests>=2.31.0",
    "PySide6>=6.7.0",
    "PyYAML>=6.0.1",
]

[project.scripts]
"my-project" = "my_service.__main__:main"

[tool.setuptools.packages.find]
where   = ["src"]
include = ["my_core*", "my_service*", "my_ui*"]
```

---

### Browser Automation Project (Playwright)

```text
my-project/
├── tools/
│   ├── .env.default
│   └── virtualenv_banner.bat
├── src/
│   └── my_bot/
│       ├── __init__.py
│       ├── __main__.py
│       ├── browser.py         # Playwright CDP / page logic
│       └── extractor.py       # BeautifulSoup DOM parsing
├── .gitignore
├── pyproject.toml
├── launch.bat
└── virtualenv.bat
```

`tools\.env.default`:
```ini
APP_AUTHOR=YourOrg
APP_NAME=MyBot
ENTRY_POINT=src/my_bot/__main__.py
PYTHON_ZIP_NAME=python-3.12.0-embed-amd64.zip
```

`pyproject.toml`:
```toml
[project]
name            = "my-bot"
version         = "0.1.0"
description     = "Browser automation bot"
requires-python = ">=3.12"
dependencies    = [
    "playwright>=1.44.0",
    "beautifulsoup4>=4.12.0",
    "requests>=2.31.0",
]

[project.scripts]
"my-bot" = "my_bot.__main__:main"

[tool.setuptools.packages.find]
where   = ["src"]
include = ["my_bot*"]
```

> Playwright browsers are installed automatically by `launch.bat`
> on first run when `playwright` is detected in the dependencies.
> A `.playwright_installed` marker file prevents re-downloading.

---

## 🛠️ Developer Shell

To open a terminal with the virtual environment pre-activated:

```bat
virtualenv.bat
```

This opens a new `cmd` window with:
- Python and `Scripts/` on the `PATH`
- The virtual environment activated
- The working directory set to the project root
- A banner showing key paths and useful commands

---

## 📦 Dependency Management

All dependencies are declared in `pyproject.toml` under `[project] dependencies`.
After adding or changing dependencies, sync the environment with:

```bat
pip install -e .
```

Or re-run to do a full refresh:

```bat
launch.bat
```

---

## 🚫 What to Exclude from Git

The provided `.gitignore` already covers all of the following:

| Path | Reason |
|------|--------|
| `*.egg-info/` | Auto-generated build metadata |
| `.venv/` | Virtual environment — always reproducible |
| `*.zip` | Large binary — keep out of version control |
| `__pycache__/` | Compiled bytecode |
| `.playwright_installed` | Local marker file |
| `tools\.shell_init.bat` | Generated at runtime — baked absolute paths |

> **Note:** `tools\boot\` must **not** be gitignored — the committed boot
> interpreter is required for first-run setup on machines without Python.

---

## ⚙️ Requirements

| Requirement | Minimum |
|-------------|---------|
| OS          | Windows (bat scripts) |
| Python      | 3.12+ (enforced by `bootstrap.py` and `pyproject.toml`) |
| pip         | Latest (auto-upgraded by `bootstrap.py`) |
| setuptools  | >= 68 (auto-upgraded by `bootstrap.py`) |

---

## 📝 Notes

> **Linux / macOS:** The `.bat` scripts are Windows-only. Equivalent `Makefile`
> or shell script support is not included but can be added following the same
> pattern — source a central `load_env.sh` and replicate the bootstrap steps.

> **Portable Python ZIP** must have `python.exe` at its root level (not nested
> in a subfolder) for the unpack logic in `bootstrap.py` to work correctly.

> **Runtime data** (venv, config, logs, data) is stored under
> `%LOCALAPPDATA%\<APP_AUTHOR>\<APP_NAME>\` — never inside the project tree.
> Safe for multi-user shared network drive deployments.

> **Editable install** means you never need to reinstall after changing source
> files. Only re-run `pip install -e .` when you add new packages or change
> `pyproject.toml`.

> **Claude Code users:** see `CLAUDE.md` for persistent session context,
> coding conventions, and rules specific to this project.
