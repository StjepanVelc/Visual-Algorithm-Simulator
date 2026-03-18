from pathlib import Path

from data.common import HASH_TABLE_NAME, fetch_rows, get_connection


def fetch_hash_rows(db_path: Path) -> list[dict]:
    query = """
    SELECT b.indeks AS bucket, c.id AS cvor_id, c.kljuc, c.vrijednost, c.sljedeci_cvor_id
    FROM hash_bucket b
    LEFT JOIN hash_cvor c ON c.bucket_id = b.id
    WHERE b.hash_tablica_id = (SELECT id FROM hash_tablica WHERE naziv = ?)
    ORDER BY b.indeks, c.id;
    """
    conn = get_connection(db_path)
    try:
        return fetch_rows(conn, query, (HASH_TABLE_NAME,))
    finally:
        conn.close()


def add_hash_node(db_path: Path, bucket_index: int, key: str, value: str) -> int:
    conn = get_connection(db_path)
    try:
        table_row = conn.execute(
            "SELECT id, velicina FROM hash_tablica WHERE naziv = ?;",
            (HASH_TABLE_NAME,),
        ).fetchone()
        if table_row is None:
            raise ValueError("Hash tablica nije pronadena.")

        table_id, table_size = table_row
        if bucket_index < 0 or bucket_index >= table_size:
            raise ValueError(f"Bucket indeks mora biti izmedu 0 i {table_size - 1}.")

        bucket_row = conn.execute(
            "SELECT id FROM hash_bucket WHERE hash_tablica_id = ? AND indeks = ?;",
            (table_id, bucket_index),
        ).fetchone()
        if bucket_row is None:
            raise ValueError("Bucket nije pronaden.")

        bucket_id = bucket_row[0]
        last_id_row = conn.execute(
            "SELECT id FROM hash_cvor WHERE bucket_id = ? ORDER BY id DESC LIMIT 1;",
            (bucket_id,),
        ).fetchone()
        last_id = last_id_row[0] if last_id_row else None

        conn.execute(
            "INSERT INTO hash_cvor (bucket_id, kljuc, vrijednost, sljedeci_cvor_id) VALUES (?, ?, ?, ?);",
            (bucket_id, key, value, None),
        )
        new_id = conn.execute("SELECT last_insert_rowid();").fetchone()[0]

        if last_id is not None:
            conn.execute(
                "UPDATE hash_cvor SET sljedeci_cvor_id = ? WHERE id = ?;",
                (new_id, last_id),
            )

        conn.commit()
        return new_id
    finally:
        conn.close()


def update_hash_node(db_path: Path, node_id: int, key: str, value: str) -> None:
    conn = get_connection(db_path)
    try:
        existing = conn.execute(
            "SELECT id FROM hash_cvor WHERE id = ?;",
            (node_id,),
        ).fetchone()
        if existing is None:
            raise ValueError("Hash cvor ne postoji.")

        conn.execute(
            "UPDATE hash_cvor SET kljuc = ?, vrijednost = ? WHERE id = ?;",
            (key, value, node_id),
        )
        conn.commit()
    finally:
        conn.close()


def delete_hash_node(db_path: Path, node_id: int) -> None:
    conn = get_connection(db_path)
    try:
        node = conn.execute(
            "SELECT id, sljedeci_cvor_id FROM hash_cvor WHERE id = ?;",
            (node_id,),
        ).fetchone()
        if node is None:
            raise ValueError("Hash cvor ne postoji.")

        conn.execute(
            "UPDATE hash_cvor SET sljedeci_cvor_id = ? WHERE sljedeci_cvor_id = ?;",
            (node[1], node_id),
        )
        conn.execute("DELETE FROM hash_cvor WHERE id = ?;", (node_id,))
        conn.commit()
    finally:
        conn.close()