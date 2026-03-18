"""Sidebar panels for the Visual Studio window."""

import tkinter as tk
from typing import Callable, Iterable

from presentation.forms.bst_form import open_bst_form, open_bst_manage_form
from presentation.forms.general_tree_form import open_general_tree_form, open_general_tree_manage_form
from presentation.forms.hash_form import open_hash_form, open_hash_manage_form
from presentation.forms.recursion_form import open_recursion_form, open_recursion_manage_form


def create_navigation_panel(parent: tk.Widget, view_names: Iterable[str], on_show_view: Callable[[str], None]) -> tk.LabelFrame:
    panel = tk.LabelFrame(parent, text="Views", bg="#eef3f8", padx=8, pady=6)
    panel.pack(fill="x", padx=10, pady=(6, 6))
    for name in view_names:
        tk.Button(panel, text=f"[{name}]", anchor="w", width=16, command=lambda view_name=name: on_show_view(view_name)).pack(pady=3)
    return panel


def create_crud_panel(parent: tk.Widget, studio_parent: tk.Misc, refresh_current_view: Callable[[], None]) -> tk.LabelFrame:
    panel = tk.LabelFrame(parent, text="CRUD", bg="#eef3f8", padx=8, pady=6)
    panel.pack(fill="x", padx=10, pady=(6, 10))
    tk.Button(panel, text="Hash: Add", anchor="w", width=16, command=lambda: open_hash_form(studio_parent)).pack(pady=2)
    tk.Button(panel, text="Hash: Edit/Delete", anchor="w", width=16, command=lambda: open_hash_manage_form(studio_parent)).pack(pady=2)
    tk.Button(panel, text="Recursion: Add", anchor="w", width=16, command=lambda: open_recursion_form(studio_parent)).pack(pady=2)
    tk.Button(panel, text="Recursion: Edit/Delete", anchor="w", width=16, command=lambda: open_recursion_manage_form(studio_parent)).pack(pady=2)
    tk.Button(panel, text="Tree: Add", anchor="w", width=16, command=lambda: open_general_tree_form(studio_parent)).pack(pady=2)
    tk.Button(panel, text="Tree: Edit/Delete", anchor="w", width=16, command=lambda: open_general_tree_manage_form(studio_parent)).pack(pady=2)
    tk.Button(panel, text="BST: Add", anchor="w", width=16, command=lambda: open_bst_form(studio_parent)).pack(pady=2)
    tk.Button(panel, text="BST: Edit/Delete", anchor="w", width=16, command=lambda: open_bst_manage_form(studio_parent)).pack(pady=2)
    tk.Button(panel, text="Refresh Active View", anchor="w", width=16, command=refresh_current_view).pack(pady=(6, 2))
    return panel
