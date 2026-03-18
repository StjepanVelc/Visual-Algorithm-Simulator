from pathlib import Path

from data.common import fetch_rows, get_connection


def fetch_stack_queue_rows(db_path: Path) -> list[dict]:
    query = """
    SELECT sr.naziv, sr.tip, e.vrijednost, e.pozicija
    FROM stog_red_element e
    JOIN stog_red sr ON sr.id = e.stog_red_id
    ORDER BY sr.naziv, e.pozicija;
    """
    conn = get_connection(db_path)
    try:
        return fetch_rows(conn, query)
    finally:
        conn.close()