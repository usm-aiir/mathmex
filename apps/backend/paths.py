"""
Central path and config for MathMex.
Import from here: from paths import ROOT, CONFIG_PATH, get_config
Run all commands from project root.
"""
import os
import sys
from pathlib import Path

# Project root (mathmex/)
_BACKEND_DIR = Path(__file__).resolve().parent
ROOT = _BACKEND_DIR.parent.parent

CONFIG_PATH = ROOT / "config.ini"
DATA_PATH = ROOT / "data"
FORMULA_SEARCH_PATH = ROOT / "formula-search"

# TangentCFT/FAISS paths: formula-search if present, else data/jsonl/TangentCFT
if FORMULA_SEARCH_PATH.exists():
    ENCODED_FILE_PATH = str(FORMULA_SEARCH_PATH / "encoded.jsonl")
    INDEX_PATH = str(FORMULA_SEARCH_PATH / "encoded_index.json")
    FAISS_INDEX_PATH = str(FORMULA_SEARCH_PATH / "slt_index.faiss")


def get_config_path() -> str:
    """Config path: BACKEND_CONFIG env or ROOT/config.ini."""
    path = os.getenv("BACKEND_CONFIG") or str(CONFIG_PATH)
    return os.path.expanduser(path)


def setup_formula_search_imports() -> None:
    """Add formula-search to sys.path for TangentCFT/LateFusion imports."""
    if not FORMULA_SEARCH_PATH.exists():
        return
    for p in (str(FORMULA_SEARCH_PATH), str(FORMULA_SEARCH_PATH / "LateFusionModel")):
        if p not in sys.path:
            sys.path.insert(0, p)
