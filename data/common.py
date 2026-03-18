import sqlite3
from pathlib import Path

HASH_TABLE_NAME = "HashTablicaA"
GENERAL_TREE_NAME = "OrgStablo"
BST_TREE_NAME = "BST_Primjer"


def get_connection(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def fetch_rows(conn: sqlite3.Connection, query: str, params: tuple = ()) -> list[dict]:
    return [dict(row) for row in conn.execute(query, params)]