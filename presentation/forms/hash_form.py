"""Hash table form dialogs."""

import tkinter as tk
from tkinter import messagebox, ttk

from services.adt_service import add_hash_node, collect_state, delete_hash_node, update_hash_node
from presentation.utils import build_option_map, confirm_delete, ensure_db


def open_hash_form(parent: tk.Tk | tk.Toplevel) -> None:
    """Open form to add a new hash node."""
    db_path = ensure_db()
    if not db_path:
        return

    win = tk.Toplevel(parent)
    win.title("Add - Hash node")
    win.geometry("360x240")

    state = collect_state(db_path, "trenutno")
    bucket_values = sorted({int(row["bucket"]) for row in state.hash_rows if row.get("bucket") is not None})
    if not bucket_values:
        bucket_values = list(range(8))

    tk.Label(win, text="Bucket indeks").pack(pady=(12, 2))
    bucket_var = tk.StringVar(value=str(bucket_values[0]))
    bucket_combo = ttk.Combobox(
        win,
        textvariable=bucket_var,
        values=[str(bucket) for bucket in bucket_values],
        state="readonly",
    )
    bucket_combo.pack(fill="x", padx=16)

    tk.Label(win, text="Kljuc").pack(pady=(8, 2))
    key_entry = tk.Entry(win)
    key_entry.pack(fill="x", padx=16)

    tk.Label(win, text="Value").pack(pady=(8, 2))
    value_entry = tk.Entry(win)
    value_entry.pack(fill="x", padx=16)

    def submit() -> None:
        try:
            bucket_index = int(bucket_var.get())
            key = key_entry.get().strip()
            value = value_entry.get().strip()
            if not key or not value:
                raise ValueError("Key and value are required.")
            new_id = add_hash_node(db_path, bucket_index, key, value)
            messagebox.showinfo("ADT", f"Added hash node ID: {new_id}")
            win.destroy()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("ADT", f"Error: {exc}")

    tk.Button(win, text="Save", command=submit).pack(pady=12)


def open_hash_manage_form(parent: tk.Tk | tk.Toplevel) -> None:
    """Open form to edit or delete a hash node."""
    db_path = ensure_db()
    if not db_path:
        return

    win = tk.Toplevel(parent)
    win.title("Edit/Delete - Hash node")
    win.geometry("380x320")

    state = collect_state(db_path, "trenutno")
    options: list[tuple[str, int | None]] = []
    node_rows: dict[int, dict] = {}
    for row in state.hash_rows:
        node_id = row.get("cvor_id")
        if node_id is None:
            continue
        node_id_int = int(node_id)
        node_rows[node_id_int] = row
        options.append((f"{node_id_int} | b={row['bucket']} | {row['kljuc']}={row['vrijednost']}", node_id_int))

    if not options:
        messagebox.showwarning("ADT", "No hash nodes available for edit/delete.")
        win.destroy()
        return

    option_map = build_option_map(options)

    tk.Label(win, text="Hash node").pack(pady=(12, 2))
    node_var = tk.StringVar(value=options[0][0])
    node_combo = ttk.Combobox(
        win,
        textvariable=node_var,
        values=[label for label, _ in options],
        state="readonly",
    )
    node_combo.pack(fill="x", padx=16)

    tk.Label(win, text="New key (for edit)").pack(pady=(8, 2))
    key_entry = tk.Entry(win)
    key_entry.pack(fill="x", padx=16)

    tk.Label(win, text="New value (for edit)").pack(pady=(8, 2))
    value_entry = tk.Entry(win)
    value_entry.pack(fill="x", padx=16)

    def _fill_from_selection(*_: object) -> None:
        selected_id = option_map.get(node_var.get())
        row = node_rows.get(int(selected_id)) if selected_id is not None else None
        if row is None:
            return
        key_entry.delete(0, tk.END)
        key_entry.insert(0, str(row.get("kljuc", "")))
        value_entry.delete(0, tk.END)
        value_entry.insert(0, str(row.get("vrijednost", "")))

    node_combo.bind("<<ComboboxSelected>>", _fill_from_selection)
    _fill_from_selection()

    def do_update() -> None:
        try:
            node_id = option_map.get(node_var.get())
            if node_id is None:
                raise ValueError("Select a hash node.")
            key = key_entry.get().strip()
            value = value_entry.get().strip()
            if not key or not value:
                raise ValueError("Key and value are required for editing.")
            update_hash_node(db_path, int(node_id), key, value)
            messagebox.showinfo("ADT", "Hash node updated.")
            win.destroy()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("ADT", f"Error: {exc}")

    def do_delete() -> None:
        try:
            node_id = option_map.get(node_var.get())
            if node_id is None:
                raise ValueError("Select a hash node.")

            row = node_rows.get(int(node_id))
            if row is None:
                raise ValueError("Selected hash node no longer exists.")

            description = f"ID={node_id} | bucket={row.get('bucket')} | kljuc={row.get('kljuc')} | vrijednost={row.get('vrijednost')}"
            if not confirm_delete(win, "Delete hash node", description):
                return

            delete_hash_node(db_path, int(node_id))
            messagebox.showinfo("ADT", "Hash node deleted.")
            win.destroy()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("ADT", f"Error: {exc}")

    tk.Button(win, text="Edit", command=do_update).pack(pady=(12, 4))
    tk.Button(win, text="Delete", command=do_delete).pack(pady=4)
