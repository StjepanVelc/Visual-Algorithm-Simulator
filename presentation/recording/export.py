"""Export helpers for recorded animation frames."""

from tkinter import filedialog, messagebox

from presentation.canvas.renderers import normalize_frames_for_video
from presentation.recording.capture import ImageGrab


def export_gif(parent, frame_store: list) -> None:
    if ImageGrab is None:
        messagebox.showwarning("Export", "Pillow is not available for GIF export.", parent=parent)
        return
    if not frame_store:
        messagebox.showwarning("Export", "No recorded frames. Enable 'Record frames' and run a few steps.", parent=parent)
        return

    out = filedialog.asksaveasfilename(defaultextension=".gif", filetypes=[("GIF", "*.gif")])
    if not out:
        return

    try:
        first = frame_store[0]
        first.save(out, save_all=True, append_images=frame_store[1:], duration=120, loop=0)
        messagebox.showinfo("Export", f"GIF saved: {out}", parent=parent)
    except Exception as exc:  # noqa: BLE001
        messagebox.showerror("Export", f"GIF export failed: {exc}", parent=parent)


def export_video(parent, frame_store: list, imageio_module) -> None:
    if imageio_module is None:
        messagebox.showwarning("Export", "imageio is not available for video export.", parent=parent)
        return
    if not frame_store:
        messagebox.showwarning("Export", "No recorded frames. Enable 'Record frames' and run a few steps.", parent=parent)
        return

    out = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4", "*.mp4")])
    if not out:
        return

    try:
        frames = normalize_frames_for_video(frame_store)
        imageio_module.imwrite(out, frames, fps=8)
        messagebox.showinfo("Export", f"Video saved: {out}", parent=parent)
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
            parent=parent,
        )


def clear_recorded_frames(parent, frame_store: list, on_cleared) -> None:
    frame_store.clear()
    on_cleared()
    messagebox.showinfo("Export", "Recorded frames were cleared.", parent=parent)
