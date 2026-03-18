from pathlib import Path

from data.common import fetch_rows, get_connection


def fetch_recursion_rows(db_path: Path) -> list[dict]:
    query = """
    SELECT id, oznaka, funkcija, argument, povrat, parent_id
    FROM rekurzija_poziv
    ORDER BY id;
    """
    conn = get_connection(db_path)
    try:
        return fetch_rows(conn, query)
    finally:
        conn.close()


def add_recursion_call(
    db_path: Path,
    oznaka: str,
    funkcija: str,
    argument: str,
    povrat: str | None,
    parent_id: int | None,
) -> int:
    conn = get_connection(db_path)
    try:
        if parent_id is not None:
            parent = conn.execute(
                "SELECT id FROM rekurzija_poziv WHERE id = ?;",
                (parent_id,),
            ).fetchone()
            if parent is None:
                raise ValueError("Parent rekurzivni poziv ne postoji.")

        conn.execute(
            "INSERT INTO rekurzija_poziv (oznaka, funkcija, argument, povrat, parent_id) VALUES (?, ?, ?, ?, ?);",
            (oznaka, funkcija, argument, povrat, parent_id),
        )
        new_id = conn.execute("SELECT last_insert_rowid();").fetchone()[0]
        conn.commit()
        return new_id
    finally:
        conn.close()


def update_recursion_call(
    db_path: Path,
    call_id: int,
    oznaka: str,
    funkcija: str,
    argument: str,
    povrat: str | None,
    parent_id: int | None,
) -> None:
    conn = get_connection(db_path)
    try:
        existing = conn.execute(
            "SELECT id FROM rekurzija_poziv WHERE id = ?;",
            (call_id,),
        ).fetchone()
        if existing is None:
            raise ValueError("Rekurzivni poziv ne postoji.")

        if parent_id is not None:
            if parent_id == call_id:
                raise ValueError("Parent ne moze biti isti kao cvor.")
            parent = conn.execute(
                "SELECT id FROM rekurzija_poziv WHERE id = ?;",
                (parent_id,),
            ).fetchone()
            if parent is None:
                raise ValueError("Parent rekurzivni poziv ne postoji.")

        conn.execute(
            "UPDATE rekurzija_poziv SET oznaka = ?, funkcija = ?, argument = ?, povrat = ?, parent_id = ? WHERE id = ?;",
            (oznaka, funkcija, argument, povrat, parent_id, call_id),
        )
        conn.commit()
    finally:
        conn.close()


def delete_recursion_call(db_path: Path, call_id: int) -> None:
    conn = get_connection(db_path)
    try:
        deleted = conn.execute(
            "DELETE FROM rekurzija_poziv WHERE id = ?;",
            (call_id,),
        ).rowcount
        if deleted == 0:
            raise ValueError("Rekurzivni poziv ne postoji.")
        conn.commit()
    finally:
        conn.close()