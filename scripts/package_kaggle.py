from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

OUTPUT_DIR = Path("dist")
OUTPUT_DIR.mkdir(exist_ok=True)

ZIP_PATH = OUTPUT_DIR / "rag-foundry.zip"

EXCLUDE_FILES = {
    ".env",
}

# Exclude ONLY these directories when they are at the project root
TOP_LEVEL_EXCLUDE_DIRS = {
    ".git",
    "venv",
    ".venv",
    ".pytest_cache",
    ".mypy_cache",
    ".ipynb_checkpoints",
    "cache",      # runtime cache only
    "reports",    # generated reports only
    "dist",
}

EXCLUDE_SUFFIXES = {
    ".pyc",
    ".pyo",
}

with ZipFile(ZIP_PATH, "w", ZIP_DEFLATED) as zf:
    for path in Path(".").rglob("*"):
        if path.is_dir():
            continue

        relative = path.relative_to(Path("."))

        # Skip excluded files
        if path.name in EXCLUDE_FILES:
            continue

        # Skip __pycache__ anywhere in the project
        if "__pycache__" in relative.parts:
            continue

        # Skip selected top-level directories only
        if relative.parts and relative.parts[0] in TOP_LEVEL_EXCLUDE_DIRS:
            continue

        # Skip compiled Python files
        if path.suffix in EXCLUDE_SUFFIXES:
            continue

        zf.write(path, relative)

print(f"Created {ZIP_PATH}")