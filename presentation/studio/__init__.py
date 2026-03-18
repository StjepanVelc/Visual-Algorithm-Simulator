"""Studio composition helpers for the Visual Studio window."""

from presentation.studio.capture import CaptureContext, create_capture_context
from presentation.studio.sidebar import create_crud_panel, create_navigation_panel

__all__ = [
    "CaptureContext",
    "create_capture_context",
    "create_crud_panel",
    "create_navigation_panel",
]
