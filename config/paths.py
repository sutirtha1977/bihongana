from pathlib import Path
import sys
import os

# =========================================================
# APP CONFIG
# =========================================================
APP_NAME = "BihonganaApp"

# =========================================================
# BASE PATHS
# =========================================================
def get_base_dir():
    """
    Returns base directory depending on execution mode.
    - Dev mode: project root
    - PyInstaller exe: folder containing the exe
    """
    if getattr(sys, "frozen", False):
        # Running as exe → use the folder where the exe lives
        base_dir = Path(sys.executable).parent
    else:
        # Dev mode → project root
        base_dir = Path(__file__).parent.parent

    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir

BASE_DIR = get_base_dir()

# ---------------- Database ----------------
DB_FILE = BASE_DIR / "bihongana.db"

# ---------------- Logging ----------------
LOG_FILE = BASE_DIR / "audit_trail.log"

# ---------------- Data Directory ----------------
DATA_DIR: Path = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ---------------- Excel Files ----------------
BIHONGANA_XLSX: Path = DATA_DIR / "bihongana.xlsx"

# =========================================================
# Helper Functions
# =========================================================
def ensure_folder(path: Path):
    """Ensure the folder exists."""
    path.mkdir(parents=True, exist_ok=True)