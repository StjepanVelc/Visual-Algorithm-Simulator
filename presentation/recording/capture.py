"""Canvas frame capture for GIF/MP4 export."""

import importlib
import tkinter as tk

try:
    ImageGrab = importlib.import_module("PIL.ImageGrab")
except Exception:  # noqa: BLE001
    ImageGrab = None


def capture_canvas_frame(canvas: tk.Canvas, frame_store: list, recording_enabled: bool) -> bool:
    """Capture a single canvas frame if recording is enabled."""
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
