#!/usr/bin/env python3
"""Remove remaining function definitions that are now in modules."""

with open('presentation/gui.py', 'r') as f:
    lines = f.readlines()

# Find where to delete - from _bind_canvas_interactions to before build_ui  
start_idx = None
end_idx = None

for i, line in enumerate(lines):
    if 'def _bind_canvas_interactions' in line and start_idx is None:
        start_idx = i
    if 'def build_ui' in line and end_idx is None:
        end_idx = i

print(f"Delete range: {start_idx+1} to {end_idx} (before build_ui)")

if start_idx is not None and end_idx is not None:
    # Remove lines and keep the rest
    new_lines = lines[:start_idx] + lines[end_idx:]
    
    with open('presentation/gui.py', 'w') as f:
        f.writelines(new_lines)
    
    print(f"Deleted {end_idx - start_idx} lines")
    print("All old function definitions removed successfully")
    
    # Verify build_ui and main are still there
    content = ''.join(new_lines)
    if 'def build_ui' in content and 'def main' in content:
        print("✓ build_ui() and main() are intact")
    else:
        print("✗ ERROR: build_ui or main missing!")
else:
    print("Could not find the section to delete")
