import sqlite3
from pathlib import Path


def export_sql(db_path: Path, sql_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    try:
        with sql_path.open("w", encoding="utf-8") as handle:
            for line in conn.iterdump():
                handle.write(f"{line}\n")
    finally:
        conn.close()


def import_sql(db_path: Path, sql_path: Path, replace: bool = True) -> None:
    if replace and db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    try:
        script = sql_path.read_text(encoding="utf-8")
        conn.executescript(script)
        conn.commit()
    finally:
        conn.close()