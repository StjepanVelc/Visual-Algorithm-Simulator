"""Canvas rendering functions."""

import tkinter as tk

from presentation.utils import DEPTH_COLORS


def render_tree_canvas(
    canvas: tk.Canvas,
    rows: list[dict],
    value_key: str,
    layout_builder,
) -> None:
    """Render tree structure on canvas."""
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


def setup_scrollable_canvas(parent: tk.Widget) -> tk.Canvas:
    """Create a canvas with scrollbars."""
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


def normalize_frames_for_video(frames: list) -> list:
    """Normalize frame sizes for video export."""
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
