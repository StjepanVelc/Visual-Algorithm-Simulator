"""BST view for the algorithm studio."""

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any, Callable

from services.adt_service import add_bst_node, collect_state, insert_bst_node_auto
from presentation.canvas.interactions import animate_travel_roundtrip, bind_canvas_interactions, highlight_node, highlight_search_path, mark_trail_node
from presentation.canvas.layouts import build_bst_layout
from presentation.canvas.renderers import render_tree_canvas, setup_scrollable_canvas
from presentation.canvas.traversals import build_bst_traversal_order
from presentation.recording.capture import ImageGrab
from presentation.recording.export import clear_recorded_frames, export_gif, export_video
from presentation.utils import add_depth_legend, build_option_map


def create_bst_view(
    parent: tk.Widget,
    studio_parent: tk.Misc,
    db_path: Path,
    recording_var: tk.BooleanVar,
    frame_store: list,
    imageio_module: Any,
    capture_frame: Callable[[tk.Canvas], None],
    on_clear_frames: Callable[[], None],
) -> tuple[tk.Frame, Callable[[], None]]:
    view = tk.Frame(parent)
    control = tk.Frame(view)
    control.pack(fill="x", padx=10, pady=8)

    tk.Label(control, text="BST Simulator", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=6, sticky="w")
    tk.Checkbutton(control, text="Record frames (global)", variable=recording_var).grid(row=0, column=6, sticky="w", padx=8)

    tk.Label(control, text="Value").grid(row=1, column=0, sticky="w", pady=(6, 0))
    value_entry = tk.Entry(control, width=10)
    value_entry.grid(row=1, column=1, sticky="w", pady=(6, 0))

    mode_var = tk.StringVar(value="Auto")
    tk.Radiobutton(control, text="Auto BST", variable=mode_var, value="Auto").grid(row=1, column=2, sticky="w", pady=(6, 0))
    tk.Radiobutton(control, text="Manual", variable=mode_var, value="Manual").grid(row=1, column=3, sticky="w", pady=(6, 0))

    parent_var = tk.StringVar()
    parent_combo = ttk.Combobox(control, textvariable=parent_var, state="readonly", width=34)
    parent_combo.grid(row=2, column=0, columnspan=4, sticky="w", pady=(6, 0))
    side_var = tk.StringVar(value="L")
    ttk.Combobox(control, textvariable=side_var, values=["L", "R"], state="readonly", width=4).grid(row=2, column=4, sticky="w", pady=(6, 0))

    traversal_var = tk.StringVar(value="BFS")
    ttk.Combobox(control, textvariable=traversal_var, values=["BFS", "DFS", "BST Search"], state="readonly", width=14).grid(row=3, column=0, sticky="w", pady=(8, 0))
    search_entry = tk.Entry(control, width=12)
    search_entry.grid(row=3, column=1, sticky="w", pady=(8, 0))

    complexity = tk.Label(
        view,
        text="Complexity  -  Search: O(log n) avg, O(n) worst  |  Memory: O(n)  |  Insert: O(log n) avg",
        fg="#1a5276",
        bg="#eaf3fb",
        relief="flat",
        font=("Segoe UI", 9),
        anchor="w",
        padx=10,
        pady=3,
    )
    complexity.pack(fill="x", padx=8, pady=(0, 3))
    canvas = setup_scrollable_canvas(view)
    tk.Label(view, text="Wheel: zoom | Right-click + drag: pan | Left-click: details").pack(fill="x", padx=8, pady=(4, 2))
    add_depth_legend(view)
    details = tk.Label(view, text="Click a node for details.", anchor="w", justify="left")
    details.pack(fill="x", padx=8, pady=(0, 6))
    bind_canvas_interactions(canvas, details)

    parent_map: dict[str, int | None] = {}
    step_order: list[int] = []
    step_index = 0
    visited_path: list[int] = []
    search_target: str | None = None
    search_found = False
    next_button_ref: list[tk.Button | None] = [None]
    status_ref: list[tk.Label | None] = [None]

    def matches_search_value(node_value: str, target_value: str) -> bool:
        try:
            return float(node_value) == float(target_value)
        except (TypeError, ValueError):
            return str(node_value).strip() == str(target_value).strip()

    def refresh() -> None:
        nonlocal parent_map, step_order, step_index, visited_path, search_target, search_found
        state = collect_state(db_path, "studio")
        render_tree_canvas(canvas, state.bst_rows, "vrijednost", build_bst_layout)
        capture_frame(canvas)
        details.configure(text="Click a node for details.")

        options: list[tuple[str, int | None]] = []
        for row in state.bst_rows:
            left = "-" if row.get("lijevi_id") is None else str(row.get("lijevi_id"))
            right = "-" if row.get("desni_id") is None else str(row.get("desni_id"))
            options.append((f"{row['id']} | v={row['vrijednost']} | L:{left} R:{right}", int(row["id"])))
        parent_map = build_option_map(options)
        parent_combo.configure(values=[label for label, _ in options])
        parent_var.set(options[0][0] if options else "")

        step_order = []
        step_index = 0
        visited_path = []
        search_target = None
        search_found = False
        if next_button_ref[0]:
            next_button_ref[0].configure(state="normal")
        if status_ref[0]:
            status_ref[0].configure(text="")

    def animate_node_fall(node_id: int, path: list[int] | None = None) -> None:
        positions = getattr(canvas, "_pixel_positions", {})
        target = positions.get(node_id)
        if target is None:
            return

        waypoints: list[tuple[float, float]] = []
        if path:
            for path_node_id in path:
                pos = positions.get(int(path_node_id))
                if pos is not None:
                    waypoints.append((float(pos[0]), float(pos[1])))
        waypoints.append((float(target[0]), float(target[1])))

        item = canvas.create_oval(waypoints[0][0] - 20, 5, waypoints[0][0] + 20, 45, fill="#ffed9c", outline="#a85a00", width=2)
        waypoint_index = [0]

        def advance() -> None:
            if waypoint_index[0] >= len(waypoints):
                canvas.delete(item)
                highlight_node(canvas, node_id, "#d35400")
                capture_frame(canvas)
                return
            move_toward(*waypoints[waypoint_index[0]])

        def move_toward(dest_x: float, dest_y: float) -> None:
            coords = canvas.coords(item)
            if not coords:
                return
            center_x = (coords[0] + coords[2]) / 2.0
            center_y = (coords[1] + coords[3]) / 2.0
            delta_x, delta_y = dest_x - center_x, dest_y - center_y
            distance = (delta_x ** 2 + delta_y ** 2) ** 0.5
            if distance <= 8.0:
                canvas.move(item, delta_x, delta_y)
                if path and waypoint_index[0] < len(path):
                    mark_trail_node(canvas, int(path[waypoint_index[0]]))
                waypoint_index[0] += 1
                capture_frame(canvas)
                canvas.after(80, advance)
                return
            canvas.move(item, delta_x / distance * 8.0, delta_y / distance * 8.0)
            capture_frame(canvas)
            canvas.after(20, lambda: move_toward(dest_x, dest_y))

        advance()

    def do_insert() -> None:
        value = value_entry.get().strip()
        if not value:
            messagebox.showwarning("BST", "Enter a value.", parent=studio_parent)
            return
        try:
            if mode_var.get() == "Auto":
                result = insert_bst_node_auto(db_path, value)
                new_id = int(result["new_id"])
                insert_path = [int(item) for item in result.get("path", [])]
            else:
                selected_parent_id = parent_map.get(parent_var.get())
                if selected_parent_id is None:
                    raise ValueError("Select a parent node.")
                new_id = add_bst_node(db_path, value, int(selected_parent_id), side_var.get())
                insert_path = []
            refresh()
            animate_node_fall(new_id, insert_path or None)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("BST", f"Error: {exc}", parent=studio_parent)

    def prepare_steps() -> None:
        nonlocal step_order, step_index, visited_path, search_target, search_found
        state = collect_state(db_path, "studio")
        search_target = search_entry.get().strip() or None
        search_found = False
        if traversal_var.get() == "BST Search" and search_target is None:
            messagebox.showwarning("BST", "Enter a target value for BST Search.", parent=studio_parent)
            return
        step_order = build_bst_traversal_order(state.bst_rows, traversal_var.get(), search_target)
        step_index = 0
        visited_path = []
        if next_button_ref[0]:
            next_button_ref[0].configure(state="normal")
        if status_ref[0]:
            status_ref[0].configure(text="")
        if not step_order:
            messagebox.showwarning("BST", "No steps available for the selected mode.", parent=studio_parent)

    def next_step() -> None:
        nonlocal step_index, visited_path, search_found
        if search_found:
            if next_button_ref[0]:
                next_button_ref[0].configure(state="disabled")
            return
        if step_index >= len(step_order):
            if next_button_ref[0]:
                next_button_ref[0].configure(state="disabled")
            if status_ref[0]:
                if search_target is not None and not search_found:
                    status_ref[0].configure(text="-> Target node not found")
                else:
                    status_ref[0].configure(text="-> Completed")
            return

        node_id = int(step_order[step_index])
        if next_button_ref[0]:
            next_button_ref[0].configure(state="disabled")

        def finish_step() -> None:
            nonlocal step_index, visited_path, search_found
            found_now = False
            node_data = getattr(canvas, "_node_data", {})
            row = node_data.get(node_id)
            node_value = "" if row is None else str(row.get("vrijednost", ""))
            if search_target is not None and matches_search_value(node_value, search_target):
                found_now = True

            if traversal_var.get() == "BST Search":
                visited_path.append(node_id)
                highlight_search_path(canvas, visited_path[:-1], node_id)
            else:
                visited_path = []
                highlight_node(canvas, node_id)

            step_index += 1
            capture_frame(canvas)
            if next_button_ref[0]:
                if found_now:
                    search_found = True
                    step_index = len(step_order)
                    next_button_ref[0].configure(state="disabled")
                    if status_ref[0]:
                        status_ref[0].configure(text="-> Target node found")
                elif step_index >= len(step_order):
                    next_button_ref[0].configure(state="disabled")
                    if status_ref[0]:
                        status_ref[0].configure(text="-> Completed")
                else:
                    next_button_ref[0].configure(state="normal")

        animate_travel_roundtrip(canvas, node_id, lambda: capture_frame(canvas), finish_step)

    tk.Button(control, text="Insert node", command=do_insert).grid(row=1, column=5, padx=6, pady=(6, 0), sticky="w")
    tk.Button(control, text="Refresh tree", command=refresh).grid(row=1, column=6, padx=6, pady=(6, 0), sticky="w")
    tk.Button(control, text="Prepare steps", command=prepare_steps).grid(row=3, column=2, padx=6, pady=(8, 0), sticky="w")
    next_button_ref[0] = tk.Button(control, text="Next step", command=next_step)
    next_button_ref[0].grid(row=3, column=3, padx=6, pady=(8, 0), sticky="w")
    status_ref[0] = tk.Label(control, text="", fg="#c0392b", font=("Segoe UI", 9, "bold"))
    status_ref[0].grid(row=3, column=7, padx=6, pady=(8, 0), sticky="w")
    tk.Button(control, text="Export GIF", command=lambda: export_gif(studio_parent, frame_store)).grid(row=3, column=4, padx=6, pady=(8, 0), sticky="w")
    tk.Button(control, text="Export video", command=lambda: export_video(studio_parent, frame_store, imageio_module)).grid(row=3, column=5, padx=6, pady=(8, 0), sticky="w")
    tk.Button(control, text="Clear frames", command=lambda: clear_recorded_frames(studio_parent, frame_store, on_clear_frames)).grid(row=3, column=6, padx=6, pady=(8, 0), sticky="w")

    return view, refresh
