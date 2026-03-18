"""Recursion view for the algorithm studio."""

import tkinter as tk
from collections import defaultdict
from pathlib import Path
from typing import Callable

from services.adt_service import collect_state


def create_recursion_view(
    parent: tk.Widget,
    db_path: Path,
    capture_frame: Callable[[tk.Canvas], None],
) -> tuple[tk.Frame, Callable[[], None]]:
    view = tk.Frame(parent)
    tk.Label(view, text="Recursion - stack animation", font=("Segoe UI", 12, "bold")).pack(pady=(10, 6))
    rec_canvas = tk.Canvas(view, bg="#f7fafc")
    rec_canvas.pack(fill="both", expand=True, padx=12, pady=8)

    rec_order: list[int] = []
    rec_rows: dict[int, dict] = {}
    rec_step = 0
    next_button_ref: list[tk.Button | None] = [None]
    status_ref: list[tk.Label | None] = [None]

    def build_order() -> tuple[list[int], dict[int, dict]]:
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

    def draw_stack(current_id: int | None) -> None:
        rec_canvas.delete("all")
        if current_id is None:
            rec_canvas.create_text(20, 20, anchor="nw", text="Click Next step to grow the stack.")
            return

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

    def refresh() -> None:
        nonlocal rec_order, rec_rows, rec_step
        rec_order, rec_rows = build_order()
        rec_step = 0
        if next_button_ref[0]:
            next_button_ref[0].configure(state="normal")
        if status_ref[0]:
            status_ref[0].configure(text="")
        draw_stack(None)

    def next_step() -> None:
        nonlocal rec_step
        if rec_step >= len(rec_order):
            if next_button_ref[0]:
                next_button_ref[0].configure(state="disabled")
            if status_ref[0]:
                status_ref[0].configure(text="-> Completed")
            return
        draw_stack(rec_order[rec_step])
        rec_step += 1
        capture_frame(rec_canvas)

    buttons = tk.Frame(view)
    buttons.pack(fill="x", padx=12, pady=(0, 8))
    tk.Button(buttons, text="Reset", command=refresh).pack(side="left", padx=4)
    next_button_ref[0] = tk.Button(buttons, text="Next step", command=next_step)
    next_button_ref[0].pack(side="left", padx=4)
    status_ref[0] = tk.Label(buttons, text="", fg="#c0392b", font=("Segoe UI", 9, "bold"))
    status_ref[0].pack(side="left", padx=8)

    return view, refresh
