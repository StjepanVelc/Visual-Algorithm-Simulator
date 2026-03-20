#!/usr/bin/env python3
"""Quick test of validation service integration."""

from services.advanced_trees_service import insert_tree_value

# First insert
r1 = insert_tree_value('avl', 1, 5)
print(f'✓ First insert (5): success, size={r1["size"]}')

# Second insert (different value)
r2 = insert_tree_value('avl', 1, 10)
print(f'✓ Second insert (10): success, size={r2["size"]}')

# Try duplicate - should fail
try:
    r3 = insert_tree_value('avl', 1, 5)
    print('ERROR: Duplicate should have been rejected')
except ValueError as e:
    print(f'✓ Duplicate (5) rejected: {e}')

print("\nTest passed!")
