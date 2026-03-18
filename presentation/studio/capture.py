"""Capture panel and recording state for the Visual Studio window."""

from dataclasses import dataclass
import importlib
import tkinter as tk
from typing import Any, Callable

from presentation.recording.capture import ImageGrab, capture_canvas_frame


@dataclass
class CaptureContext:
    frame_store: list
    recording_var: tk.BooleanVar
    frame_status_var: tk.StringVar
    imageio_module: Any
    capture_frame: Callable[[tk.Canvas], None]
    clear_recording_state: Callable[[], None]


def create_capture_context(parent: tk.Widget) -> CaptureContext:
    try:
        imageio_module = importlib.import_module("imageio.v3")
    except Exception:  # noqa: BLE001
        imageio_module = None

    frame_store: list = []
    recording_var = tk.BooleanVar(value=False)
    frame_status_var = tk.StringVar(value="Frames: 0 | Recording: OFF")
    capture_error: list[str | None] = [None]

    def update_frame_status() -> None:
        recording_state = "ON" if recording_var.get() else "OFF"
        text = f"Frames: {len(frame_store)} | Recording: {recording_state}"
        if capture_error[0]:
            text = f"{text} | {capture_error[0]}"
        frame_status_var.set(text)

    def on_recording_toggle(*_: object) -> None:
        if not recording_var.get():
            capture_error[0] = None
        update_frame_status()

    recording_var.trace_add("write", on_recording_toggle)

    def capture_frame(canvas: tk.Canvas) -> None:
        captured = capture_canvas_frame(canvas, frame_store, recording_var.get())
        if captured:
            capture_error[0] = None
        elif recording_var.get() and ImageGrab is None:
            capture_error[0] = "Pillow ImageGrab is not available"
        elif recording_var.get() and ImageGrab is not None:
            capture_error[0] = "Capture failed (keep the window visible on screen)"
        update_frame_status()

    def clear_recording_state() -> None:
        capture_error[0] = None
        update_frame_status()

    panel = tk.LabelFrame(parent, text="Capture", bg="#eef3f8", padx=8, pady=6)
    panel.pack(fill="x", padx=10, pady=(10, 6))
    tk.Checkbutton(panel, text="Record frames", variable=recording_var, bg="#eef3f8").pack(anchor="w")
    tk.Label(panel, text="For GIF/MP4 export", bg="#eef3f8", fg="#3f5163", font=("Segoe UI", 8)).pack(anchor="w")
    tk.Label(panel, textvariable=frame_status_var, bg="#eef3f8", fg="#1f3a56", justify="left", wraplength=158).pack(anchor="w", pady=(4, 0))

    return CaptureContext(
        frame_store=frame_store,
        recording_var=recording_var,
        frame_status_var=frame_status_var,
        imageio_module=imageio_module,
        capture_frame=capture_frame,
        clear_recording_state=clear_recording_state,
    )
