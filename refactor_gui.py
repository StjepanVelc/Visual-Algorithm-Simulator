#!/usr/bin/env python3
"""Refactor gui.py to use new modularized components."""

import re

# Read current gui.py
with open('presentation/gui.py', 'r') as f:
    lines = f.readlines()

# Find key sections
studio_start = None
form_start = None
build_ui_start = None

for i, line in enumerate(lines):
    if 'def open_algorithm_studio' in line and studio_start is None:
        studio_start = i
    if 'def open_hash_form' in line and form_start is None:
        form_start = i
    if 'def build_ui' in line and build_ui_start is None:
        build_ui_start = i

print(f"studio_start: {studio_start+1}")
print(f"form_start: {form_start+1}")
print(f"build_ui_start: {build_ui_start+1}")

# Read full content
content = ''.join(lines)

# Extract just the sections we need
studio_end = form_start
utilities_end = studio_start

# Get the studio code
studio_code = ''.join(lines[studio_start:studio_end])

# Get the build_ui and main code
build_ui_code = ''.join(lines[build_ui_start:])

# Now need to replace private functions with public ones
replacements = {
    '_render_tree_canvas': 'render_tree_canvas',
    '_build_bst_layout': 'build_bst_layout',
    '_build_general_tree_layout': 'build_general_tree_layout',
    '_setup_scrollable_canvas': 'setup_scrollable_canvas',
    '_capture_canvas_frame': 'capture_canvas_frame',
    '_bind_canvas_interactions': 'bind_canvas_interactions',
    '_build_bst_traversal_order': 'build_bst_traversal_order',
    '_build_general_traversal_order': 'build_general_traversal_order',
    '_highlight_node': 'highlight_node',
    '_mark_trail_node': 'mark_trail_node',
    '_highlight_search_path': 'highlight_search_path',
    '_animate_travel_roundtrip': 'animate_travel_roundtrip',
    '_build_option_map': 'build_option_map',
    '_confirm_delete': 'confirm_delete',
    '_extract_node_id_from_tags': 'extract_node_id_from_tags',
    '_format_node_details': 'format_node_details',
    '_normalize_frames_for_video': 'normalize_frames_for_video',
    '_add_depth_legend': 'add_depth_legend',
}

for old, new in replacements.items():
    studio_code = studio_code.replace(old, new)

# Create new imports section
new_imports = '''"""Main GUI entry point and Visual Studio interface."""

import tkinter as tk
from collections import defaultdict
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

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

# Import UI components
from presentation.db_operations import on_build_db, on_export_sql, on_generate_report, on_import_sql
from presentation.forms.bst_form import open_bst_form, open_bst_manage_form
from presentation.forms.general_tree_form import open_general_tree_form, open_general_tree_manage_form
from presentation.forms.hash_form import open_hash_form, open_hash_manage_form
from presentation.forms.recursion_form import open_recursion_form, open_recursion_manage_form
from presentation.canvas.interactions import (
    animate_travel_roundtrip,
    bind_canvas_interactions,
    highlight_node,
    highlight_search_path,
    mark_trail_node,
)
from presentation.canvas.layouts import build_bst_layout, build_general_tree_layout
from presentation.canvas.renderers import normalize_frames_for_video, render_tree_canvas, setup_scrollable_canvas
from presentation.canvas.traversals import build_bst_traversal_order, build_general_traversal_order
from presentation.recording.capture import capture_canvas_frame
from presentation.utils import (
    DEPTH_COLORS,
    add_depth_legend,
    build_option_map,
    confirm_delete,
    ensure_db,
    extract_node_id_from_tags,
    format_node_details,
    parse_optional_int,
    resolve_paths,
)

'''

# Create new gui.py
new_gui = new_imports + "\n" + studio_code + "\n\n" + build_ui_code

# Write new gui.py
with open('presentation/gui_new.py', 'w') as f:
    f.write(new_gui)

print(f"New gui.py created with {len(new_gui)} characters")
print(f"Original size: {len(content)} characters")
print(f"Reduced by: {len(content) - len(new_gui)} characters ({100*(len(content)-len(new_gui))/len(content):.1f}%)")
