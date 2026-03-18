"""Canvas interactions and animations."""

import tkinter as tk

from presentation.utils import extract_node_id_from_tags, format_node_details


def bind_canvas_interactions(canvas: tk.Canvas, details_label: tk.Label) -> None:
    """Bind mouse interactions to canvas for node selection."""

    def on_canvas_click(event):
        obj = canvas.find_closest(event.x, event.y)
        if not obj:
            return
        tags = canvas.gettags(obj[0])
        node_id = extract_node_id_from_tags(tags)
        if node_id is not None:
            highlight_node(canvas, node_id)
            node_data = getattr(canvas, "_node_data", {})
            node_row = node_data.get(node_id)
            if node_row:
                text = format_node_details(node_row)
                details_label.configure(text=text)

    def on_canvas_wheel(event):
        canvas_zoom = getattr(canvas, "_tree_zoom", 1.0)
        if event.delta > 0:
            canvas_zoom *= 1.1
        else:
            canvas_zoom /= 1.1
        canvas._tree_zoom = canvas_zoom  # type: ignore[attr-defined]

    def on_mouse_press(event):
        canvas.scan_mark(event.x, event.y)

    def on_mouse_drag(event):
        canvas.scan_dragto(event.x, event.y, gain=1)

    canvas.bind("<Button-1>", on_canvas_click)
    canvas.bind("<MouseWheel>", on_canvas_wheel)
    canvas.bind("<Button-3>", on_mouse_press)
    canvas.bind("<B3-Motion>", on_mouse_drag)


def highlight_node(canvas: tk.Canvas, node_id: int, color: str = "#f39c12") -> None:
    """Highlight a single node."""
    oval_item_ids = getattr(canvas, "_node_ovals", {})
    for oval_id in oval_item_ids.values():
        canvas.itemconfigure(oval_id, width=2, outline="#2c5d82")

    target = oval_item_ids.get(node_id)
    if target is not None:
        canvas.itemconfigure(target, width=4, outline=color)


def mark_trail_node(canvas: tk.Canvas, node_id: int, color: str = "#f0a500") -> None:
    """Mark a waypoint node during traversal animation."""
    oval_item_ids = getattr(canvas, "_node_ovals", {})
    target = oval_item_ids.get(node_id)
    if target is not None:
        canvas.itemconfigure(target, width=3, outline=color)


def highlight_search_path(canvas: tk.Canvas, visited_ids: list[int], current_id: int) -> None:
    """Show the full search path with trail and active node."""
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


def animate_travel_roundtrip(
    canvas: tk.Canvas,
    node_id: int,
    capture_frame_cb,
    on_done,
) -> None:
    """Animate marker traveling to node and back."""
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
