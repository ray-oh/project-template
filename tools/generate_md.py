# =============================================================================
# save_md.py
#
# Purpose : Writes a raw Markdown string to a local .md file.
#           Intended as a paste-and-run script — replace the content
#           between the triple-quoted string with Markdown from Claude,
#           then execute to produce a clean .md file on disk.
#
# Usage   : python save_md.py
#
# Output  : savefile.md  (same directory as this script)
#
# Notes   : Use ||| as a placeholder for ``` inside the raw string to
#           avoid triple-quote conflicts. They are replaced at write time.
# =============================================================================

from pathlib import Path

savefilename = "savefile.md"

content = r"""
# Paste the markdown text from claude here
"""

content = content.replace("|||", "```")
Path(savefilename).write_text(content, encoding="utf-8")
print(f"Written: {Path(savefilename).resolve()}")
