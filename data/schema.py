import sqlite3
from pathlib import Path


def build_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")

    schema = """
    CREATE TABLE struktura (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        naziv TEXT NOT NULL,
        opis TEXT NOT NULL
    );

    CREATE TABLE hash_tablica (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        naziv TEXT NOT NULL,
        velicina INTEGER NOT NULL,
        hash_funkcija TEXT NOT NULL
    );

    CREATE TABLE hash_bucket (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hash_tablica_id INTEGER NOT NULL,
        indeks INTEGER NOT NULL,
        FOREIGN KEY (hash_tablica_id) REFERENCES hash_tablica(id) ON DELETE CASCADE
    );

    CREATE TABLE hash_cvor (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bucket_id INTEGER NOT NULL,
        kljuc TEXT NOT NULL,
        vrijednost TEXT NOT NULL,
        sljedeci_cvor_id INTEGER,
        FOREIGN KEY (bucket_id) REFERENCES hash_bucket(id) ON DELETE CASCADE,
        FOREIGN KEY (sljedeci_cvor_id) REFERENCES hash_cvor(id) ON DELETE SET NULL
    );

    CREATE TABLE rekurzija_poziv (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        oznaka TEXT NOT NULL,
        funkcija TEXT NOT NULL,
        argument TEXT NOT NULL,
        povrat TEXT,
        parent_id INTEGER,
        FOREIGN KEY (parent_id) REFERENCES rekurzija_poziv(id) ON DELETE CASCADE
    );

    CREATE TABLE stablo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        naziv TEXT NOT NULL,
        tip TEXT NOT NULL
    );

    CREATE TABLE stablo_cvor (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stablo_id INTEGER NOT NULL,
        vrijednost TEXT NOT NULL,
        parent_id INTEGER,
        lijevi_id INTEGER,
        desni_id INTEGER,
        redoslijed INTEGER,
        FOREIGN KEY (stablo_id) REFERENCES stablo(id) ON DELETE CASCADE,
        FOREIGN KEY (parent_id) REFERENCES stablo_cvor(id) ON DELETE CASCADE,
        FOREIGN KEY (lijevi_id) REFERENCES stablo_cvor(id) ON DELETE SET NULL,
        FOREIGN KEY (desni_id) REFERENCES stablo_cvor(id) ON DELETE SET NULL
    );

    CREATE TABLE stog_red (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        naziv TEXT NOT NULL,
        tip TEXT NOT NULL
    );

    CREATE TABLE stog_red_element (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stog_red_id INTEGER NOT NULL,
        vrijednost TEXT NOT NULL,
        pozicija INTEGER NOT NULL,
        FOREIGN KEY (stog_red_id) REFERENCES stog_red(id) ON DELETE CASCADE
    );
    """

    conn.executescript(schema)

    strukture = [
        ("Hash tablica", "Lanci u bucketima (chaining)"),
        ("Rekurzija", "Stablo poziva funkcije"),
        ("Stabla", "Opce stablo s vise djece"),
        ("BST", "Binarno stablo pretrage"),
        ("Stog/Red", "Linearne strukture s redoslijedom"),
    ]
    conn.executemany("INSERT INTO struktura (naziv, opis) VALUES (?, ?);", strukture)

    conn.execute(
        "INSERT INTO hash_tablica (naziv, velicina, hash_funkcija) VALUES (?, ?, ?);",
        ("HashTablicaA", 8, "sum(ord) % 8"),
    )
    hash_id = conn.execute("SELECT id FROM hash_tablica WHERE naziv = ?;", ("HashTablicaA",)).fetchone()[0]

    buckets = [(hash_id, i) for i in range(8)]
    conn.executemany("INSERT INTO hash_bucket (hash_tablica_id, indeks) VALUES (?, ?);", buckets)

    bucket_ids = {
        row[1]: row[0]
        for row in conn.execute("SELECT id, indeks FROM hash_bucket WHERE hash_tablica_id = ?;", (hash_id,))
    }

    nodes = [
        (bucket_ids[1], "ana", "10", None),
        (bucket_ids[1], "iva", "22", None),
        (bucket_ids[2], "marko", "35", None),
        (bucket_ids[2], "luka", "44", None),
        (bucket_ids[3], "pero", "19", None),
        (bucket_ids[3], "mate", "27", None),
        (bucket_ids[4], "tea", "51", None),
        (bucket_ids[4], "toni", "12", None),
        (bucket_ids[5], "iva2", "18", None),
        (bucket_ids[6], "sara", "33", None),
        (bucket_ids[6], "ivan", "29", None),
        (bucket_ids[7], "nina", "41", None),
    ]
    conn.executemany(
        "INSERT INTO hash_cvor (bucket_id, kljuc, vrijednost, sljedeci_cvor_id) VALUES (?, ?, ?, ?);",
        nodes,
    )

    bucket_chain = conn.execute(
        "SELECT id FROM hash_cvor WHERE bucket_id = ? ORDER BY id;", (bucket_ids[1],)
    ).fetchall()
    if len(bucket_chain) == 2:
        conn.execute(
            "UPDATE hash_cvor SET sljedeci_cvor_id = ? WHERE id = ?;",
            (bucket_chain[1][0], bucket_chain[0][0]),
        )

    fib_calls = [
        ("f(5)", "fib", "5", None, None),
        ("f(4)", "fib", "4", None, 1),
        ("f(3)", "fib", "3", None, 1),
        ("f(3a)", "fib", "3", None, 2),
        ("f(2)", "fib", "2", "1", 2),
        ("f(2a)", "fib", "2", "1", 3),
        ("f(1)", "fib", "1", "1", 3),
        ("f(2b)", "fib", "2", "1", 4),
        ("f(1a)", "fib", "1", "1", 4),
        ("f(1b)", "fib", "1", "1", 6),
        ("f(0)", "fib", "0", "0", 6),
        ("f(1c)", "fib", "1", "1", 2),
    ]
    conn.executemany(
        "INSERT INTO rekurzija_poziv (oznaka, funkcija, argument, povrat, parent_id) VALUES (?, ?, ?, ?, ?);",
        fib_calls,
    )

    conn.execute("INSERT INTO stablo (naziv, tip) VALUES (?, ?);", ("OrgStablo", "opce"))
    tree_id = conn.execute("SELECT id FROM stablo WHERE naziv = ?;", ("OrgStablo",)).fetchone()[0]

    opce_nodes = [
        (tree_id, "CEO", None, None, None, 0),
        (tree_id, "CTO", 1, None, None, 0),
        (tree_id, "CFO", 1, None, None, 1),
        (tree_id, "Dev1", 2, None, None, 0),
        (tree_id, "Dev2", 2, None, None, 1),
        (tree_id, "Ops", 2, None, None, 2),
        (tree_id, "Acc1", 3, None, None, 0),
        (tree_id, "Acc2", 3, None, None, 1),
        (tree_id, "QA", 2, None, None, 3),
        (tree_id, "HR", 1, None, None, 2),
    ]
    conn.executemany(
        "INSERT INTO stablo_cvor (stablo_id, vrijednost, parent_id, lijevi_id, desni_id, redoslijed) VALUES (?, ?, ?, ?, ?, ?);",
        opce_nodes,
    )

    conn.execute("INSERT INTO stablo (naziv, tip) VALUES (?, ?);", ("BST_Primjer", "bst"))
    bst_id = conn.execute("SELECT id FROM stablo WHERE naziv = ?;", ("BST_Primjer",)).fetchone()[0]

    bst_nodes = [
        (bst_id, "8", None, None, None, None),
        (bst_id, "3", 11, None, None, None),
        (bst_id, "10", 11, None, None, None),
        (bst_id, "1", 12, None, None, None),
        (bst_id, "6", 12, None, None, None),
        (bst_id, "14", 13, None, None, None),
        (bst_id, "4", 15, None, None, None),
        (bst_id, "7", 15, None, None, None),
        (bst_id, "13", 16, None, None, None),
        (bst_id, "9", 13, None, None, None),
    ]
    conn.executemany(
        "INSERT INTO stablo_cvor (stablo_id, vrijednost, parent_id, lijevi_id, desni_id, redoslijed) VALUES (?, ?, ?, ?, ?, ?);",
        bst_nodes,
    )

    bst_lookup = {
        row[1]: row[0]
        for row in conn.execute("SELECT id, vrijednost FROM stablo_cvor WHERE stablo_id = ?;", (bst_id,))
    }
    conn.execute(
        "UPDATE stablo_cvor SET lijevi_id = ?, desni_id = ? WHERE id = ?;",
        (bst_lookup["3"], bst_lookup["10"], bst_lookup["8"]),
    )
    conn.execute(
        "UPDATE stablo_cvor SET lijevi_id = ?, desni_id = ? WHERE id = ?;",
        (bst_lookup["1"], bst_lookup["6"], bst_lookup["3"]),
    )
    conn.execute(
        "UPDATE stablo_cvor SET lijevi_id = ?, desni_id = ? WHERE id = ?;",
        (bst_lookup["9"], bst_lookup["14"], bst_lookup["10"]),
    )
    conn.execute(
        "UPDATE stablo_cvor SET lijevi_id = ?, desni_id = ? WHERE id = ?;",
        (bst_lookup["4"], bst_lookup["7"], bst_lookup["6"]),
    )
    conn.execute(
        "UPDATE stablo_cvor SET lijevi_id = ? WHERE id = ?;",
        (bst_lookup["13"], bst_lookup["14"]),
    )

    conn.execute("INSERT INTO stog_red (naziv, tip) VALUES (?, ?);", ("StogA", "stog"))
    conn.execute("INSERT INTO stog_red (naziv, tip) VALUES (?, ?);", ("RedA", "red"))
    stog_id = conn.execute("SELECT id FROM stog_red WHERE naziv = ?;", ("StogA",)).fetchone()[0]
    red_id = conn.execute("SELECT id FROM stog_red WHERE naziv = ?;", ("RedA",)).fetchone()[0]

    stog_items = [(stog_id, str(v), i) for i, v in enumerate(["A", "B", "C", "D", "E"], start=1)]
    red_items = [(red_id, str(v), i) for i, v in enumerate(["1", "2", "3", "4", "5", "6"], start=1)]

    conn.executemany(
        "INSERT INTO stog_red_element (stog_red_id, vrijednost, pozicija) VALUES (?, ?, ?);",
        stog_items,
    )
    conn.executemany(
        "INSERT INTO stog_red_element (stog_red_id, vrijednost, pozicija) VALUES (?, ?, ?);",
        red_items,
    )

    conn.commit()
    conn.close()
