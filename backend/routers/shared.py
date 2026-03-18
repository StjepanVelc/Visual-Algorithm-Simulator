from dataclasses import asdict
from pathlib import Path

from services.adt_service import build_database, collect_state

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "adt.db"

if not DB_PATH.exists():
    build_database(DB_PATH)


def full_state() -> dict:
    return asdict(collect_state(DB_PATH, "api"))
