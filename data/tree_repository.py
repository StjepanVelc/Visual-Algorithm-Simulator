from pathlib import Path

from data.common import BST_TREE_NAME, GENERAL_TREE_NAME, fetch_rows, get_connection


def _value_to_cmp_key(value: str) -> tuple[int, float | str]:
    try:
        return (0, float(value))
    except (TypeError, ValueError):
        return (1, str(value))


def fetch_general_tree_rows(db_path: Path) -> list[dict]:
    query = """
    SELECT c.id, c.vrijednost, c.parent_id, c.redoslijed
    FROM stablo_cvor c
    WHERE c.stablo_id = (SELECT id FROM stablo WHERE naziv = ?)
    ORDER BY COALESCE(c.parent_id, 0), c.redoslijed, c.id;
    """
    conn = get_connection(db_path)
    try:
        return fetch_rows(conn, query, (GENERAL_TREE_NAME,))
    finally:
        conn.close()


def fetch_bst_rows(db_path: Path) -> list[dict]:
    query = """
    SELECT c.id, c.vrijednost, c.parent_id, c.lijevi_id, c.desni_id
    FROM stablo_cvor c
    WHERE c.stablo_id = (SELECT id FROM stablo WHERE naziv = ?)
    ORDER BY c.id;
    """
    conn = get_connection(db_path)
    try:
        return fetch_rows(conn, query, (BST_TREE_NAME,))
    finally:
        conn.close()


def add_general_tree_node(
    db_path: Path,
    vrijednost: str,
    parent_id: int | None,
    redoslijed: int | None,
) -> int:
    conn = get_connection(db_path)
    try:
        tree_row = conn.execute(
            "SELECT id FROM stablo WHERE naziv = ?;",
            (GENERAL_TREE_NAME,),
        ).fetchone()
        if tree_row is None:
            raise ValueError("Opce stablo nije pronadeno.")

        tree_id = tree_row[0]
        if parent_id is not None:
            parent = conn.execute(
                "SELECT id FROM stablo_cvor WHERE id = ? AND stablo_id = ?;",
                (parent_id, tree_id),
            ).fetchone()
            if parent is None:
                raise ValueError("Parent cvor ne postoji u opcem stablu.")

        conn.execute(
            "INSERT INTO stablo_cvor (stablo_id, vrijednost, parent_id, lijevi_id, desni_id, redoslijed) VALUES (?, ?, ?, ?, ?, ?);",
            (tree_id, vrijednost, parent_id, None, None, redoslijed),
        )
        new_id = conn.execute("SELECT last_insert_rowid();").fetchone()[0]
        conn.commit()
        return new_id
    finally:
        conn.close()


def update_general_tree_node(
    db_path: Path,
    node_id: int,
    vrijednost: str,
    parent_id: int | None,
    redoslijed: int | None,
) -> None:
    conn = get_connection(db_path)
    try:
        tree_row = conn.execute(
            "SELECT id FROM stablo WHERE naziv = ?;",
            (GENERAL_TREE_NAME,),
        ).fetchone()
        if tree_row is None:
            raise ValueError("Opce stablo nije pronadeno.")
        tree_id = tree_row[0]

        existing = conn.execute(
            "SELECT id FROM stablo_cvor WHERE id = ? AND stablo_id = ?;",
            (node_id, tree_id),
        ).fetchone()
        if existing is None:
            raise ValueError("Cvor ne postoji u opcem stablu.")

        if parent_id is not None:
            if parent_id == node_id:
                raise ValueError("Parent ne moze biti isti kao cvor.")
            parent = conn.execute(
                "SELECT id FROM stablo_cvor WHERE id = ? AND stablo_id = ?;",
                (parent_id, tree_id),
            ).fetchone()
            if parent is None:
                raise ValueError("Parent cvor ne postoji u opcem stablu.")

        conn.execute(
            "UPDATE stablo_cvor SET vrijednost = ?, parent_id = ?, redoslijed = ? WHERE id = ?;",
            (vrijednost, parent_id, redoslijed, node_id),
        )
        conn.commit()
    finally:
        conn.close()


def delete_general_tree_node(db_path: Path, node_id: int) -> None:
    conn = get_connection(db_path)
    try:
        tree_row = conn.execute(
            "SELECT id FROM stablo WHERE naziv = ?;",
            (GENERAL_TREE_NAME,),
        ).fetchone()
        if tree_row is None:
            raise ValueError("Opce stablo nije pronadeno.")

        deleted = conn.execute(
            "DELETE FROM stablo_cvor WHERE id = ? AND stablo_id = ?;",
            (node_id, tree_row[0]),
        ).rowcount
        if deleted == 0:
            raise ValueError("Cvor ne postoji u opcem stablu.")
        conn.commit()
    finally:
        conn.close()


def add_bst_node(db_path: Path, vrijednost: str, parent_id: int, side: str) -> int:
    if side not in {"L", "R"}:
        raise ValueError("Side mora biti 'L' ili 'R'.")

    conn = get_connection(db_path)
    try:
        bst_row = conn.execute(
            "SELECT id FROM stablo WHERE naziv = ?;",
            (BST_TREE_NAME,),
        ).fetchone()
        if bst_row is None:
            raise ValueError("BST nije pronaden.")

        bst_id = bst_row[0]
        parent = conn.execute(
            "SELECT id, lijevi_id, desni_id FROM stablo_cvor WHERE id = ? AND stablo_id = ?;",
            (parent_id, bst_id),
        ).fetchone()
        if parent is None:
            raise ValueError("Ne postoji parent cvor u BST-u.")

        left_id, right_id = parent[1], parent[2]
        if side == "L" and left_id is not None:
            raise ValueError("Parent vec ima lijevo dijete.")
        if side == "R" and right_id is not None:
            raise ValueError("Parent vec ima desno dijete.")

        conn.execute(
            "INSERT INTO stablo_cvor (stablo_id, vrijednost, parent_id, lijevi_id, desni_id, redoslijed) VALUES (?, ?, ?, ?, ?, ?);",
            (bst_id, vrijednost, parent_id, None, None, None),
        )
        new_id = conn.execute("SELECT last_insert_rowid();").fetchone()[0]

        if side == "L":
            conn.execute("UPDATE stablo_cvor SET lijevi_id = ? WHERE id = ?;", (new_id, parent_id))
        else:
            conn.execute("UPDATE stablo_cvor SET desni_id = ? WHERE id = ?;", (new_id, parent_id))

        conn.commit()
        return new_id
    finally:
        conn.close()


def insert_bst_node_auto(db_path: Path, vrijednost: str) -> dict:
    conn = get_connection(db_path)
    try:
        bst_row = conn.execute(
            "SELECT id FROM stablo WHERE naziv = ?;",
            (BST_TREE_NAME,),
        ).fetchone()
        if bst_row is None:
            raise ValueError("BST nije pronaden.")
        bst_id = int(bst_row[0])

        rows = conn.execute(
            "SELECT id, vrijednost, parent_id, lijevi_id, desni_id FROM stablo_cvor WHERE stablo_id = ? ORDER BY id;",
            (bst_id,),
        ).fetchall()

        if not rows:
            conn.execute(
                "INSERT INTO stablo_cvor (stablo_id, vrijednost, parent_id, lijevi_id, desni_id, redoslijed) VALUES (?, ?, ?, ?, ?, ?);",
                (bst_id, vrijednost, None, None, None, None),
            )
            new_id = int(conn.execute("SELECT last_insert_rowid();").fetchone()[0])
            conn.commit()
            return {
                "new_id": new_id,
                "parent_id": None,
                "side": None,
                "path": [new_id],
            }

        nodes = {
            int(row[0]): {
                "id": int(row[0]),
                "vrijednost": str(row[1]),
                "parent_id": row[2],
                "lijevi_id": row[3],
                "desni_id": row[4],
            }
            for row in rows
        }
        root_id = next((node_id for node_id, node in nodes.items() if node["parent_id"] is None), None)
        if root_id is None:
            raise ValueError("BST nema korijenski cvor.")

        cmp_value = _value_to_cmp_key(vrijednost)
        path: list[int] = []
        current_id = int(root_id)

        while True:
            current = nodes[current_id]
            path.append(current_id)
            current_cmp = _value_to_cmp_key(current["vrijednost"])
            go_left = cmp_value < current_cmp
            side = "L" if go_left else "R"
            child_id = current["lijevi_id"] if go_left else current["desni_id"]

            if child_id is None:
                conn.execute(
                    "INSERT INTO stablo_cvor (stablo_id, vrijednost, parent_id, lijevi_id, desni_id, redoslijed) VALUES (?, ?, ?, ?, ?, ?);",
                    (bst_id, vrijednost, current_id, None, None, None),
                )
                new_id = int(conn.execute("SELECT last_insert_rowid();").fetchone()[0])
                if side == "L":
                    conn.execute("UPDATE stablo_cvor SET lijevi_id = ? WHERE id = ?;", (new_id, current_id))
                else:
                    conn.execute("UPDATE stablo_cvor SET desni_id = ? WHERE id = ?;", (new_id, current_id))
                conn.commit()
                return {
                    "new_id": new_id,
                    "parent_id": current_id,
                    "side": side,
                    "path": path + [new_id],
                }

            current_id = int(child_id)
    finally:
        conn.close()


def update_bst_node_value(db_path: Path, node_id: int, vrijednost: str) -> None:
    conn = get_connection(db_path)
    try:
        bst_row = conn.execute(
            "SELECT id FROM stablo WHERE naziv = ?;",
            (BST_TREE_NAME,),
        ).fetchone()
        if bst_row is None:
            raise ValueError("BST nije pronaden.")

        updated = conn.execute(
            "UPDATE stablo_cvor SET vrijednost = ? WHERE id = ? AND stablo_id = ?;",
            (vrijednost, node_id, bst_row[0]),
        ).rowcount
        if updated == 0:
            raise ValueError("BST cvor ne postoji.")
        conn.commit()
    finally:
        conn.close()


def delete_bst_node(db_path: Path, node_id: int) -> None:
    conn = get_connection(db_path)
    try:
        bst_row = conn.execute(
            "SELECT id FROM stablo WHERE naziv = ?;",
            (BST_TREE_NAME,),
        ).fetchone()
        if bst_row is None:
            raise ValueError("BST nije pronaden.")
        bst_id = bst_row[0]

        node = conn.execute(
            "SELECT id, parent_id, lijevi_id, desni_id FROM stablo_cvor WHERE id = ? AND stablo_id = ?;",
            (node_id, bst_id),
        ).fetchone()
        if node is None:
            raise ValueError("BST cvor ne postoji.")

        if node[2] is not None or node[3] is not None:
            raise ValueError("Moguce je obrisati samo BST list (cvor bez djece).")

        parent_id = node[1]
        if parent_id is not None:
            conn.execute(
                "UPDATE stablo_cvor SET lijevi_id = NULL WHERE id = ? AND lijevi_id = ?;",
                (parent_id, node_id),
            )
            conn.execute(
                "UPDATE stablo_cvor SET desni_id = NULL WHERE id = ? AND desni_id = ?;",
                (parent_id, node_id),
            )

        conn.execute("DELETE FROM stablo_cvor WHERE id = ? AND stablo_id = ?;", (node_id, bst_id))
        conn.commit()
    finally:
        conn.close()