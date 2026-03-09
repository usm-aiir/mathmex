# Re-export from backend (canonical source)
# Admin scripts add backend to path; use: from schemas.indexes import source_to_index
import sys
from pathlib import Path

_backend = Path(__file__).resolve().parents[2] / "backend"
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

from schemas.indexes import source_to_index  # noqa: F401, E402

__all__ = ["source_to_index"]
