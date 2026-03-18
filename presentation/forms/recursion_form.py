"""Recursion call form dialogs."""

import tkinter as tk
from tkinter import messagebox, ttk

from services.adt_service import (
    add_recursion_call,
    collect_state,
    delete_recursion_call,
    update_recursion_call,
)
from presentation.utils import build_option_map, confirm_delete, ensure_db, parse_optional_int


def open_recursion_form(parent: tk.Tk | tk.Toplevel) -> None:
    """Open form to add a new recursion call."""
    db_path = ensure_db()
    if not db_path:
        return

    win = tk.Toplevel(parent)
    win.title("Add - Recursion")
    win.geometry("360x360")

    state = collect_state(db_path, "trenutno")
    parent_options: list[tuple[str, int | None]] = [("(no parent)", None)]
    for row in state.recursion_rows:
        parent_options.append((f"{row['id']} | {row['oznaka']} | arg={row['argument']}", int(row["id"])))
    parent_map = build_option_map(parent_options)

    tk.Label(win, text="Label").pack(pady=(12, 2))
    oznaka_entry = tk.Entry(win)
    oznaka_entry.pack(fill="x", padx=16)

    tk.Label(win, text="Function").pack(pady=(8, 2))
    funkcija_entry = tk.Entry(win)
    funkcija_entry.pack(fill="x", padx=16)

    tk.Label(win, text="Argument").pack(pady=(8, 2))
    argument_entry = tk.Entry(win)
    argument_entry.pack(fill="x", padx=16)

    tk.Label(win, text="Return (optional)").pack(pady=(8, 2))
    povrat_entry = tk.Entry(win)
    povrat_entry.pack(fill="x", padx=16)

    tk.Label(win, text="Parent node (optional)").pack(pady=(8, 2))
    parent_var = tk.StringVar(value=parent_options[0][0])
    parent_combo = ttk.Combobox(
        win,
        textvariable=parent_var,
        values=[label for label, _ in parent_options],
        state="readonly",
    )
    parent_combo.pack(fill="x", padx=16)

    def submit() -> None:
        try:
            oznaka = oznaka_entry.get().strip()
            funkcija = funkcija_entry.get().strip()
            argument = argument_entry.get().strip()
            povrat = povrat_entry.get().strip() or None
            parent_id = parent_map.get(parent_var.get())
            if not oznaka or not funkcija or not argument:
                raise ValueError("Label, function, and argument are required.")
            new_id = add_recursion_call(db_path, oznaka, funkcija, argument, povrat, parent_id)
            messagebox.showinfo("ADT", f"Added call ID: {new_id}")
            win.destroy()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("ADT", f"Error: {exc}")

    tk.Button(win, text="Save", command=submit).pack(pady=12)


def open_recursion_manage_form(parent: tk.Tk | tk.Toplevel) -> None:
    """Open form to edit or delete a recursion call."""
    db_path = ensure_db()
    if not db_path:
        return

    win = tk.Toplevel(parent)
    win.title("Edit/Delete - Recursion")
    win.geometry("400x520")

    state = collect_state(db_path, "trenutno")
    call_options: list[tuple[str, int | None]] = []
    call_rows: dict[int, dict] = {}
    for row in state.recursion_rows:
        call_id = int(row["id"])
        call_rows[call_id] = row
        call_options.append((f"{call_id} | {row['oznaka']} | arg={row['argument']}", call_id))

    if not call_options:
        messagebox.showwarning("ADT", "No recursive calls available for edit/delete.")
        win.destroy()
        return

    call_map = build_option_map(call_options)

    child_parent_ids = {int(row["parent_id"]) for row in state.recursion_rows if row.get("parent_id") is not None}
    safe_delete_options = [(label, value) for label, value in call_options if value not in child_parent_ids]

    parent_options: list[tuple[str, int | None]] = [("(no parent)", None)]
    for row in state.recursion_rows:
        parent_options.append((f"{row['id']} | {row['oznaka']}", int(row["id"])))
    parent_map = build_option_map(parent_options)

    tk.Label(win, text="Call").pack(pady=(12, 2))
    call_var = tk.StringVar(value=call_options[0][0])
    call_combo = ttk.Combobox(
        win,
        textvariable=call_var,
        values=[label for label, _ in call_options],
        state="readonly",
    )
    call_combo.pack(fill="x", padx=16)

    tk.Label(win, text="Label (for edit)").pack(pady=(8, 2))
    oznaka_entry = tk.Entry(win)
    oznaka_entry.pack(fill="x", padx=16)

    tk.Label(win, text="Function (for edit)").pack(pady=(8, 2))
    funkcija_entry = tk.Entry(win)
    funkcija_entry.pack(fill="x", padx=16)

    tk.Label(win, text="Argument (for edit)").pack(pady=(8, 2))
    argument_entry = tk.Entry(win)
    argument_entry.pack(fill="x", padx=16)

    tk.Label(win, text="Return (optional)").pack(pady=(8, 2))
    povrat_entry = tk.Entry(win)
    povrat_entry.pack(fill="x", padx=16)

    tk.Label(win, text="Parent node (optional)").pack(pady=(8, 2))
    parent_var = tk.StringVar(value=parent_options[0][0])
    parent_combo = ttk.Combobox(
        win,
        textvariable=parent_var,
        values=[label for label, _ in parent_options],
        state="readonly",
    )
    parent_combo.pack(fill="x", padx=16)

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
        active_options = call_options if show_all_delete_var.get() else safe_delete_options
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
        selected_id = call_map.get(call_var.get())
        row = call_rows.get(int(selected_id)) if selected_id is not None else None
        if row is None:
            return
        oznaka_entry.delete(0, tk.END)
        oznaka_entry.insert(0, str(row.get("oznaka", "")))
        funkcija_entry.delete(0, tk.END)
        funkcija_entry.insert(0, str(row.get("funkcija", "")))
        argument_entry.delete(0, tk.END)
        argument_entry.insert(0, str(row.get("argument", "")))
        povrat_entry.delete(0, tk.END)
        if row.get("povrat") is not None:
            povrat_entry.insert(0, str(row.get("povrat")))

        parent_id = row.get("parent_id")
        if parent_id is None:
            parent_var.set(parent_options[0][0])
        else:
            matching = next((label for label, value in parent_options if value == int(parent_id)), parent_options[0][0])
            parent_var.set(matching)

    call_combo.bind("<<ComboboxSelected>>", _fill_from_selection)
    _fill_from_selection()

    def do_update() -> None:
        try:
            call_id = call_map.get(call_var.get())
            if call_id is None:
                raise ValueError("Select a call.")
            oznaka = oznaka_entry.get().strip()
            funkcija = funkcija_entry.get().strip()
            argument = argument_entry.get().strip()
            povrat = povrat_entry.get().strip() or None
            parent_id = parent_map.get(parent_var.get())
            if not oznaka or not funkcija or not argument:
                raise ValueError("Label, function, and argument are required for editing.")
            update_recursion_call(db_path, int(call_id), oznaka, funkcija, argument, povrat, parent_id)
            messagebox.showinfo("ADT", "Recursive call updated.")
            win.destroy()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("ADT", f"Error: {exc}")

    def do_delete() -> None:
        try:
            call_id = call_map.get(delete_var.get())
            if call_id is None:
                raise ValueError("Select a call to delete.")

            row = call_rows.get(int(call_id))
            if row is None:
                raise ValueError("Selected recursive call no longer exists.")

            description = (
                f"ID={call_id} | oznaka={row.get('oznaka')} | funkcija={row.get('funkcija')} | "
                f"argument={row.get('argument')}"
            )
            if not confirm_delete(win, "Delete recursive call", description):
                return

            delete_recursion_call(db_path, int(call_id))
            messagebox.showinfo("ADT", "Recursive call deleted.")
            win.destroy()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("ADT", f"Error: {exc}")

    tk.Button(win, text="Edit", command=do_update).pack(pady=(12, 4))
    tk.Button(win, text="Delete", command=do_delete).pack(pady=4)
