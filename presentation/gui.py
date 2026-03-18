import importlib
import tkinter as tk
from collections import defaultdict
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

try:
    ImageGrab = importlib.import_module("PIL.ImageGrab")
except Exception:  # noqa: BLE001
    ImageGrab = None

try:
    imageio = importlib.import_module("imageio.v3")
except Exception:  # noqa: BLE001
    imageio = None

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

DEPTH_COLORS = [
    "#d9eefc",
    "#dff7e3",
    "#fff1d6",
    "#fde0e0",
    "#e9e2ff",
    "#ffe7f5",
]


def _add_depth_legend(parent: tk.Widget) -> None:
    legend = tk.Frame(parent)
    legend.pack(fill="x", padx=8, pady=(0, 6))

    tk.Label(legend, text="Depth legend:", anchor="w").pack(side="left", padx=(0, 8))
    for depth, color in enumerate(DEPTH_COLORS):
        item = tk.Frame(legend)
        item.pack(side="left", padx=4)
        swatch = tk.Canvas(item, width=14, height=14, highlightthickness=1, highlightbackground="#6f7d8a")
        swatch.create_rectangle(0, 0, 14, 14, fill=color, outline=color)
        swatch.pack(side="left")
        tk.Label(item, text=f"D{depth}").pack(side="left", padx=(3, 0))


def resolve_paths() -> tuple[Path, Path]:
    base_dir = Path(__file__).resolve().parent.parent
    db_path = base_dir / "adt.db"
    report_dir = base_dir / "izvjestaji"
    return db_path, report_dir


def ensure_db() -> Path | None:
    db_path, _ = resolve_paths()
    if not db_path.exists():
        messagebox.showwarning("ADT", "Database does not exist. Create it first.")
        return None
    return db_path


def parse_optional_int(value: str) -> int | None:
    text = value.strip()
    if not text:
        return None
    return int(text)


def _build_option_map(options: list[tuple[str, int | None]]) -> dict[str, int | None]:
    return {label: value for label, value in options}


def _build_general_tree_layout(rows: list[dict]) -> tuple[dict[int, tuple[float, int]], list[tuple[int, int]]]:
    if not rows:
        return {}, []

    nodes = {row["id"]: row for row in rows}
    children: dict[int, list[int]] = defaultdict(list)
    roots: list[int] = []
    edges: list[tuple[int, int]] = []

    for row in rows:
        parent_id = row["parent_id"]
        node_id = row["id"]
        if parent_id is None:
            roots.append(node_id)
        else:
            children[parent_id].append(node_id)
            edges.append((parent_id, node_id))

    def sort_key(node_id: int) -> tuple[int, int]:
        redoslijed = nodes[node_id].get("redoslijed")
        return (redoslijed if redoslijed is not None else 0, node_id)

    for parent_id in children:
        children[parent_id].sort(key=sort_key)
    roots.sort(key=sort_key)

    positions: dict[int, tuple[float, int]] = {}
    next_x = [0]

    def dfs(node_id: int, depth: int) -> float:
        child_ids = children.get(node_id, [])
        if not child_ids:
            x = float(next_x[0])
            next_x[0] += 1
            positions[node_id] = (x, depth)
            return x

        child_x = [dfs(child_id, depth + 1) for child_id in child_ids]
        x = sum(child_x) / len(child_x)
        positions[node_id] = (x, depth)
        return x

    for root_id in roots:
        dfs(root_id, 0)

    return positions, edges


def _build_bst_layout(rows: list[dict]) -> tuple[dict[int, tuple[float, int]], list[tuple[int, int]]]:
    if not rows:
        return {}, []

    nodes = {row["id"]: row for row in rows}
    root_id = next((row["id"] for row in rows if row["parent_id"] is None), None)
    if root_id is None:
        return {}, []

    positions: dict[int, tuple[float, int]] = {}
    edges: list[tuple[int, int]] = []
    next_x = [0]

    def dfs(node_id: int, depth: int) -> float:
        node = nodes[node_id]
        child_x: list[float] = []
        left_id = node.get("lijevi_id")
        right_id = node.get("desni_id")

        if left_id is not None and left_id in nodes:
            edges.append((node_id, left_id))
            child_x.append(dfs(left_id, depth + 1))

        if right_id is not None and right_id in nodes:
            edges.append((node_id, right_id))
            child_x.append(dfs(right_id, depth + 1))

        if child_x:
            x = sum(child_x) / len(child_x)
        else:
            x = float(next_x[0])
            next_x[0] += 1

        positions[node_id] = (x, depth)
        return x

    dfs(root_id, 0)
    return positions, edges


def _render_tree_canvas(
    canvas: tk.Canvas,
    rows: list[dict],
    value_key: str,
    layout_builder,
) -> None:
    canvas.delete("all")
    if not rows:
        canvas.create_text(30, 30, anchor="nw", text="(no data)", font=("Segoe UI", 11))
        canvas.configure(scrollregion=(0, 0, 400, 120))
        return

    positions, edges = layout_builder(rows)
    if not positions:
        canvas.create_text(30, 30, anchor="nw", text="(no data)", font=("Segoe UI", 11))
        canvas.configure(scrollregion=(0, 0, 400, 120))
        return

    nodes = {row["id"]: row for row in rows}
    margin_x = 60
    margin_y = 50
    x_gap = 110
    y_gap = 95
    radius = 24

    pixel_positions: dict[int, tuple[float, float]] = {}
    for node_id, (x_level, depth) in positions.items():
        pixel_positions[node_id] = (margin_x + x_level * x_gap, margin_y + depth * y_gap)

    for parent_id, child_id in edges:
        parent_pos = pixel_positions.get(parent_id)
        child_pos = pixel_positions.get(child_id)
        if parent_pos and child_pos:
            canvas.create_line(
                parent_pos[0],
                parent_pos[1] + radius,
                child_pos[0],
                child_pos[1] - radius,
                fill="#5a6b7d",
                width=2,
            )

    node_ovals: dict[int, int] = {}
    parent_map: dict[int, int | None] = {}

    for node_id, (x, y) in pixel_positions.items():
        node = nodes[node_id]
        depth = int(positions[node_id][1])
        label = str(node.get(value_key, ""))
        text_label = label if len(label) <= 8 else f"{label[:8]}..."
        fill_color = DEPTH_COLORS[depth % len(DEPTH_COLORS)]
        node_tag = f"node_{node_id}"

        oval_id = canvas.create_oval(
            x - radius,
            y - radius,
            x + radius,
            y + radius,
            fill=fill_color,
            outline="#2c5d82",
            width=2,
            tags=("node", node_tag),
        )
        node_ovals[int(node_id)] = int(oval_id)
        parent_id = node.get("parent_id")
        parent_map[int(node_id)] = int(parent_id) if parent_id is not None else None
        canvas.create_text(
            x,
            y,
            text=text_label,
            font=("Segoe UI", 10, "bold"),
            fill="#173b57",
            tags=("node", node_tag),
        )
        canvas.create_text(
            x,
            y + radius + 12,
            text=f"ID:{node_id}",
            font=("Segoe UI", 8),
            fill="#4f5f6e",
            tags=("node", node_tag),
        )

    canvas._node_data = nodes  # type: ignore[attr-defined]
    canvas._node_ovals = node_ovals  # type: ignore[attr-defined]
    canvas._pixel_positions = pixel_positions  # type: ignore[attr-defined]
    canvas._parent_map = parent_map  # type: ignore[attr-defined]
    canvas._tree_zoom = 1.0  # type: ignore[attr-defined]

    max_x = max(pos[0] for pos in pixel_positions.values())
    max_y = max(pos[1] for pos in pixel_positions.values())
    canvas.configure(scrollregion=(0, 0, max_x + 120, max_y + 100))


def _setup_scrollable_canvas(parent: tk.Widget) -> tk.Canvas:
    wrapper = tk.Frame(parent)
    wrapper.pack(fill="both", expand=True)

    canvas = tk.Canvas(wrapper, bg="#f8fbff")
    x_scroll = tk.Scrollbar(wrapper, orient="horizontal", command=canvas.xview)
    y_scroll = tk.Scrollbar(wrapper, orient="vertical", command=canvas.yview)
    canvas.configure(xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)

    canvas.grid(row=0, column=0, sticky="nsew")
    y_scroll.grid(row=0, column=1, sticky="ns")
    x_scroll.grid(row=1, column=0, sticky="ew")

    wrapper.rowconfigure(0, weight=1)
    wrapper.columnconfigure(0, weight=1)
    return canvas


def _extract_node_id_from_tags(tags: tuple[str, ...]) -> int | None:
    for tag in tags:
        if tag.startswith("node_"):
            try:
                return int(tag.removeprefix("node_"))
            except ValueError:
                return None
    return None


def _format_node_details(row: dict) -> str:
    ordered = [f"{key}={row[key]}" for key in row.keys()]
    return " | ".join(ordered)


def _confirm_delete(parent: tk.Misc, title: str, description: str) -> bool:
    return messagebox.askyesno(
        "Delete confirmation",
        f"{title}\n\n{description}\n\nAre you sure you want to delete this node?",
        parent=parent,
        icon="warning",
    )


def _build_bst_traversal_order(rows: list[dict], mode: str, search_value: str | None = None) -> list[int]:
    nodes = {int(row["id"]): row for row in rows}
    root_id = next((int(row["id"]) for row in rows if row.get("parent_id") is None), None)
    if root_id is None:
        return []

    if mode == "BFS":
        order: list[int] = []
        queue = [root_id]
        while queue:
            node_id = queue.pop(0)
            order.append(node_id)
            node = nodes[node_id]
            if node.get("lijevi_id") is not None and int(node["lijevi_id"]) in nodes:
                queue.append(int(node["lijevi_id"]))
            if node.get("desni_id") is not None and int(node["desni_id"]) in nodes:
                queue.append(int(node["desni_id"]))
        return order

    if mode == "DFS":
        order = []

        def dfs(node_id: int) -> None:
            order.append(node_id)
            node = nodes[node_id]
            if node.get("lijevi_id") is not None and int(node["lijevi_id"]) in nodes:
                dfs(int(node["lijevi_id"]))
            if node.get("desni_id") is not None and int(node["desni_id"]) in nodes:
                dfs(int(node["desni_id"]))

        dfs(root_id)
        return order

    if mode == "BST Search" and search_value is not None:
        def cmp_key(value: str) -> tuple[int, float | str]:
            try:
                return (0, float(value))
            except (TypeError, ValueError):
                return (1, str(value))

        target = cmp_key(search_value)
        order = []
        current = root_id
        while True:
            node = nodes.get(current)
            if node is None:
                break
            order.append(current)
            node_key = cmp_key(str(node.get("vrijednost", "")))
            if node_key == target:
                break
            if target < node_key:
                left = node.get("lijevi_id")
                if left is None:
                    break
                current = int(left)
            else:
                right = node.get("desni_id")
                if right is None:
                    break
                current = int(right)
        return order

    return []


def _build_general_traversal_order(rows: list[dict], mode: str) -> list[int]:
    nodes = {int(row["id"]): row for row in rows}
    children: dict[int, list[int]] = defaultdict(list)
    roots: list[int] = []

    for row in rows:
        node_id = int(row["id"])
        parent_id = row.get("parent_id")
        if parent_id is None:
            roots.append(node_id)
        else:
            children[int(parent_id)].append(node_id)

    def sort_key(node_id: int) -> tuple[int, int]:
        red = nodes[node_id].get("redoslijed")
        return (int(red) if red is not None else 0, node_id)

    roots.sort(key=sort_key)
    for parent_id in children:
        children[parent_id].sort(key=sort_key)

    if mode == "BFS":
        order: list[int] = []
        queue = roots[:]
        while queue:
            node_id = queue.pop(0)
            order.append(node_id)
            queue.extend(children.get(node_id, []))
        return order

    if mode == "DFS":
        order: list[int] = []

        def dfs(node_id: int) -> None:
            order.append(node_id)
            for child_id in children.get(node_id, []):
                dfs(child_id)

        for root_id in roots:
            dfs(root_id)
        return order

    return []


def _highlight_node(canvas: tk.Canvas, node_id: int, color: str = "#f39c12") -> None:
    oval_item_ids = getattr(canvas, "_node_ovals", {})
    for oval_id in oval_item_ids.values():
        canvas.itemconfigure(oval_id, width=2, outline="#2c5d82")

    target = oval_item_ids.get(node_id)
    if target is not None:
        canvas.itemconfigure(target, width=4, outline=color)


def _mark_trail_node(canvas: tk.Canvas, node_id: int, color: str = "#f0a500") -> None:
    """Mark a waypoint node during insert-path animation (light trail)."""
    oval_item_ids = getattr(canvas, "_node_ovals", {})
    target = oval_item_ids.get(node_id)
    if target is not None:
        canvas.itemconfigure(target, width=3, outline=color)


def _highlight_search_path(canvas: tk.Canvas, visited_ids: list[int], current_id: int) -> None:
    """Show the full BST-search path: trail nodes in amber, active node in red-orange."""
    oval_item_ids = getattr(canvas, "_node_ovals", {})
    for oval_id in oval_item_ids.values():
        canvas.itemconfigure(oval_id, width=2, outline="#2c5d82")
    for nid in visited_ids:
        oval = oval_item_ids.get(nid)
        if oval is not None:
            canvas.itemconfigure(oval, width=3, outline="#f0a500")
    active = oval_item_ids.get(current_id)
    if active is not None:
        canvas.itemconfigure(active, width=4, outline="#d35400")


def _animate_travel_roundtrip(
    canvas: tk.Canvas,
    node_id: int,
    capture_frame_cb,
    on_done,
) -> None:
    positions = getattr(canvas, "_pixel_positions", {})
    parent_map = getattr(canvas, "_parent_map", {})
    if node_id not in positions:
        on_done()
        return

    path_to_root: list[int] = []
    current = int(node_id)
    seen: set[int] = set()
    while current in positions and current not in seen:
        seen.add(current)
        path_to_root.append(current)
        parent_id = parent_map.get(current)
        if parent_id is None:
            break
        current = int(parent_id)

    if not path_to_root:
        on_done()
        return

    path_to_node = list(reversed(path_to_root))
    visit_path = path_to_node + path_to_node[-2::-1]
    waypoints = [positions[nid] for nid in visit_path if nid in positions]
    if not waypoints:
        on_done()
        return

    start_x, start_y = float(waypoints[0][0]), float(waypoints[0][1])
    marker = canvas.create_oval(
        start_x - 10,
        start_y - 10,
        start_x + 10,
        start_y + 10,
        fill="#ffe082",
        outline="#a85a00",
        width=2,
    )

    target_idx = [1]

    def finish() -> None:
        canvas.delete(marker)
        on_done()

    def move_toward(dest_x: float, dest_y: float) -> None:
        coords = canvas.coords(marker)
        if not coords:
            finish()
            return
        cx = (coords[0] + coords[2]) / 2.0
        cy = (coords[1] + coords[3]) / 2.0
        dx = dest_x - cx
        dy = dest_y - cy
        dist = (dx ** 2 + dy ** 2) ** 0.5

        if dist <= 6.0:
            canvas.move(marker, dx, dy)
            capture_frame_cb()
            if target_idx[0] >= len(waypoints):
                finish()
                return
            next_x, next_y = waypoints[target_idx[0]]
            target_idx[0] += 1
            canvas.after(70, lambda: move_toward(float(next_x), float(next_y)))
            return

        step = 6.0
        canvas.move(marker, dx / dist * step, dy / dist * step)
        capture_frame_cb()
        canvas.after(20, lambda: move_toward(dest_x, dest_y))

    if len(waypoints) == 1:
        capture_frame_cb()
        finish()
        return

    first_dest = waypoints[target_idx[0]]
    target_idx[0] += 1
    move_toward(float(first_dest[0]), float(first_dest[1]))


def _capture_canvas_frame(canvas: tk.Canvas, frame_store: list, recording_enabled: bool) -> bool:
    if not recording_enabled or ImageGrab is None:
        return False
    try:
        canvas.update()
        x0 = canvas.winfo_rootx()
        y0 = canvas.winfo_rooty()
        x1 = x0 + canvas.winfo_width()
        y1 = y0 + canvas.winfo_height()
        if x1 <= x0 or y1 <= y0:
            return False
        frame_store.append(ImageGrab.grab(bbox=(x0, y0, x1, y1)).convert("RGB"))
        return True
    except Exception:  # noqa: BLE001
        return False


def _normalize_frames_for_video(frames: list) -> list:
    if not frames:
        return frames
    base_w, base_h = frames[0].size
    normalized = [frames[0].convert("RGB")]
    for frame in frames[1:]:
        rgb = frame.convert("RGB")
        if rgb.size != (base_w, base_h):
            rgb = rgb.resize((base_w, base_h))
        normalized.append(rgb)
    return normalized


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
    bst_canvas = _setup_scrollable_canvas(bst_view)
    bst_hint = tk.Label(bst_view, text="Wheel: zoom | Right-click + drag: pan | Left-click: details")
    bst_hint.pack(fill="x", padx=8, pady=(4, 2))
    _add_depth_legend(bst_view)
    bst_details = tk.Label(bst_view, text="Click a node for details.", anchor="w", justify="left")
    bst_details.pack(fill="x", padx=8, pady=(0, 6))
    _bind_canvas_interactions(bst_canvas, bst_details)

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
        _render_tree_canvas(bst_canvas, state.bst_rows, "vrijednost", _build_bst_layout)
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
    _bind_canvas_interactions(gen_canvas, gen_details)

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


def _bind_canvas_interactions(canvas: tk.Canvas, details_label: tk.Label) -> None:
    def start_pan(event: tk.Event) -> None:
        canvas.scan_mark(event.x, event.y)

    def drag_pan(event: tk.Event) -> None:
        canvas.scan_dragto(event.x, event.y, gain=1)

    def zoom(event: tk.Event) -> None:
        delta = getattr(event, "delta", 0)
        factor = 1.1 if delta > 0 else 0.9
        current_zoom = float(getattr(canvas, "_tree_zoom", 1.0))
        new_zoom = current_zoom * factor
        if new_zoom < 0.4 or new_zoom > 2.8:
            return

        canvas.scale("all", canvas.canvasx(event.x), canvas.canvasy(event.y), factor, factor)
        canvas._tree_zoom = new_zoom  # type: ignore[attr-defined]
        bbox = canvas.bbox("all")
        if bbox:
            canvas.configure(scrollregion=(bbox[0] - 40, bbox[1] - 40, bbox[2] + 40, bbox[3] + 40))

    def show_node_details(event: tk.Event) -> None:
        item_ids = canvas.find_withtag("current")
        if not item_ids:
            details_label.configure(text="Click a node for details.")
            return

        tags = canvas.gettags(item_ids[0])
        node_id = _extract_node_id_from_tags(tags)
        if node_id is None:
            details_label.configure(text="Click a node for details.")
            return

        node_data = getattr(canvas, "_node_data", {})
        row = node_data.get(node_id)
        if row is None:
            details_label.configure(text="Click a node for details.")
            return

        details_label.configure(text=_format_node_details(row))

    canvas.bind("<ButtonPress-3>", start_pan)
    canvas.bind("<B3-Motion>", drag_pan)
    canvas.bind("<MouseWheel>", zoom)
    canvas.bind("<Button-1>", show_node_details)


def on_build_db() -> None:
    db_path, _ = resolve_paths()
    build_database(db_path)
    messagebox.showinfo("ADT", f"Database created: {db_path}")


def on_generate_report() -> None:
    db_path, report_dir = resolve_paths()
    if not db_path.exists():
        messagebox.showwarning("ADT", "Database does not exist. Create it first.")
        return

    report_path = generate_report(db_path, report_dir)
    messagebox.showinfo("ADT", f"HTML report for current state: {report_path}")


def on_export_sql() -> None:
    db_path = ensure_db()
    if not db_path:
        return

    sql_path = filedialog.asksaveasfilename(
        title="Save SQL",
        defaultextension=".sql",
        filetypes=[("SQL", "*.sql")],
    )
    if not sql_path:
        return

    export_sql(db_path, Path(sql_path))
    messagebox.showinfo("ADT", f"SQL saved: {sql_path}")


def on_import_sql() -> None:
    db_path, _ = resolve_paths()
    sql_path = filedialog.askopenfilename(
        title="Load SQL",
        filetypes=[("SQL", "*.sql")],
    )
    if not sql_path:
        return

    import_sql(db_path, Path(sql_path), replace=True)
    messagebox.showinfo("ADT", f"SQL loaded into database: {db_path}")


def open_hash_form(parent: tk.Tk | tk.Toplevel) -> None:
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

    option_map = _build_option_map(options)

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
            if not _confirm_delete(win, "Delete hash node", description):
                return

            delete_hash_node(db_path, int(node_id))
            messagebox.showinfo("ADT", "Hash node deleted.")
            win.destroy()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("ADT", f"Error: {exc}")

    tk.Button(win, text="Edit", command=do_update).pack(pady=(12, 4))
    tk.Button(win, text="Delete", command=do_delete).pack(pady=4)


def open_recursion_form(parent: tk.Tk | tk.Toplevel) -> None:
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
    parent_map = _build_option_map(parent_options)

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

    call_map = _build_option_map(call_options)

    child_parent_ids = {int(row["parent_id"]) for row in state.recursion_rows if row.get("parent_id") is not None}
    safe_delete_options = [(label, value) for label, value in call_options if value not in child_parent_ids]

    parent_options: list[tuple[str, int | None]] = [("(no parent)", None)]
    for row in state.recursion_rows:
        parent_options.append((f"{row['id']} | {row['oznaka']}", int(row["id"])))
    parent_map = _build_option_map(parent_options)

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
            if not _confirm_delete(win, "Delete recursive call", description):
                return

            delete_recursion_call(db_path, int(call_id))
            messagebox.showinfo("ADT", "Recursive call deleted.")
            win.destroy()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("ADT", f"Error: {exc}")

    tk.Button(win, text="Edit", command=do_update).pack(pady=(12, 4))
    tk.Button(win, text="Delete", command=do_delete).pack(pady=4)


def open_general_tree_form(parent: tk.Tk | tk.Toplevel) -> None:
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
    parent_map = _build_option_map(parent_options)

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

    node_map = _build_option_map(node_options)

    child_parent_ids = {int(row["parent_id"]) for row in state.opce_rows if row.get("parent_id") is not None}
    safe_delete_options = [(label, value) for label, value in node_options if value not in child_parent_ids]

    parent_options: list[tuple[str, int | None]] = [("(root node)", None)]
    for row in state.opce_rows:
        parent_options.append((f"{row['id']} | {row['vrijednost']}", int(row["id"])))
    parent_map = _build_option_map(parent_options)

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
            if not _confirm_delete(win, "Delete general-tree node", description):
                return

            delete_general_tree_node(db_path, int(node_id))
            messagebox.showinfo("ADT", "General-tree node deleted.")
            win.destroy()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("ADT", f"Error: {exc}")

    tk.Button(win, text="Edit", command=do_update).pack(pady=(12, 4))
    tk.Button(win, text="Delete", command=do_delete).pack(pady=4)


def open_bst_form(parent: tk.Tk | tk.Toplevel) -> None:
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

    parent_map = _build_option_map(parent_options)

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

    node_map = _build_option_map(node_options)

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
            if not _confirm_delete(win, "Delete BST node", description):
                return

            delete_bst_node(db_path, int(node_id))
            messagebox.showinfo("ADT", "BST node deleted.")
            win.destroy()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("ADT", f"Error: {exc}")

    tk.Button(win, text="Edit", command=do_update).pack(pady=(12, 4))
    tk.Button(win, text="Delete", command=do_delete).pack(pady=4)


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











