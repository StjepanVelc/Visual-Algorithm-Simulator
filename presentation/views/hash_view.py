"""Hash view for the algorithm studio."""

import tkinter as tk
from collections import defaultdict
from pathlib import Path
from typing import Callable

from services.adt_service import collect_state


def create_hash_view(parent: tk.Widget, db_path: Path) -> tuple[tk.Frame, Callable[[], None]]:
    view = tk.Frame(parent)
    tk.Label(view, text="Hash - bucket overview", font=("Segoe UI", 12, "bold")).pack(pady=(12, 6))
    hash_text = tk.Text(view, height=25)
    hash_text.pack(fill="both", expand=True, padx=12, pady=8)

    def refresh() -> None:
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

    tk.Button(view, text="Refresh", command=refresh).pack(pady=(0, 10))
    return view, refresh
