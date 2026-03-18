#!/usr/bin/env python3
"""Replace all private function calls with public ones."""

import re

with open('presentation/gui.py', 'r') as f:
    content = f.read()

# Replace private function calls with public ones using regex
replacements = {
    r'_render_tree_canvas': 'render_tree_canvas',
    r'_build_bst_layout': 'build_bst_layout',
    r'_build_general_tree_layout': 'build_general_tree_layout',
    r'_setup_scrollable_canvas': 'setup_scrollable_canvas',
    r'_capture_canvas_frame': 'capture_canvas_frame',
    r'_bind_canvas_interactions': 'bind_canvas_interactions',
    r'_build_bst_traversal_order': 'build_bst_traversal_order',
    r'_build_general_traversal_order': 'build_general_traversal_order',
    r'_highlight_node': 'highlight_node',
    r'_mark_trail_node': 'mark_trail_node',
    r'_highlight_search_path': 'highlight_search_path',
    r'_animate_travel_roundtrip': 'animate_travel_roundtrip',
    r'_build_option_map': 'build_option_map',
    r'_confirm_delete': 'confirm_delete',
    r'_extract_node_id_from_tags': 'extract_node_id_from_tags',
    r'_format_node_details': 'format_node_details',
    r'_normalize_frames_for_video': 'normalize_frames_for_video',
    r'_add_depth_legend': 'add_depth_legend',
}

for old_pattern, new_str in replacements.items():
    content = content.replace(old_pattern, new_str)

with open('presentation/gui.py', 'w') as f:
    f.write(content)

print('All replacements completed successfully')
