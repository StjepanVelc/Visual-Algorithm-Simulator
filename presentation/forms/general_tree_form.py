"""General tree form dialogs."""

import tkinter as tk
from tkinter import messagebox, ttk

from services.adt_service import (
    add_general_tree_node,
    collect_state,
    delete_general_tree_node,
    update_general_tree_node,
)
from presentation.utils import build_option_map, confirm_delete, ensure_db, parse_optional_int


def open_general_tree_form(parent: tk.Tk | tk.Toplevel) -> None:
    """Open form to add a new general tree node."""
    db_path = ensure_db()
    if not db_path:
        return

    win = tk.Toplevel(parent)
    win.title("Add - General Tree")
    win.geometry("360x290")

    state = collect_state(db_path, "trenutno")
    parent_options: list[tuple[str, int | None]] = [("(root node)", None)]
    for row in state.opce_rows:
        parent_options.append((f"{row['id']} | {row['vrijednost']}", int(row["id"])))
    parent_map = build_option_map(parent_options)

    tk.Label(win, text="Value").pack(pady=(12, 2))
    value_entry = tk.Entry(win)
    value_entry.pack(fill="x", padx=16)

    tk.Label(win, text="Parent node (optional)").pack(pady=(8, 2))
    parent_var = tk.StringVar(value=parent_options[0][0])
    parent_combo = ttk.Combobox(
        win,
        textvariable=parent_var,
        values=[label for label, _ in parent_options],
        state="readonly",
    )
    parent_combo.pack(fill="x", padx=16)

    tk.Label(win, text="Order (optional)").pack(pady=(8, 2))
    order_entry = tk.Entry(win)
    order_entry.pack(fill="x", padx=16)

    def submit() -> None:
        try:
            vrijednost = value_entry.get().strip()
            parent_id = parent_map.get(parent_var.get())
            redoslijed = parse_optional_int(order_entry.get())
            if not vrijednost:
                raise ValueError("Value is required.")
            new_id = add_general_tree_node(db_path, vrijednost, parent_id, redoslijed)
            messagebox.showinfo("ADT", f"Added node ID: {new_id}")
            win.destroy()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("ADT", f"Error: {exc}")

    tk.Button(win, text="Save", command=submit).pack(pady=12)


def open_general_tree_manage_form(parent: tk.Tk | tk.Toplevel) -> None:
    """Open form to edit or delete a general tree node."""
    db_path = ensure_db()
    if not db_path:
        return

    win = tk.Toplevel(parent)
    win.title("Edit/Delete - General Tree")
    win.geometry("400x440")

    state = collect_state(db_path, "trenutno")
    node_options: list[tuple[str, int | None]] = []
    node_rows: dict[int, dict] = {}
    for row in state.opce_rows:
        node_id = int(row["id"])
        node_rows[node_id] = row
        node_options.append((f"{node_id} | {row['vrijednost']}", node_id))

    if not node_options:
        messagebox.showwarning("ADT", "No general-tree nodes available for edit/delete.")
        win.destroy()
        return

    node_map = build_option_map(node_options)

    child_parent_ids = {int(row["parent_id"]) for row in state.opce_rows if row.get("parent_id") is not None}
    safe_delete_options = [(label, value) for label, value in node_options if value not in child_parent_ids]

    parent_options: list[tuple[str, int | None]] = [("(root node)", None)]
    for row in state.opce_rows:
        parent_options.append((f"{row['id']} | {row['vrijednost']}", int(row["id"])))
    parent_map = build_option_map(parent_options)

    tk.Label(win, text="Node").pack(pady=(12, 2))
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

    tk.Label(win, text="Parent node (optional)").pack(pady=(8, 2))
    parent_var = tk.StringVar(value=parent_options[0][0])
    parent_combo = ttk.Combobox(
        win,
        textvariable=parent_var,
        values=[label for label, _ in parent_options],
        state="readonly",
    )
    parent_combo.pack(fill="x", padx=16)

    tk.Label(win, text="Order (optional)").pack(pady=(8, 2))
    order_entry = tk.Entry(win)
    order_entry.pack(fill="x", padx=16)

    tk.Label(win, text="Delete - node selection").pack(pady=(10, 2))
    delete_var = tk.StringVar()
    delete_combo = ttk.Combobox(win, textvariable=delete_var, state="readonly")
    delete_combo.pack(fill="x", padx=16)

    show_all_delete_var = tk.BooleanVar(value=False)
    tk.Checkbutton(
        win,
        text="Show all nodes for deletion (warning)",
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

        order_entry.delete(0, tk.END)
        if row.get("redoslijed") is not None:
            order_entry.insert(0, str(row.get("redoslijed")))

        parent_id = row.get("parent_id")
        if parent_id is None:
            parent_var.set(parent_options[0][0])
        else:
            matching = next((label for label, value in parent_options if value == int(parent_id)), parent_options[0][0])
            parent_var.set(matching)

    node_combo.bind("<<ComboboxSelected>>", _fill_from_selection)
    _fill_from_selection()

    def do_update() -> None:
        try:
            node_id = node_map.get(node_var.get())
            if node_id is None:
                raise ValueError("Select a node.")
            vrijednost = value_entry.get().strip()
            parent_id = parent_map.get(parent_var.get())
            redoslijed = parse_optional_int(order_entry.get())
            if not vrijednost:
                raise ValueError("Value is required for editing.")
            update_general_tree_node(db_path, int(node_id), vrijednost, parent_id, redoslijed)
            messagebox.showinfo("ADT", "General-tree node updated.")
            win.destroy()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("ADT", f"Error: {exc}")

    def do_delete() -> None:
        try:
            node_id = node_map.get(delete_var.get())
            if node_id is None:
                raise ValueError("Select a node to delete.")

            row = node_rows.get(int(node_id))
            if row is None:
                raise ValueError("Selected node no longer exists.")

            description = f"ID={node_id} | vrijednost={row.get('vrijednost')} | parent={row.get('parent_id')}"
            if not confirm_delete(win, "Delete general-tree node", description):
                return

            delete_general_tree_node(db_path, int(node_id))
            messagebox.showinfo("ADT", "General-tree node deleted.")
            win.destroy()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("ADT", f"Error: {exc}")

    tk.Button(win, text="Edit", command=do_update).pack(pady=(12, 4))
    tk.Button(win, text="Delete", command=do_delete).pack(pady=4)
