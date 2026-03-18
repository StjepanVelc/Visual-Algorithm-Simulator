"""General tree view for the algorithm studio."""

import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Callable

from services.adt_service import collect_state
from presentation.canvas.interactions import animate_travel_roundtrip, bind_canvas_interactions, highlight_node
from presentation.canvas.layouts import build_general_tree_layout
from presentation.canvas.renderers import render_tree_canvas, setup_scrollable_canvas
from presentation.canvas.traversals import build_general_traversal_order


def create_general_tree_view(
    parent: tk.Widget,
    db_path: Path,
    capture_frame: Callable[[tk.Canvas], None],
) -> tuple[tk.Frame, Callable[[], None]]:
    view = tk.Frame(parent)
    controls = tk.Frame(view)
    controls.pack(fill="x", padx=10, pady=8)
    tk.Label(controls, text="General Tree - step mode", font=("Segoe UI", 12, "bold")).pack(side="left")

    mode_var = tk.StringVar(value="BFS")
    ttk.Combobox(controls, textvariable=mode_var, values=["BFS", "DFS"], state="readonly", width=8).pack(side="left", padx=8)

    canvas = setup_scrollable_canvas(view)
    details = tk.Label(view, text="Click a node for details.", anchor="w")
    details.pack(fill="x", padx=8, pady=(2, 8))
    bind_canvas_interactions(canvas, details)

    order: list[int] = []
    index = 0
    next_button_ref: list[tk.Button | None] = [None]
    status_ref: list[tk.Label | None] = [None]

    def refresh() -> None:
        nonlocal order, index
        state = collect_state(db_path, "studio")
        render_tree_canvas(canvas, state.opce_rows, "vrijednost", build_general_tree_layout)
        capture_frame(canvas)
        order = []
        index = 0

    def prepare_steps() -> None:
        nonlocal order, index
        state = collect_state(db_path, "studio")
        order = build_general_traversal_order(state.opce_rows, mode_var.get())
        index = 0
        if next_button_ref[0]:
            next_button_ref[0].configure(state="normal")
        if status_ref[0]:
            status_ref[0].configure(text="")

    def next_step() -> None:
        nonlocal index
        if index >= len(order):
            if next_button_ref[0]:
                next_button_ref[0].configure(state="disabled")
            if status_ref[0]:
                status_ref[0].configure(text="-> Completed")
            return

        node_id = int(order[index])
        if next_button_ref[0]:
            next_button_ref[0].configure(state="disabled")

        def finish_step() -> None:
            nonlocal index
            highlight_node(canvas, node_id)
            index += 1
            capture_frame(canvas)
            if next_button_ref[0]:
                if index >= len(order):
                    next_button_ref[0].configure(state="disabled")
                    if status_ref[0]:
                        status_ref[0].configure(text="-> Completed")
                else:
                    next_button_ref[0].configure(state="normal")

        animate_travel_roundtrip(
            canvas,
            node_id,
            lambda: capture_frame(canvas),
            finish_step,
        )

    buttons = tk.Frame(view)
    buttons.pack(fill="x", padx=12, pady=(0, 8))
    tk.Button(buttons, text="Refresh", command=refresh).pack(side="left", padx=4)
    tk.Button(buttons, text="Prepare steps", command=prepare_steps).pack(side="left", padx=4)
    next_button_ref[0] = tk.Button(buttons, text="Next step", command=next_step)
    next_button_ref[0].pack(side="left", padx=4)
    status_ref[0] = tk.Label(buttons, text="", fg="#c0392b", font=("Segoe UI", 9, "bold"))
    status_ref[0].pack(side="left", padx=8)

    return view, refresh
