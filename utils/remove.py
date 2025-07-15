# utils/remove.py
import shutil
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INSTANCE_DIR = PROJECT_ROOT / "instance"
SQLITE_FILE  = INSTANCE_DIR / "parking.sqlite3"

# ───────────────────────── helpers ──────────────────────────
def _rm_tree(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
        print(f"💥  removed dir  : {path.relative_to(PROJECT_ROOT)}")

def _rm_file(path: Path) -> None:
    if path.is_file():
        path.unlink()
        print(f"💥  removed file : {path.relative_to(PROJECT_ROOT)}")

def _purge_pycache(root: Path) -> None:
    for pyc_dir in root.rglob("__pycache__"):
        _rm_tree(pyc_dir)

def _newer_than_db(files: Iterable[Path], db_path: Path) -> bool:
    """Return True if any given file is newer than the database file."""
    if not db_path.exists():
        return True                          # DB missing => treat as outdated
    db_mtime = db_path.stat().st_mtime
    return any(p.stat().st_mtime > db_mtime for p in files if p.exists())

# ──────────────────────── public API ─────────────────────────
def wipe_all(
    *,
    nuke_instance: bool = True,
    auto: bool = False,
    model_glob: str = "application/**/*.py"
) -> None:
    """
    Dev‑only wipe.
    nuke_instance=True  – delete instance/ folder (else only .sqlite file)
    auto=True           – wipe only if model files are newer than DB
    model_glob          – glob pattern to match model / migration files
    """
    # auto‑mode check
    if auto:
        model_files = list(PROJECT_ROOT.glob(model_glob))
        if not _newer_than_db(model_files, SQLITE_FILE):
            print("⏩  DB up‑to‑date; skip wipe")
            return
        print("🔄  Models newer than DB – wiping...")

    # nuke instance or just the DB file
    if nuke_instance:
        _rm_tree(INSTANCE_DIR)
    else:
        _rm_file(SQLITE_FILE)

    # always clear __pycache__
    _purge_pycache(PROJECT_ROOT)
    print("✅  wipe complete")

# Alias for backward compatibility
remove = wipe_all
