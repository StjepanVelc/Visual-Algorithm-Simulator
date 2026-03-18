"""Main GUI entry point and Visual Studio interface."""

import tkinter as tk
from collections import defaultdict
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from services.adt_service import (
    add_bst_node,
    add_general_tree_node,
    add_hash_node,
    add_recursion_call,
    build_database,
    collect_state,
    delete_bst_node,
    delete_general_tree_node,
    delete_hash_node,
    delete_recursion_call,
    export_sql,
    generate_report,
    import_sql,
    insert_bst_node_auto,
    update_bst_node_value,
    update_general_tree_node,
    update_hash_node,
    update_recursion_call,
)

# Import refactored UI components
from presentation.canvas.interactions import (
    animate_travel_roundtrip,
    bind_canvas_interactions,
    highlight_node,
    highlight_search_path,
    mark_trail_node,
)
from presentation.canvas.layouts import build_bst_layout, build_general_tree_layout
from presentation.canvas.renderers import normalize_frames_for_video, render_tree_canvas, setup_scrollable_canvas
from presentation.canvas.traversals import build_bst_traversal_order, build_general_traversal_order
from presentation.db_operations import on_build_db, on_export_sql, on_generate_report, on_import_sql
from presentation.forms.bst_form import open_bst_form, open_bst_manage_form
from presentation.forms.general_tree_form import open_general_tree_form, open_general_tree_manage_form
from presentation.forms.hash_form import open_hash_form, open_hash_manage_form
from presentation.forms.recursion_form import open_recursion_form, open_recursion_manage_form
from presentation.recording.capture import capture_canvas_frame
from presentation.utils import (
    DEPTH_COLORS,
    add_depth_legend,
    build_option_map,
    confirm_delete,
    ensure_db,
    extract_node_id_from_tags,
    format_node_details,
    parse_optional_int,
    resolve_paths,
)


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

    frame_store: list = []
    recording_var = tk.BooleanVar(value=False)
    frame_status_var = tk.StringVar(value="Frames: 0 | Recording: OFF")
    capture_error: list[str | None] = [None]

    def _update_frame_status() -> None:
        recording_state = "ON" if recording_var.get() else "OFF"
        text = f"Frames: {len(frame_store)} | Recording: {recording_state}"
        if capture_error[0]:
            text = f"{text} | {capture_error[0]}"
        frame_status_var.set(text)

    def _on_recording_toggle(*_: object) -> None:
        if not recording_var.get():
            capture_error[0] = None
        _update_frame_status()

    recording_var.trace_add("write", _on_recording_toggle)

    def capture_frame(canvas: tk.Canvas) -> None:
        captured = _capture_canvas_frame(canvas, frame_store, recording_var.get())
        if captured:
            capture_error[0] = None
        elif recording_var.get() and ImageGrab is None:
            capture_error[0] = "Pillow ImageGrab is not available"
        elif recording_var.get() and ImageGrab is not None:
            capture_error[0] = "Capture failed (keep the window visible on screen)"
        _update_frame_status()

    capture_panel = tk.LabelFrame(sidebar, text="Capture", bg="#eef3f8", padx=8, pady=6)
    capture_panel.pack(fill="x", padx=10, pady=(10, 6))
    tk.Checkbutton(capture_panel, text="Record frames", variable=recording_var, bg="#eef3f8").pack(anchor="w")
    tk.Label(capture_panel, text="For GIF/MP4 export", bg="#eef3f8", fg="#3f5163", font=("Segoe UI", 8)).pack(anchor="w")
    tk.Label(capture_panel, textvariable=frame_status_var, bg="#eef3f8", fg="#1f3a56", justify="left", wraplength=158).pack(anchor="w", pady=(4, 0))

    views: dict[str, tk.Frame] = {}
    current_view: list[str] = ["BST"]

    def show_view(name: str) -> None:
        for view in views.values():
            view.pack_forget()
        views[name].pack(fill="both", expand=True)
        current_view[0] = name

    # Hash view
    hash_view = tk.Frame(content)
    views["Hash"] = hash_view
    tk.Label(hash_view, text="Hash - bucket overview", font=("Segoe UI", 12, "bold")).pack(pady=(12, 6))
    hash_text = tk.Text(hash_view, height=25)
    hash_text.pack(fill="both", expand=True, padx=12, pady=8)

    def refresh_hash() -> None:
        state = collect_state(db_path, "studio")
        lines: list[str] = []
        grouped: dict[int, list[str]] = defaultdict(list)
        for row in state.hash_rows:
            bucket = int(row["bucket"])
            if row.get("cvor_id") is None:
                continue
            grouped[bucket].append(f"{row['cvor_id']}:{row['kljuc']}={row['vrijednost']}")

        for bucket in sorted({int(r["bucket"]) for r in state.hash_rows}):
            chain = " -> ".join(grouped.get(bucket, [])) if grouped.get(bucket) else "(empty)"
            lines.append(f"Bucket {bucket}: {chain}")

        hash_text.configure(state="normal")
        hash_text.delete("1.0", tk.END)
        hash_text.insert(tk.END, "\n".join(lines))
        hash_text.configure(state="disabled")

    tk.Button(hash_view, text="Refresh", command=refresh_hash).pack(pady=(0, 10))

    # BST view
    bst_view = tk.Frame(content)
    views["BST"] = bst_view
    control = tk.Frame(bst_view)
    control.pack(fill="x", padx=10, pady=8)

    tk.Label(control, text="BST Simulator", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=6, sticky="w")
    tk.Checkbutton(control, text="Record frames (global)", variable=recording_var).grid(row=0, column=6, sticky="w", padx=8)

    tk.Label(control, text="Value").grid(row=1, column=0, sticky="w", pady=(6, 0))
    bst_value_entry = tk.Entry(control, width=10)
    bst_value_entry.grid(row=1, column=1, sticky="w", pady=(6, 0))

    mode_var = tk.StringVar(value="Auto")
    tk.Radiobutton(control, text="Auto BST", variable=mode_var, value="Auto").grid(row=1, column=2, sticky="w", pady=(6, 0))
    tk.Radiobutton(control, text="Manual", variable=mode_var, value="Manual").grid(row=1, column=3, sticky="w", pady=(6, 0))

    parent_var = tk.StringVar()
    parent_combo = ttk.Combobox(control, textvariable=parent_var, state="readonly", width=34)
    parent_combo.grid(row=2, column=0, columnspan=4, sticky="w", pady=(6, 0))
    side_var = tk.StringVar(value="L")
    side_combo = ttk.Combobox(control, textvariable=side_var, values=["L", "R"], state="readonly", width=4)
    side_combo.grid(row=2, column=4, sticky="w", pady=(6, 0))

    traversal_var = tk.StringVar(value="BFS")
    traversal_combo = ttk.Combobox(control, textvariable=traversal_var, values=["BFS", "DFS", "BST Search"], state="readonly", width=14)
    traversal_combo.grid(row=3, column=0, sticky="w", pady=(8, 0))
    search_entry = tk.Entry(control, width=12)
    search_entry.grid(row=3, column=1, sticky="w", pady=(8, 0))

    bst_complexity = tk.Label(
        bst_view,
        text="Complexity  -  Search: O(log n) avg, O(n) worst  |  Memory: O(n)  |  Insert: O(log n) avg",
        fg="#1a5276", bg="#eaf3fb", relief="flat",
        font=("Segoe UI", 9), anchor="w", padx=10, pady=3,
    )
    bst_complexity.pack(fill="x", padx=8, pady=(0, 3))
    bst_canvas = setup_scrollable_canvas(bst_view)
    bst_hint = tk.Label(bst_view, text="Wheel: zoom | Right-click + drag: pan | Left-click: details")
    bst_hint.pack(fill="x", padx=8, pady=(4, 2))
    add_depth_legend(bst_view)
    bst_details = tk.Label(bst_view, text="Click a node for details.", anchor="w", justify="left")
    bst_details.pack(fill="x", padx=8, pady=(0, 6))
    bind_canvas_interactions(bst_canvas, bst_details)

    bst_parent_map: dict[str, int | None] = {}
    bst_step_order: list[int] = []
    bst_step_index = 0
    bst_visited_path: list[int] = []
    bst_search_target: str | None = None
    bst_search_found = False
    _bst_next_ref: list[tk.Button | None] = [None]
    _bst_status_ref: list[tk.Label | None] = [None]

    def _matches_search_value(node_value: str, target_value: str) -> bool:
        try:
            return float(node_value) == float(target_value)
        except (TypeError, ValueError):
            return str(node_value).strip() == str(target_value).strip()

    def refresh_bst_view() -> None:
        nonlocal bst_parent_map, bst_step_order, bst_step_index
        nonlocal bst_visited_path, bst_search_target, bst_search_found
        state = collect_state(db_path, "studio")
        render_tree_canvas(bst_canvas, state.bst_rows, "vrijednost", build_bst_layout)
        capture_frame(bst_canvas)
        bst_details.configure(text="Click a node for details.")

        options: list[tuple[str, int | None]] = []
        for row in state.bst_rows:
            left = "-" if row.get("lijevi_id") is None else str(row.get("lijevi_id"))
            right = "-" if row.get("desni_id") is None else str(row.get("desni_id"))
            options.append((f"{row['id']} | v={row['vrijednost']} | L:{left} R:{right}", int(row["id"])))
        bst_parent_map = _build_option_map(options)
        parent_combo.configure(values=[label for label, _ in options])
        if options:
            parent_var.set(options[0][0])
        else:
            parent_var.set("")

        bst_step_order = []
        bst_step_index = 0
        bst_visited_path = []
        bst_search_target = None
        bst_search_found = False
        if _bst_next_ref[0]:
            _bst_next_ref[0].configure(state="normal")
        if _bst_status_ref[0]:
            _bst_status_ref[0].configure(text="")

    def animate_node_fall(node_id: int, path: list[int] | None = None) -> None:
        positions = getattr(bst_canvas, "_pixel_positions", {})
        target = positions.get(node_id)
        if target is None:
            return

        waypoints: list[tuple[float, float]] = []
        if path:
            for pid in path:
                pos = positions.get(int(pid))
                if pos is not None:
                    waypoints.append((float(pos[0]), float(pos[1])))
        waypoints.append((float(target[0]), float(target[1])))

        start_x = waypoints[0][0]
        item = bst_canvas.create_oval(
            start_x - 20, 5, start_x + 20, 45, fill="#ffed9c", outline="#a85a00", width=2
        )
        wp_idx = [0]

        def advance() -> None:
            if wp_idx[0] >= len(waypoints):
                bst_canvas.delete(item)
                _highlight_node(bst_canvas, node_id, "#d35400")
                capture_frame(bst_canvas)
                return
            dest_x, dest_y = waypoints[wp_idx[0]]
            move_toward(dest_x, dest_y)

        def move_toward(dest_x: float, dest_y: float) -> None:
            coords = bst_canvas.coords(item)
            if not coords:
                return
            cx = (coords[0] + coords[2]) / 2.0
            cy = (coords[1] + coords[3]) / 2.0
            dx, dy = dest_x - cx, dest_y - cy
            dist = (dx ** 2 + dy ** 2) ** 0.5
            if dist <= 8.0:
                bst_canvas.move(item, dx, dy)
                if path and wp_idx[0] < len(path):
                    _mark_trail_node(bst_canvas, int(path[wp_idx[0]]))
                wp_idx[0] += 1
                capture_frame(bst_canvas)
                bst_canvas.after(80, advance)
            else:
                bst_canvas.move(item, dx / dist * 8.0, dy / dist * 8.0)
                capture_frame(bst_canvas)
                bst_canvas.after(20, lambda: move_toward(dest_x, dest_y))

        advance()

    def do_bst_insert() -> None:
        value = bst_value_entry.get().strip()
        if not value:
            messagebox.showwarning("BST", "Enter a value.", parent=win)
            return
        try:
            if mode_var.get() == "Auto":
                result = insert_bst_node_auto(db_path, value)
                new_id = int(result["new_id"])
                insert_path = [int(p) for p in result.get("path", [])]
            else:
                parent_id = bst_parent_map.get(parent_var.get())
                if parent_id is None:
                    raise ValueError("Select a parent node.")
                new_id = add_bst_node(db_path, value, int(parent_id), side_var.get())
                insert_path = []

            refresh_bst_view()
            animate_node_fall(new_id, insert_path or None)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("BST", f"Error: {exc}", parent=win)

    def prepare_bst_steps() -> None:
        nonlocal bst_step_order, bst_step_index, bst_visited_path
        nonlocal bst_search_target, bst_search_found
        state = collect_state(db_path, "studio")
        search_value = search_entry.get().strip()
        bst_search_target = search_value or None
        bst_search_found = False
        bst_step_order = _build_bst_traversal_order(
            state.bst_rows,
            traversal_var.get(),
            bst_search_target,
        )
        bst_step_index = 0
        bst_visited_path = []
        if _bst_next_ref[0]:
            _bst_next_ref[0].configure(state="normal")
        if _bst_status_ref[0]:
            _bst_status_ref[0].configure(text="")
        if traversal_var.get() == "BST Search" and bst_search_target is None:
            messagebox.showwarning("BST", "Enter a target value for BST Search.", parent=win)
            return
        if not bst_step_order:
            messagebox.showwarning("BST", "No steps available for the selected mode.", parent=win)

    def next_bst_step() -> None:
        nonlocal bst_step_index, bst_visited_path, bst_search_found
        if bst_search_found:
            if _bst_next_ref[0]:
                _bst_next_ref[0].configure(state="disabled")
            return
        if bst_step_index >= len(bst_step_order):
            if _bst_next_ref[0]:
                _bst_next_ref[0].configure(state="disabled")
            if _bst_status_ref[0]:
                if bst_search_target is not None and not bst_search_found:
                    _bst_status_ref[0].configure(text="-> Target node not found")
                else:
                    _bst_status_ref[0].configure(text="-> Completed")
            return
        node_id = int(bst_step_order[bst_step_index])

        if _bst_next_ref[0]:
            _bst_next_ref[0].configure(state="disabled")

        def _finish_step() -> None:
            nonlocal bst_step_index, bst_visited_path, bst_search_found
            found_now = False
            node_data = getattr(bst_canvas, "_node_data", {})
            row = node_data.get(node_id)
            node_value = "" if row is None else str(row.get("vrijednost", ""))

            if bst_search_target is not None and _matches_search_value(node_value, bst_search_target):
                found_now = True

            if traversal_var.get() == "BST Search":
                bst_visited_path.append(node_id)
                _highlight_search_path(bst_canvas, bst_visited_path[:-1], node_id)
            else:
                bst_visited_path = []
                _highlight_node(bst_canvas, node_id)

            bst_step_index += 1
            capture_frame(bst_canvas)

            if _bst_next_ref[0]:
                if found_now:
                    bst_search_found = True
                    bst_step_index = len(bst_step_order)
                    _bst_next_ref[0].configure(state="disabled")
                    if _bst_status_ref[0]:
                        _bst_status_ref[0].configure(text="-> Target node found")
                elif bst_step_index >= len(bst_step_order):
                    _bst_next_ref[0].configure(state="disabled")
                    if _bst_status_ref[0]:
                        _bst_status_ref[0].configure(text="-> Completed")
                else:
                    _bst_next_ref[0].configure(state="normal")

        _animate_travel_roundtrip(
            bst_canvas,
            node_id,
            lambda: capture_frame(bst_canvas),
            _finish_step,
        )

    def export_gif() -> None:
        if ImageGrab is None:
            messagebox.showwarning("Export", "Pillow is not available for GIF export.", parent=win)
            return
        if not frame_store:
            messagebox.showwarning("Export", "No recorded frames. Enable 'Record frames' and run a few steps.", parent=win)
            return
        out = filedialog.asksaveasfilename(defaultextension=".gif", filetypes=[("GIF", "*.gif")])
        if not out:
            return
        try:
            first = frame_store[0]
            first.save(out, save_all=True, append_images=frame_store[1:], duration=120, loop=0)
            messagebox.showinfo("Export", f"GIF saved: {out}", parent=win)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Export", f"GIF export failed: {exc}", parent=win)

    def export_video() -> None:
        if imageio is None:
            messagebox.showwarning("Export", "imageio is not available for video export.", parent=win)
            return
        if not frame_store:
            messagebox.showwarning("Export", "No recorded frames. Enable 'Record frames' and run a few steps.", parent=win)
            return
        out = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4", "*.mp4")])
        if not out:
            return
        try:
            frames = _normalize_frames_for_video(frame_store)
            imageio.imwrite(out, frames, fps=8)
            messagebox.showinfo("Export", f"Video saved: {out}", parent=win)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror(
                "Export",
                (
                    f"Video export failed: {exc}\n\n"
                    "Try installing backend:\n"
                    "pip install imageio-ffmpeg\n"
                    "or\n"
                    "pip install imageio[pyav]"
                ),
                parent=win,
            )

    def clear_frames() -> None:
        frame_store.clear()
        capture_error[0] = None
        _update_frame_status()
        messagebox.showinfo("Export", "Recorded frames were cleared.", parent=win)

    tk.Button(control, text="Insert node", command=do_bst_insert).grid(row=1, column=5, padx=6, pady=(6, 0), sticky="w")
    tk.Button(control, text="Refresh tree", command=refresh_bst_view).grid(row=1, column=6, padx=6, pady=(6, 0), sticky="w")
    tk.Button(control, text="Prepare steps", command=prepare_bst_steps).grid(row=3, column=2, padx=6, pady=(8, 0), sticky="w")
    _bst_next_ref[0] = tk.Button(control, text="Next step", command=next_bst_step)
    _bst_next_ref[0].grid(row=3, column=3, padx=6, pady=(8, 0), sticky="w")
    _bst_status_ref[0] = tk.Label(control, text="", fg="#c0392b", font=("Segoe UI", 9, "bold"))
    _bst_status_ref[0].grid(row=3, column=7, padx=6, pady=(8, 0), sticky="w")
    tk.Button(control, text="Export GIF", command=export_gif).grid(row=3, column=4, padx=6, pady=(8, 0), sticky="w")
    tk.Button(control, text="Export video", command=export_video).grid(row=3, column=5, padx=6, pady=(8, 0), sticky="w")
    tk.Button(control, text="Clear frames", command=clear_frames).grid(row=3, column=6, padx=6, pady=(8, 0), sticky="w")

    # Recursion view
    rec_view = tk.Frame(content)
    views["Recursion"] = rec_view
    tk.Label(rec_view, text="Recursion - stack animation", font=("Segoe UI", 12, "bold")).pack(pady=(10, 6))
    rec_canvas = tk.Canvas(rec_view, bg="#f7fafc")
    rec_canvas.pack(fill="both", expand=True, padx=12, pady=8)

    rec_order: list[int] = []
    rec_rows: dict[int, dict] = {}
    rec_step = 0
    _rec_next_ref: list[tk.Button | None] = [None]
    _rec_status_ref: list[tk.Label | None] = [None]

    def _build_rec_order() -> tuple[list[int], dict[int, dict]]:
        state = collect_state(db_path, "studio")
        rows = {int(row["id"]): row for row in state.recursion_rows}
        children: dict[int, list[int]] = defaultdict(list)
        roots: list[int] = []
        for row in state.recursion_rows:
            node_id = int(row["id"])
            parent_id = row.get("parent_id")
            if parent_id is None:
                roots.append(node_id)
            else:
                children[int(parent_id)].append(node_id)
        for parent_id in children:
            children[parent_id].sort()
        roots.sort()

        order: list[int] = []

        def dfs(node_id: int) -> None:
            order.append(node_id)
            for child_id in children.get(node_id, []):
                dfs(child_id)

        for root_id in roots:
            dfs(root_id)
        return order, rows

    def draw_rec_stack(current_id: int | None) -> None:
        rec_canvas.delete("all")
        if current_id is None:
            rec_canvas.create_text(20, 20, anchor="nw", text="Click Next step to grow the stack.")
            return

        # build path to root
        stack_ids: list[int] = []
        node_id = current_id
        while node_id is not None:
            stack_ids.append(node_id)
            parent_id = rec_rows.get(node_id, {}).get("parent_id")
            node_id = int(parent_id) if parent_id is not None else None
        stack_ids.reverse()

        y = 20
        for node in stack_ids:
            row = rec_rows[node]
            is_active = node == current_id
            ret = row.get("povrat", "") or ""
            ret_suffix = "" if is_active or not ret else f"  -> return: {ret}"
            marker = "> " if is_active else "  "
            text = f"{marker}{row['oznaka']} | {row['funkcija']}({row['argument']}){ret_suffix}"
            fill = "#dff7e3" if is_active else "#dce8f5"
            outline_col = "#2d6a4f" if is_active else "#2471a3"
            lw = 3 if is_active else 1
            bold = "bold" if is_active else "normal"
            rec_canvas.create_rectangle(30, y, 520, y + 42, fill=fill, outline=outline_col, width=lw)
            rec_canvas.create_text(42, y + 21, text=text, anchor="w", font=("Segoe UI", 10, bold))
            y += 52

    def reset_rec() -> None:
        nonlocal rec_order, rec_rows, rec_step
        rec_order, rec_rows = _build_rec_order()
        rec_step = 0
        if _rec_next_ref[0]:
            _rec_next_ref[0].configure(state="normal")
        if _rec_status_ref[0]:
            _rec_status_ref[0].configure(text="")
        draw_rec_stack(None)

    def next_rec_step() -> None:
        nonlocal rec_step
        if rec_step >= len(rec_order):
            if _rec_next_ref[0]:
                _rec_next_ref[0].configure(state="disabled")
            if _rec_status_ref[0]:
                _rec_status_ref[0].configure(text="-> Completed")
            return
        draw_rec_stack(rec_order[rec_step])
        rec_step += 1
        capture_frame(rec_canvas)

    rec_btns = tk.Frame(rec_view)
    rec_btns.pack(fill="x", padx=12, pady=(0, 8))
    tk.Button(rec_btns, text="Reset", command=reset_rec).pack(side="left", padx=4)
    _rec_next_ref[0] = tk.Button(rec_btns, text="Next step", command=next_rec_step)
    _rec_next_ref[0].pack(side="left", padx=4)
    _rec_status_ref[0] = tk.Label(rec_btns, text="", fg="#c0392b", font=("Segoe UI", 9, "bold"))
    _rec_status_ref[0].pack(side="left", padx=8)

    # General tree view
    gen_view = tk.Frame(content)
    views["General Tree"] = gen_view
    gen_ctrl = tk.Frame(gen_view)
    gen_ctrl.pack(fill="x", padx=10, pady=8)
    tk.Label(gen_ctrl, text="General Tree - step mode", font=("Segoe UI", 12, "bold")).pack(side="left")

    gen_mode_var = tk.StringVar(value="BFS")
    ttk.Combobox(gen_ctrl, textvariable=gen_mode_var, values=["BFS", "DFS"], state="readonly", width=8).pack(side="left", padx=8)
    gen_canvas = _setup_scrollable_canvas(gen_view)
    gen_details = tk.Label(gen_view, text="Click a node for details.", anchor="w")
    gen_details.pack(fill="x", padx=8, pady=(2, 8))
    bind_canvas_interactions(gen_canvas, gen_details)

    gen_order: list[int] = []
    gen_index = 0
    _gen_next_ref: list[tk.Button | None] = [None]
    _gen_status_ref: list[tk.Label | None] = [None]

    def refresh_gen() -> None:
        nonlocal gen_order, gen_index
        state = collect_state(db_path, "studio")
        _render_tree_canvas(gen_canvas, state.opce_rows, "vrijednost", _build_general_tree_layout)
        capture_frame(gen_canvas)
        gen_order = []
        gen_index = 0

    def prepare_gen_steps() -> None:
        nonlocal gen_order, gen_index
        state = collect_state(db_path, "studio")
        gen_order = _build_general_traversal_order(state.opce_rows, gen_mode_var.get())
        gen_index = 0
        if _gen_next_ref[0]:
            _gen_next_ref[0].configure(state="normal")
        if _gen_status_ref[0]:
            _gen_status_ref[0].configure(text="")

    def next_gen_step() -> None:
        nonlocal gen_index
        if gen_index >= len(gen_order):
            if _gen_next_ref[0]:
                _gen_next_ref[0].configure(state="disabled")
            if _gen_status_ref[0]:
                _gen_status_ref[0].configure(text="-> Completed")
            return

        node_id = int(gen_order[gen_index])
        if _gen_next_ref[0]:
            _gen_next_ref[0].configure(state="disabled")

        def _finish_step() -> None:
            nonlocal gen_index
            _highlight_node(gen_canvas, node_id)
            gen_index += 1
            capture_frame(gen_canvas)
            if _gen_next_ref[0]:
                if gen_index >= len(gen_order):
                    _gen_next_ref[0].configure(state="disabled")
                    if _gen_status_ref[0]:
                        _gen_status_ref[0].configure(text="-> Completed")
                else:
                    _gen_next_ref[0].configure(state="normal")

        _animate_travel_roundtrip(
            gen_canvas,
            node_id,
            lambda: capture_frame(gen_canvas),
            _finish_step,
        )

    gen_btns = tk.Frame(gen_view)
    gen_btns.pack(fill="x", padx=12, pady=(0, 8))
    tk.Button(gen_btns, text="Refresh", command=refresh_gen).pack(side="left", padx=4)
    tk.Button(gen_btns, text="Prepare steps", command=prepare_gen_steps).pack(side="left", padx=4)
    _gen_next_ref[0] = tk.Button(gen_btns, text="Next step", command=next_gen_step)
    _gen_next_ref[0].pack(side="left", padx=4)
    _gen_status_ref[0] = tk.Label(gen_btns, text="", fg="#c0392b", font=("Segoe UI", 9, "bold"))
    _gen_status_ref[0].pack(side="left", padx=8)

    navigation_panel = tk.LabelFrame(sidebar, text="Views", bg="#eef3f8", padx=8, pady=6)
    navigation_panel.pack(fill="x", padx=10, pady=(6, 6))
    for name in ["Hash", "BST", "Recursion", "General Tree"]:
        tk.Button(navigation_panel, text=f"[{name}]", anchor="w", width=16, command=lambda n=name: show_view(n)).pack(pady=3)

    crud_panel = tk.LabelFrame(sidebar, text="CRUD", bg="#eef3f8", padx=8, pady=6)
    crud_panel.pack(fill="x", padx=10, pady=(6, 10))
    tk.Button(crud_panel, text="Hash: Add", anchor="w", width=16, command=lambda: open_hash_form(win)).pack(pady=2)
    tk.Button(crud_panel, text="Hash: Edit/Delete", anchor="w", width=16, command=lambda: open_hash_manage_form(win)).pack(pady=2)
    tk.Button(crud_panel, text="Recursion: Add", anchor="w", width=16, command=lambda: open_recursion_form(win)).pack(pady=2)
    tk.Button(crud_panel, text="Recursion: Edit/Delete", anchor="w", width=16, command=lambda: open_recursion_manage_form(win)).pack(pady=2)
    tk.Button(crud_panel, text="Tree: Add", anchor="w", width=16, command=lambda: open_general_tree_form(win)).pack(pady=2)
    tk.Button(crud_panel, text="Tree: Edit/Delete", anchor="w", width=16, command=lambda: open_general_tree_manage_form(win)).pack(pady=2)
    tk.Button(crud_panel, text="BST: Add", anchor="w", width=16, command=lambda: open_bst_form(win)).pack(pady=2)
    tk.Button(crud_panel, text="BST: Edit/Delete", anchor="w", width=16, command=lambda: open_bst_manage_form(win)).pack(pady=2)

    def refresh_current_view() -> None:
        match current_view[0]:
            case "Hash":
                refresh_hash()
            case "BST":
                refresh_bst_view()
            case "Recursion":
                reset_rec()
            case "General Tree":
                refresh_gen()

    tk.Button(crud_panel, text="Refresh Active View", anchor="w", width=16, command=refresh_current_view).pack(pady=(6, 2))

    refresh_hash()
    refresh_bst_view()
    reset_rec()
    refresh_gen()
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
