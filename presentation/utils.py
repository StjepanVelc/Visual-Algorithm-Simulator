"""Utility functions for presentation layer."""

import tkinter as tk
from pathlib import Path
from tkinter import messagebox

DEPTH_COLORS = [
    "#d9eefc",
    "#dff7e3",
    "#fff1d6",
    "#fde0e0",
    "#e9e2ff",
    "#ffe7f5",
]


def add_depth_legend(parent: tk.Widget) -> None:
    """Add depth color legend to parent widget."""
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
    """Resolve base directory and paths to database and report directory."""
    base_dir = Path(__file__).resolve().parent.parent
    db_path = base_dir / "adt.db"
    report_dir = base_dir / "izvjestaji"
    return db_path, report_dir


def ensure_db() -> Path | None:
    """Check if database exists and show warning if not."""
    db_path, _ = resolve_paths()
    if not db_path.exists():
        tk.messagebox.showwarning("ADT", "Database does not exist. Create it first.")
        return None
    return db_path


def parse_optional_int(value: str) -> int | None:
    """Parse an optional integer from string."""
    text = value.strip()
    if not text:
        return None
    return int(text)


def build_option_map(options: list[tuple[str, int | None]]) -> dict[str, int | None]:
    """Build a mapping from label to value from option tuples."""
    return {label: value for label, value in options}


def extract_node_id_from_tags(tags: tuple[str, ...]) -> int | None:
    """Extract node ID from canvas tags."""
    for tag in tags:
        if tag.startswith("node_"):
            try:
                return int(tag.removeprefix("node_"))
            except ValueError:
                return None
    return None


def format_node_details(row: dict) -> str:
    """Format node details for display."""
    ordered = [f"{key}={row[key]}" for key in row.keys()]
    return " | ".join(ordered)


def confirm_delete(parent: tk.Misc, title: str, description: str) -> bool:
    """Show delete confirmation dialog."""
    return tk.messagebox.askyesno(
        "Delete confirmation",
        f"{title}\n\n{description}\n\nAre you sure you want to delete this node?",
        parent=parent,
        icon="warning",
    )
