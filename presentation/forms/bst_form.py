"""BST form dialogs."""

import tkinter as tk
from tkinter import messagebox, ttk

from services.adt_service import (
    add_bst_node,
    collect_state,
    delete_bst_node,
    update_bst_node_value,
)
from presentation.utils import build_option_map, confirm_delete, ensure_db


def open_bst_form(parent: tk.Tk | tk.Toplevel) -> None:
    """Open form to add a new BST node."""
    db_path = ensure_db()
    if not db_path:
        return

    win = tk.Toplevel(parent)
    win.title("Add - BST node")
    win.geometry("360x260")

    state = collect_state(db_path, "trenutno")
    parent_options: list[tuple[str, int | None]] = []
    for row in state.bst_rows:
        left = "free" if row.get("lijevi_id") is None else f"{row['lijevi_id']}"
        right = "free" if row.get("desni_id") is None else f"{row['desni_id']}"
        parent_options.append((f"{row['id']} | v={row['vrijednost']} | L:{left} R:{right}", int(row["id"])))

    if not parent_options:
        messagebox.showwarning("ADT", "No BST nodes available for parent selection.")
        win.destroy()
        return

    parent_map = build_option_map(parent_options)

    tk.Label(win, text="Value").pack(pady=(12, 2))
    value_entry = tk.Entry(win)
    value_entry.pack(fill="x", padx=16)

    tk.Label(win, text="Parent node").pack(pady=(8, 2))
    parent_var = tk.StringVar(value=parent_options[0][0])
    parent_combo = ttk.Combobox(
        win,
        textvariable=parent_var,
        values=[label for label, _ in parent_options],
        state="readonly",
    )
    parent_combo.pack(fill="x", padx=16)

    tk.Label(win, text="Side (L/R)").pack(pady=(8, 2))
    side_var = tk.StringVar(value="L")
    side_menu = tk.OptionMenu(win, side_var, "L", "R")
    side_menu.pack(pady=2)

    def submit() -> None:
        try:
            vrijednost = value_entry.get().strip()
            if not vrijednost:
                raise ValueError("Value is required.")
            parent_id = parent_map.get(parent_var.get())
            if parent_id is None:
                raise ValueError("Select a parent node.")
            new_id = add_bst_node(db_path, vrijednost, parent_id, side_var.get())
            messagebox.showinfo("ADT", f"Added BST node ID: {new_id}")
            win.destroy()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("ADT", f"Error: {exc}")

    tk.Button(win, text="Save", command=submit).pack(pady=12)


def open_bst_manage_form(parent: tk.Tk | tk.Toplevel) -> None:
    """Open form to edit or delete a BST node."""
    db_path = ensure_db()
    if not db_path:
        return

    win = tk.Toplevel(parent)
    win.title("Edit/Delete - BST")
    win.geometry("400x380")

    state = collect_state(db_path, "trenutno")
    node_options: list[tuple[str, int | None]] = []
    node_rows: dict[int, dict] = {}
    for row in state.bst_rows:
        node_id = int(row["id"])
        left = "free" if row.get("lijevi_id") is None else str(row.get("lijevi_id"))
        right = "free" if row.get("desni_id") is None else str(row.get("desni_id"))
        node_rows[node_id] = row
        node_options.append((f"{node_id} | v={row['vrijednost']} | L:{left} R:{right}", node_id))

    if not node_options:
        messagebox.showwarning("ADT", "No BST nodes available for edit/delete.")
        win.destroy()
        return

    node_map = build_option_map(node_options)

    safe_delete_options = [
        (label, value)
        for label, value in node_options
        if value is not None
        and node_rows[int(value)].get("lijevi_id") is None
        and node_rows[int(value)].get("desni_id") is None
    ]

    tk.Label(win, text="BST node").pack(pady=(12, 2))
    node_var = tk.StringVar(value=node_options[0][0])
    node_combo = ttk.Combobox(
        win,
        textvariable=node_var,
        values=[label for label, _ in node_options],
        state="readonly",
    )
    node_combo.pack(fill="x", padx=16)

    tk.Label(win, text="New value (for edit)").pack(pady=(8, 2))
    value_entry = tk.Entry(win)
    value_entry.pack(fill="x", padx=16)

    tk.Label(win, text="Delete - node selection").pack(pady=(10, 2))
    delete_var = tk.StringVar()
    delete_combo = ttk.Combobox(win, textvariable=delete_var, state="readonly")
    delete_combo.pack(fill="x", padx=16)

    show_all_delete_var = tk.BooleanVar(value=False)
    tk.Checkbutton(
        win,
        text="Show all BST nodes for deletion (warning)",
        variable=show_all_delete_var,
    ).pack(anchor="w", padx=16, pady=(4, 0))

    def refresh_delete_combo() -> None:
        active_options = node_options if show_all_delete_var.get() else safe_delete_options
        labels = [label for label, _ in active_options]
        delete_combo.configure(values=labels)
        if not labels:
            delete_var.set("")
            return
        if delete_var.get() not in labels:
            delete_var.set(labels[0])

    show_all_delete_var.trace_add("write", lambda *_: refresh_delete_combo())
    refresh_delete_combo()

    def _fill_from_selection(*_: object) -> None:
        selected_id = node_map.get(node_var.get())
        row = node_rows.get(int(selected_id)) if selected_id is not None else None
        if row is None:
            return
        value_entry.delete(0, tk.END)
        value_entry.insert(0, str(row.get("vrijednost", "")))

    node_combo.bind("<<ComboboxSelected>>", _fill_from_selection)
    _fill_from_selection()

    def do_update() -> None:
        try:
            node_id = node_map.get(node_var.get())
            if node_id is None:
                raise ValueError("Select a BST node.")
            vrijednost = value_entry.get().strip()
            if not vrijednost:
                raise ValueError("Value is required for editing.")
            update_bst_node_value(db_path, int(node_id), vrijednost)
            messagebox.showinfo("ADT", "BST node updated.")
            win.destroy()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("ADT", f"Error: {exc}")

    def do_delete() -> None:
        try:
            node_id = node_map.get(delete_var.get())
            if node_id is None:
                raise ValueError("Select a BST node to delete.")

            row = node_rows.get(int(node_id))
            if row is None:
                raise ValueError("Selected BST node no longer exists.")

            description = (
                f"ID={node_id} | vrijednost={row.get('vrijednost')} | "
                f"L={row.get('lijevi_id')} | R={row.get('desni_id')}"
            )
            if not confirm_delete(win, "Delete BST node", description):
                return

            delete_bst_node(db_path, int(node_id))
            messagebox.showinfo("ADT", "BST node deleted.")
            win.destroy()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("ADT", f"Error: {exc}")

    tk.Button(win, text="Edit", command=do_update).pack(pady=(12, 4))
    tk.Button(win, text="Delete", command=do_delete).pack(pady=4)
