"""Main GUI entry point and Visual Studio interface."""

import tkinter as tk
from typing import Callable

from presentation.db_operations import on_build_db, on_export_sql, on_generate_report, on_import_sql
from presentation.studio import create_capture_context, create_crud_panel, create_navigation_panel
from presentation.utils import ensure_db
from presentation.views import create_bst_view, create_general_tree_view, create_hash_view, create_recursion_view


def open_algorithm_studio(parent: tk.Tk | tk.Toplevel) -> None:
    db_path = ensure_db()
    if not db_path:
        return

    win = tk.Toplevel(parent)
    win.title("ADT Visual Studio")
    win.geometry("1260x780")

    root = tk.Frame(win)
    root.pack(fill="both", expand=True)

    sidebar = tk.Frame(root, width=180, bg="#eef3f8")
    sidebar.pack(side="left", fill="y")
    content = tk.Frame(root)
    content.pack(side="right", fill="both", expand=True)

    capture_context = create_capture_context(sidebar)

    views: dict[str, tk.Frame] = {}
    refreshers: dict[str, Callable[[], None]] = {}
    current_view: list[str] = ["BST"]

    def show_view(name: str) -> None:
        for view in views.values():
            view.pack_forget()
        views[name].pack(fill="both", expand=True)
        current_view[0] = name

    hash_view, refresh_hash = create_hash_view(content, db_path)
    bst_view, refresh_bst_view = create_bst_view(
        content,
        win,
        db_path,
        capture_context.recording_var,
        capture_context.frame_store,
        capture_context.imageio_module,
        capture_context.capture_frame,
        capture_context.clear_recording_state,
    )
    recursion_view, refresh_recursion_view = create_recursion_view(content, db_path, capture_context.capture_frame)
    general_tree_view, refresh_general_tree_view = create_general_tree_view(content, db_path, capture_context.capture_frame)

    views["Hash"] = hash_view
    views["BST"] = bst_view
    views["Recursion"] = recursion_view
    views["General Tree"] = general_tree_view

    refreshers["Hash"] = refresh_hash
    refreshers["BST"] = refresh_bst_view
    refreshers["Recursion"] = refresh_recursion_view
    refreshers["General Tree"] = refresh_general_tree_view

    def refresh_current_view() -> None:
        refreshers[current_view[0]]()

    create_navigation_panel(sidebar, ["Hash", "BST", "Recursion", "General Tree"], show_view)
    create_crud_panel(sidebar, win, refresh_current_view)

    refresh_hash()
    refresh_bst_view()
    refresh_recursion_view()
    refresh_general_tree_view()
    show_view("BST")


def build_ui() -> tk.Tk:
    root = tk.Tk()
    root.title("ADT - Control Center")
    root.geometry("420x300")

    frame = tk.Frame(root, padx=16, pady=16)
    frame.pack(fill="both", expand=True)

    title = tk.Label(frame, text="ADT - database management", font=("Segoe UI", 14, "bold"))
    title.pack(pady=(0, 12))

    tk.Button(frame, text="1) Create database", command=on_build_db, width=30).pack(pady=4)
    tk.Button(frame, text="2) Generate HTML", command=on_generate_report, width=30).pack(pady=4)
    tk.Button(frame, text="3) Export SQL", command=on_export_sql, width=30).pack(pady=4)
    tk.Button(frame, text="4) Load SQL", command=on_import_sql, width=30).pack(pady=4)
    tk.Button(frame, text="5) Visual Studio", command=lambda: open_algorithm_studio(root), width=30).pack(pady=4)

    info = tk.Label(
        frame,
        text="Database: adt.db\nHTML report: izvjestaji/stabla.html",
        justify="left",
    )
    info.pack(pady=(12, 0))

    return root


def main() -> None:
    root = build_ui()
    root.mainloop()


if __name__ == "__main__":
    main()
