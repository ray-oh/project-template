# tools/bundle_generator.py
import os
import fnmatch
from pathlib import Path

# ================================================================================
# bundle_generator.py
# Bundles a project's directory tree + source files into a single .txt file
# for AI code review (e.g. Claude, MAIA), respecting .gitignore rules.
#
# HOW TO RUN:
#     python tools/bundle_generator.py        (from project root or anywhere)
#     scripts\bundle.bat                      (Windows convenience launcher)
#
# OUTPUT:
#     claude_code_bundle.txt — saved in the project root folder.
#
# TROUBLESHOOTING:
#     If a folder/file unexpectedly appears in the bundle:
#       1. Add its name to ALWAYS_EXCLUDE (exact name match), OR
#       2. Add its relative path to MANUAL_EXCLUDE (path prefix match), OR
#       3. Set DEBUG = True to trace every inclusion/exclusion decision.
# ================================================================================

# ─── CONFIGURATION ──────────────────────────────────────────────────────────────

# Always resolve project root from THIS file's location — never from cwd().
# tools/bundle_generator.py lives one level below the project root.
ROOT_DIR       = Path(__file__).resolve().parent.parent   # ← FIXED #1
OUTPUT_FILE    = ROOT_DIR / "claude_code_bundle.txt"
GITIGNORE_FILE = ROOT_DIR / ".gitignore"

# Extensions shown in the directory tree (includes binary types for visibility)
ALLOWED_EXTENSIONS = {
    ".py", ".md", ".json", ".yaml", ".yml", ".toml",
    ".ini", ".txt", ".env", ".bat", ".jinja", ".xml",
    ".bin", ".safetensors",  # shown in tree only — content not saved (too large / binary)
}

# Extensions whose content is written into the bundle
ALLOWED_EXTENSIONS_SAVE_CONTENT = {
    ".py", ".md", ".json", ".yaml", ".yml", ".toml",
    ".ini", ".txt", ".env", ".bat", ".jinja", ".xml",
}

MAX_FILE_SIZE_KB = 500   # Files larger than this are skipped
DEBUG            = False  # ← FIXED #5 — set True only when debugging exclusions

# ─── ALWAYS_EXCLUDE ─────────────────────────────────────────────────────────────
# Excluded by exact NAME — applies to files and folders anywhere in the tree.
ALWAYS_EXCLUDE = {
    ".git",
    "__pycache__",
    ".DS_Store",
    "venv",
    ".venv",                     # ← FIXED #4 — duplicate removed
    ".idea",
    ".vscode",
    "build",
    "dist",
    OUTPUT_FILE.name,            # exclude the output bundle itself
    "bundle_generator.py",       # ← FIXED #2 — exclude this script itself
    "pack_repo.py",              # legacy name aliases
    "claude_code_bundle.py",
    "python",
    ".ipynb_checkpoints",
    "raw_html.txt",
    "selectors_raw.txt",
}

# ─── MANUAL_EXCLUDE ─────────────────────────────────────────────────────────────
# Excluded by FULL RELATIVE PATH (forward-slash, case-insensitive).
# Both the path itself AND all its children are excluded.
# Format: relative/path/from/root
MANUAL_EXCLUDE = {
    #"tools",                     # ← FIXED #3 — exclude the tools/ folder itself
    "docs",
    "installation",
    "archive",
    "save",
    # ← FIXED #7 — removed all project-specific paths (autobot/, maia_autosave/)
    # Add your own project-specific exclusions here:
    # "my_folder",
}

# ─── AI PROMPT ──────────────────────────────────────────────────────────────────

AI_MESSAGE = '''
Act as a Principal Software Engineer with deep expertise in Python projects.

I have uploaded a full code bundle of my private repository.
Your task is to analyse it thoroughly and generate a production-ready CLAUDE.md file
that will be used as persistent context for future Claude Code sessions on this project.

---

## Instructions

1. ANALYSE the bundle carefully before writing anything:
   - Identify the project's purpose, architecture, and key workflows.
   - Infer the tech stack from imports, config files, and dependency files.
   - Note naming conventions, coding patterns, and structural decisions already in use.
   - Identify entry points, core modules, and any obvious TODOs or tech debt.

2. GENERATE a CLAUDE.md file with exactly these sections:

   ### 1. Project Overview
   What does this project do? What problem does it solve? What is its business value?

   ### 2. Tech Stack & Dependencies
   Languages, frameworks, libraries, and infrastructure inferred from the codebase.

   ### 3. Architecture Overview
   High-level structure: key directories, core modules, and how they interact.
   Include the directory tree if relevant.

   ### 4. Key Workflows
   Walk through 2-3 critical operational paths from start to finish.

   ### 5. Coding Conventions
   Naming rules, typing standards, import order, docstring style, error handling —
   based strictly on what you observe in the code, not generic best practices.

   ### 6. Common Commands
   Build, run, test, and lint commands inferred from Makefile, .bat, or config files.

   ### 7. Rules & Prohibitions
   Things Claude should NEVER do in this codebase (e.g. patterns already avoided,
   anti-patterns observed, sensitive areas to leave untouched).

   ### 8. Verification Instructions
   Steps Claude should follow to confirm its changes are correct before finishing.

---

## Constraints

- Base EVERY statement on evidence from the code bundle. Do NOT invent or assume.
- If something is genuinely unclear, write a short "> NOTE: ..." rather than guessing.
- Keep the output under 150 lines — be concise and scannable.
- Output ONLY the raw Markdown for CLAUDE.md. No preamble, no explanation.
- Do not include any section that has no evidence in the codebase.

## Style for markdown output
When generating any Markdown document output, do not display it directly in chat as rendering corrupts it when copied. 
Instead, deliver it as a Python script that writes the file to disk.  
Take care to replace any Fenced Code Block in the markdown content with "|||TEXT" for starting block and "|||" for closing block.

from pathlib import Path
content = r"""..."""
content = content.replace('|||', '"""')
Path("FILENAME.md").write_text(content, encoding="utf-8")
print(f"Written: {Path('FILENAME.md').resolve()}")

Use a raw string r'...' to preserve all formatting. Output the script only — no separate Markdown display. 
Script must run as-is from the project root. To prevent issues with chat window rendering messing the content, 
replace all triple single quotes in the content with '|||' — including the opening and closing delimiters.
'''

# ← FIXED #6 — AI_MESSAGE_OLD removed (dead code)

# ────────────────────────────────────────────────────────────────────────────────


def parse_gitignore(gitignore_path: Path) -> list:
    """Parse a .gitignore file and return a list of rule dictionaries."""
    rules = []
    if not gitignore_path.exists():
        print(f"⚠️  No .gitignore found at: {gitignore_path}")
        return rules

    with open(gitignore_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip() or line.strip().startswith("#"):
                continue

            is_negation = line.startswith("!")
            if is_negation:
                line = line[1:]

            line        = line.strip()
            is_rooted   = line.startswith("/")
            is_dir_only = line.endswith("/")
            pattern     = line.strip("/")

            rules.append({
                "raw"        : line,
                "pattern"    : pattern,
                "is_negation": is_negation,
                "is_rooted"  : is_rooted,
                "is_dir_only": is_dir_only,
            })

    return rules


def is_ignored(rel_path: Path, name: str, is_dir: bool, rules: list) -> bool:
    """
    Evaluate gitignore rules against a path.
    Rules are evaluated in order — the LAST matching rule wins.
    Negation rules (!) can un-ignore a previously ignored path.
    """
    rel    = str(rel_path).replace("\\", "/")
    rel_l  = rel.lower()
    name_l = name.lower()
    ignored      = False
    matched_rule = None

    for rule in rules:
        pattern     = rule["pattern"]
        pattern_l   = pattern.lower()
        is_negation = rule["is_negation"]
        is_rooted   = rule["is_rooted"]
        is_dir_only = rule["is_dir_only"]

        if is_dir_only and not is_dir:
            continue

        matched = False

        # ← FIXED #8 — simplified rooted block, removed redundant elif branches
        if is_rooted:
            if fnmatch.fnmatch(rel_l, pattern_l):
                matched = True
            elif fnmatch.fnmatch(rel_l, pattern_l + "/*"):
                matched = True
        else:
            if fnmatch.fnmatch(name_l, pattern_l):
                matched = True
            elif fnmatch.fnmatch(rel_l, pattern_l):
                matched = True
            elif fnmatch.fnmatch(rel_l, "*/" + pattern_l):
                matched = True

        if matched:
            ignored      = not is_negation
            matched_rule = rule["raw"]

    if DEBUG:
        status    = "❌ EXCLUDED" if ignored else "✅ INCLUDED"
        rule_info = f"  ← gitignore rule: '{matched_rule}'" if matched_rule else "  ← no rule matched"
        print(f"  {status}  {rel}{rule_info}")

    return ignored


def is_manually_excluded(rel_path: Path) -> bool:
    """
    Check if a path matches any MANUAL_EXCLUDE entry (case-insensitive).
    Both the exact path and any of its children are excluded.
    """
    rel_l = str(rel_path).replace("\\", "/").lower()
    for excl in MANUAL_EXCLUDE:
        excl_l = excl.lower()
        if rel_l == excl_l or rel_l.startswith(excl_l + "/"):
            return True
    return False


def should_exclude(path: Path, name: str, is_dir: bool, rules: list) -> bool:
    """
    Master exclusion check — three layers evaluated in order:
        1. ALWAYS_EXCLUDE  — exact name match
        2. MANUAL_EXCLUDE  — relative path prefix match
        3. Gitignore rules — pattern matching
    """
    if name in ALWAYS_EXCLUDE:
        if DEBUG:
            print(f"  ❌ ALWAYS_EXCLUDE  {name}")
        return True

    rel_path = path.relative_to(ROOT_DIR)

    if is_manually_excluded(rel_path):
        if DEBUG:
            print(f"  ❌ MANUAL_EXCLUDE  {rel_path}")
        return True

    return is_ignored(rel_path, name, is_dir, rules)


def process_file(file_path: Path) -> str:
    """Read and return file content, respecting size limits."""
    try:
        size_kb = file_path.stat().st_size / 1024
        if size_kb > MAX_FILE_SIZE_KB:
            if DEBUG:
                print(f"  ⏩ SKIPPED (Too Large: {size_kb:.1f} KB) {file_path.name}")
            return f"[File skipped: size {size_kb:.1f} KB exceeds limit of {MAX_FILE_SIZE_KB} KB]\n"
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception as e:
        return f"[Error reading file: {e}]\n"


def generate_tree(dir_path: Path, rules: list, prefix: str = "") -> list[str]:
    """
    Recursively generate a visual directory tree using Unicode connectors.
    Only includes files with allowed extensions and non-excluded items.

    Args:
        dir_path: Absolute path of the current directory.
        rules:    Parsed gitignore rules.
        prefix:   Current indentation prefix string.

    Returns:
        List of tree lines as strings.
    """
    tree  = []
    items = sorted(
        item for item in dir_path.iterdir()
        if not should_exclude(item, item.name, item.is_dir(), rules)
        and (item.is_dir() or item.suffix in ALLOWED_EXTENSIONS)
    )

    for i, item in enumerate(items):
        is_last   = (i == len(items) - 1)
        connector = "└── " if is_last else "├── "   # ← FIXED #12 — consistent double quotes
        tree.append(f"{prefix}{connector}{item.name}")
        if item.is_dir():
            next_prefix = prefix + ("    " if is_last else "│   ")
            tree.extend(generate_tree(item, rules, next_prefix))

    return tree


def generate_bundle() -> None:
    """Orchestrate directory scanning and compile all content into a single bundle file."""
    print(f"🚀 Scanning: {ROOT_DIR}")
    print(f"📦 Output:   {OUTPUT_FILE}")

    if not ROOT_DIR.exists():
        print(f"❌ Root directory not found: {ROOT_DIR}")
        return

    gitignore_rules = parse_gitignore(GITIGNORE_FILE)
    file_count      = 0
    skipped_count   = 0    # counts excluded dirs + excluded/extension-skipped files
    ext_skip_count  = 0    # ← FIXED #13 — track extension skips separately

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:

        # Header
        out.write("PROJECT CODE BUNDLE GENERATED FOR AI ANALYSIS\n")   # ← FIXED #9
        out.write(f"{AI_MESSAGE}\n\n")
        out.write(f"Root Directory: {ROOT_DIR}\n")

        # Directory tree
        out.write("<directory_structure>\n")
        out.write(f"{ROOT_DIR.name}/\n")
        out.write("\n".join(generate_tree(ROOT_DIR, gitignore_rules)))
        out.write("\n</directory_structure>\n\n")

        # File contents
        for current_root, dirs, files in os.walk(ROOT_DIR):
            current_path = Path(current_root)

            # Prune excluded directories so os.walk does not descend into them
            valid_dirs = []
            for d in sorted(dirs):
                dir_path = current_path / d
                if not should_exclude(dir_path, d, is_dir=True, rules=gitignore_rules):
                    valid_dirs.append(d)
                else:
                    skipped_count += 1
            dirs[:] = valid_dirs

            for f in sorted(files):
                file_path = current_path / f

                if should_exclude(file_path, f, is_dir=False, rules=gitignore_rules):
                    skipped_count += 1
                    continue

                if file_path.suffix.lower() not in ALLOWED_EXTENSIONS_SAVE_CONTENT:
                    ext_skip_count += 1    # ← FIXED #13
                    if DEBUG:
                        print(f"  ⏩ SKIPPED (Extension) {file_path.name}")
                    continue

                file_count    += 1
                rel_file_path  = file_path.relative_to(ROOT_DIR)
                out.write(f"<file path={rel_file_path}>\n")
                content = process_file(file_path)
                out.write(content)
                if not content.endswith("\n"):
                    out.write("\n")
                out.write("</file>\n\n")

    # ← FIXED #13 — accurate summary
    print(f"✅ Done — {file_count} files bundled, "
          f"{skipped_count} excluded, "
          f"{ext_skip_count} skipped (extension not in save list).")


if __name__ == "__main__":
    generate_bundle()
