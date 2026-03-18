#!/usr/bin/env python3
"""Remove all private function definitions since they're now in modules."""

with open('presentation/gui.py', 'r') as f:
    lines = f.readlines()

# Find where to delete - from first _def to before open_algorithm_studio
start_idx = None
end_idx = None

for i, line in enumerate(lines):
    if 'def _add_depth_legend' in line and start_idx is None:
        start_idx = i
    if 'def open_algorithm_studio' in line and end_idx is None:
        end_idx = i

print(f"Delete range: {start_idx+1} to {end_idx}")

if start_idx is not None and end_idx is not None:
    # Remove lines and keep the rest
    new_lines = lines[:start_idx] + lines[end_idx:]
    
    with open('presentation/gui.py', 'w') as f:
        f.writelines(new_lines)
    
    print(f"Deleted {end_idx - start_idx} lines")
    print("Private function definitions removed successfully")
else:
    print("Could not find the section to delete")
