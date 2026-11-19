"""Rename the project from CivicWeb Access to CivicWeb Observatory.

The project is no longer India-specific: it measures government websites across
93 countries. The name should say that.

This script does the rename in one pass and is idempotent, so running it twice
is harmless. It handles three things:

1. **File and directory names** — the package directory, the paper, the deck.
2. **Content** — every reference in code, docs, config and data.
3. **Ordering** — longest patterns first, so ``civicweb_observatory_clean.csv``
   becomes ``civicweb_observatory_clean.csv`` rather than a mangled hybrid.

It deliberately does not touch ``.git``, ``node_modules``, caches, or the
scratch directory.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".pytest_cache", "scratch", ".venv", "venv"}
TEXT_SUFFIXES = {
    ".py", ".md", ".html", ".js", ".css", ".toml", ".json", ".yml", ".yaml",
    ".tex", ".cff", ".txt", ".cfg", ".ini", ".sh", ".ps1", ".service", ".example",
}

#: Ordered longest-first so a specific pattern wins over a general one.
REPLACEMENTS: list[tuple[str, str]] = [
    # Data artefacts
    ("civicweb_observatory_clean.parquet", "civicweb_observatory_clean.parquet"),
    ("civicweb_observatory_clean.csv", "civicweb_observatory_clean.csv"),
    ("civicweb_observatory_clean.json", "civicweb_observatory_clean.json"),
    ("civicweb_observatory_clean", "civicweb_observatory_clean"),
    ("civicweb_observatory_vX.Y.Z", "civicweb_observatory_vX.Y.Z"),
    ("civicweb_observatory_v0.1.0", "civicweb_observatory_v0.1.0"),
    ("civicweb_observatory_0.1.0", "civicweb_observatory_0.1.0"),
    ("civicweb_observatory_2026", "civicweb_observatory_2026"),
    ("civicweb_observatory_", "civicweb_observatory_"),
    # Package and module
    ("civicweb-observatory", "civicweb-observatory"),
    ("civicweb_observatory", "civicweb_observatory"),
    # Infrastructure identifiers
    ("civicweb-ephemeral", "civicweb-ephemeral"),
    ("civicweb-node", "civicweb-node"),
    ("civicweb-dashboard", "civicweb-dashboard"),
    ("civicweb-tunnel", "civicweb-tunnel"),
    ("civicweb-evidence", "civicweb-evidence"),
    ("civicweb_secure_password_change_me", "civicweb_secure_password_change_me"),
    ("civicweb_password", "civicweb_password"),
    ("civicweb_postgres", "civicweb_postgres"),
    ("civicweb_redis", "civicweb_redis"),
    ("civicweb_minio", "civicweb_minio"),
    ("civicweb_ollama", "civicweb_ollama"),
    ("civicweb_worker", "civicweb_worker"),
    ("civicweb_api", "civicweb_api"),
    # Documents
    ("CivicWeb_Observatory_Research_Paper", "CivicWeb_Observatory_Research_Paper"),
    ("CivicWeb_Observatory_Final_Deck", "CivicWeb_Observatory_Final_Deck"),
    ("CivicWeb_Observatory_Project_Documentation", "CivicWeb_Observatory_Project_Documentation"),
    ("CivicWeb_Observatory_Checkpoint_2_Presentation", "CivicWeb_Observatory_Checkpoint_2_Presentation"),
    ("CivicWeb_Observatory", "CivicWeb_Observatory"),
    # Display names and identifiers
    ("CivicWebObservatory", "CivicWebObservatory"),
    ("CivicWebObservatory", "CivicWebObservatory"),
    ("CivicWeb", "CivicWeb"),
    ("civicweb", "civicweb"),
    # Contact address
    ("research-bot@civicweb.in", "research-bot@civicweb.org"),
    ("civicweb.in", "civicweb.org"),
]


def rename_paths() -> int:
    """Rename files and directories, deepest first."""
    changed = 0
    for root, dirs, files in os.walk(REPO, topdown=False):
        root_path = Path(root)
        if any(part in SKIP_DIRS for part in root_path.parts):
            continue
        for name in files + dirs:
            old = root_path / name
            new_name = name
            for pattern, replacement in REPLACEMENTS:
                if pattern in new_name:
                    new_name = new_name.replace(pattern, replacement)
            if new_name != name:
                new = root_path / new_name
                if new.exists():
                    print(f"  skip (exists): {new.relative_to(REPO)}")
                    continue
                old.rename(new)
                print(f"  renamed: {old.relative_to(REPO)} -> {new_name}")
                changed += 1
    return changed


def rewrite_content() -> int:
    """Replace every reference inside text files."""
    changed = 0
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            path = Path(root) / name
            if path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            original = text
            for pattern, replacement in REPLACEMENTS:
                text = text.replace(pattern, replacement)
            if text != original:
                path.write_text(text, encoding="utf-8")
                changed += 1
    return changed


def main() -> int:
    print("Renaming paths...")
    paths = rename_paths()
    print(f"\nRewriting content...")
    files = rewrite_content()
    print(f"\nrenamed {paths} paths, rewrote {files} files")

    # Verify nothing was missed.
    leftovers = []
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            path = Path(root) / name
            if path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            if re.search(r"[Bb]harat[Gg]ov", text):
                leftovers.append(str(path.relative_to(REPO)))
    if leftovers:
        print(f"\nWARNING: {len(leftovers)} files still mention the old name:")
        for f in leftovers[:20]:
            print("  ", f)
        return 1
    print("\nno references to the old name remain")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
