"""
Centralized validation and integrity checks for all tree structures.
Ensures data consistency, prevents duplicates, validates relationships, etc.
"""

from typing import Any


class ValidationError(ValueError):
    """Custom exception for validation failures."""
    pass


class TreeValidator:
    """Validates tree rows for integrity, duplicates, and structural consistency."""

    @staticmethod
    def validate_value(value: Any, tree_type: str, allow_null: bool = False) -> None:
        """Validate a single value for insertion/update."""
        if value is None and not allow_null:
            raise ValidationError("Value cannot be None")
        
        # String length check for hash keys
        if isinstance(value, str) and len(value) > 255:
            raise ValidationError(f"Value length {len(value)} exceeds 255 characters")
        
        # Numeric range check (if applicable)
        if isinstance(value, (int, float)):
            if tree_type in ("avl", "bst", "rbtree", "btree", "bplustree"):
                # Allow reasonable range for tree values
                if value not in range(-10**9, 10**9):
                    raise ValidationError(f"Value {value} out of supported range")

    @staticmethod
    def check_no_duplicates_bst(rows: list[dict], new_value: int) -> None:
        """Ensure no duplicate values in BST."""
        existing_values = {int(row.get("vrijednost", 0)) for row in rows}
        if new_value in existing_values:
            raise ValidationError(f"BST already contains value {new_value}")

    @staticmethod
    def check_no_duplicates_avl(rows: list[dict], new_value: int) -> None:
        """Ensure no duplicate values in AVL tree."""
        existing_values = {int(row.get("vrijednost", 0)) for row in rows}
        if new_value in existing_values:
            raise ValidationError(f"AVL tree already contains value {new_value}")

    @staticmethod
    def check_no_duplicates_rbtree(rows: list[dict], new_value: int) -> None:
        """Ensure no duplicate values in Red-Black tree."""
        existing_values = {int(row.get("vrijednost", 0)) for row in rows}
        if new_value in existing_values:
            raise ValidationError(f"Red-Black tree already contains value {new_value}")

    @staticmethod
    def check_no_duplicates_btree(rows: list[dict], new_value: int) -> None:
        """Ensure no duplicate values in B-Tree."""
        for row in rows:
            keys = row.get("keys", [])
            if isinstance(keys, list):
                keys_int = [int(k) for k in keys]
                if new_value in keys_int:
                    raise ValidationError(f"B-Tree already contains value {new_value}")

    @staticmethod
    def check_no_duplicates_bplus(rows: list[dict], new_value: int) -> None:
        """Ensure no duplicate values in B+ tree."""
        for row in rows:
            keys = row.get("keys", [])
            if isinstance(keys, list):
                keys_int = [int(k) for k in keys]
                if new_value in keys_int:
                    raise ValidationError(f"B+ tree already contains value {new_value}")

    @staticmethod
    def validate_parent_child_consistency(rows: list[dict], tree_type: str) -> None:
        """Verify all parent-child relationships are consistent."""
        if not rows:
            return
        
        node_ids = {int(row.get("id", 0)) for row in rows}
        
        for row in rows:
            node_id = int(row.get("id", 0))
            
            # Check parent exists if specified
            parent_id = row.get("parent_id")
            if parent_id is not None:
                parent_id_int = int(parent_id) if parent_id != "None" else None
                if parent_id_int is not None and parent_id_int not in node_ids:
                    raise ValidationError(
                        f"Node {node_id} references non-existent parent {parent_id_int}"
                    )
            
            # Check binary tree children (for BST, AVL, RB-Tree)
            if tree_type in ("bst", "avl", "rbtree"):
                left_id = row.get("lijevi_id")
                right_id = row.get("desni_id")
                
                if left_id is not None:
                    left_id_int = int(left_id) if left_id != "None" else None
                    if left_id_int is not None and left_id_int not in node_ids:
                        raise ValidationError(
                            f"Node {node_id} references non-existent left child {left_id_int}"
                        )
                
                if right_id is not None:
                    right_id_int = int(right_id) if right_id != "None" else None
                    if right_id_int is not None and right_id_int not in node_ids:
                        raise ValidationError(
                            f"Node {node_id} references non-existent right child {right_id_int}"
                        )

    @staticmethod
    def check_bst_property(rows: list[dict]) -> None:
        """Verify BST property: left < parent < right."""
        if not rows:
            return
        
        nodes_by_id = {int(row.get("id", 0)): row for row in rows}
        
        for row in rows:
            node_value = int(row.get("vrijednost", 0))
            
            # Check left child
            left_id = row.get("lijevi_id")
            if left_id is not None:
                left_id_int = int(left_id) if left_id != "None" else None
                if left_id_int is not None and left_id_int in nodes_by_id:
                    left_value = int(nodes_by_id[left_id_int].get("vrijednost", 0))
                    if left_value >= node_value:
                        raise ValidationError(
                            f"BST violation: left child {left_value} >= parent {node_value}"
                        )
            
            # Check right child
            right_id = row.get("desni_id")
            if right_id is not None:
                right_id_int = int(right_id) if right_id != "None" else None
                if right_id_int is not None and right_id_int in nodes_by_id:
                    right_value = int(nodes_by_id[right_id_int].get("vrijednost", 0))
                    if right_value <= node_value:
                        raise ValidationError(
                            f"BST violation: right child {right_value} <= parent {node_value}"
                        )

    @staticmethod
    def check_no_cycles(rows: list[dict], tree_type: str) -> None:
        """Ensure tree has no cycles (is acyclic)."""
        if not rows:
            return
        
        nodes_by_id = {int(row.get("id", 0)): row for row in rows}
        visited = set()
        path = set()
        
        def has_cycle(node_id: int) -> bool:
            if node_id in path:
                return True
            if node_id in visited:
                return False
            
            visited.add(node_id)
            path.add(node_id)
            
            node = nodes_by_id.get(node_id)
            if not node:
                path.remove(node_id)
                return False
            
            # Check binary tree children
            if tree_type in ("bst", "avl", "rbtree"):
                for child_field in ("lijevi_id", "desni_id"):
                    child_id = node.get(child_field)
                    if child_id is not None:
                        child_id_int = int(child_id) if child_id != "None" else None
                        if child_id_int is not None and has_cycle(child_id_int):
                            return True
            # Check n-ary tree children via parent_id reverse lookup
            elif tree_type == "tree":
                for other_id, other_node in nodes_by_id.items():
                    if other_node.get("parent_id") == node_id and has_cycle(other_id):
                        return True
            
            path.remove(node_id)
            return False
        
        # Check each potential root
        for node_id in nodes_by_id:
            if node_id not in visited:
                if has_cycle(node_id):
                    raise ValidationError("Cycle detected in tree structure")

    @staticmethod
    def check_single_root(rows: list[dict], tree_type: str) -> None:
        """Ensure tree has exactly one root (or is empty)."""
        if not rows:
            return
        
        if tree_type in ("bst", "avl", "rbtree"):
            # Binary trees should have one root
            roots = [row for row in rows if row.get("parent_id") is None]
            if len(roots) > 1:
                raise ValidationError(f"Multiple roots found: {len(roots)} root nodes")
        
        elif tree_type == "tree":
            # General trees allow multiple roots (forest)
            # But typically should have one
            roots = [row for row in rows if row.get("parent_id") is None]
            if len(roots) > 1:
                # Warning: multiple roots (forest), but allow if intentional
                pass

    @staticmethod
    def check_no_orphans(rows: list[dict]) -> None:
        """Ensure all nodes are reachable from root (no orphaned components)."""
        if not rows:
            return
        
        nodes_by_id = {int(row.get("id", 0)): row for row in rows}
        
        # Find roots
        roots = [row for row in rows if row.get("parent_id") is None]
        if not roots:
            # No roots = all orphaned
            raise ValidationError("No root node found; all nodes are orphaned")
        
        # BFS from all roots
        visited = set()
        queue = []
        
        for root in roots:
            root_id = int(root.get("id", 0))
            queue.append(root_id)
            visited.add(root_id)
        
        while queue:
            node_id = queue.pop(0)
            node = nodes_by_id.get(node_id)
            if not node:
                continue
            
            # Add children
            for child_field in ("lijevi_id", "desni_id"):
                child_id = node.get(child_field)
                if child_id is not None:
                    child_id_int = int(child_id) if child_id != "None" else None
                    if child_id_int is not None and child_id_int not in visited:
                        visited.add(child_id_int)
                        queue.append(child_id_int)
            
            # For n-ary trees, add children via parent_id
            for other_id, other_node in nodes_by_id.items():
                if other_node.get("parent_id") == node_id and other_id not in visited:
                    visited.add(other_id)
                    queue.append(other_id)
        
        # Check for orphans
        orphans = set(nodes_by_id.keys()) - visited
        if orphans:
            raise ValidationError(f"Orphaned nodes found: {orphans}")

    @staticmethod
    def validate_btree_degree(rows: list[dict], min_degree: int = 2) -> None:
        """Validate B-Tree node degree constraints."""
        for row in rows:
            keys = row.get("keys", [])
            key_count = len(keys) if isinstance(keys, list) else 0
            child_ids = row.get("child_ids", [])
            child_count = len(child_ids) if isinstance(child_ids, list) else 0
            
            # Check key count
            max_keys = 2 * min_degree - 1
            if key_count > max_keys:
                raise ValidationError(
                    f"B-Tree node {row.get('id')} has {key_count} keys, max {max_keys}"
                )
            
            # Check child count for internal nodes
            if child_count > 0:
                max_children = 2 * min_degree
                if child_count > max_children:
                    raise ValidationError(
                        f"B-Tree node {row.get('id')} has {child_count} children, max {max_children}"
                    )

    @staticmethod
    def validate_bplus_order(rows: list[dict], order: int = 4) -> None:
        """Validate B+ Tree order constraints."""
        max_keys = order - 1
        
        for row in rows:
            keys = row.get("keys", [])
            key_count = len(keys) if isinstance(keys, list) else 0
            
            if key_count > max_keys:
                raise ValidationError(
                    f"B+ Tree node {row.get('id')} has {key_count} keys, max {max_keys}"
                )

    @staticmethod
    def validate_hash_bucket(bucket_index: int, num_buckets: int = 16) -> None:
        """Validate hash table bucket index."""
        if bucket_index < 0 or bucket_index >= num_buckets:
            raise ValidationError(
                f"Bucket index {bucket_index} out of range [0, {num_buckets})"
            )

    @staticmethod
    def check_general_tree_no_duplicates(rows: list[dict], new_value: int) -> None:
        """Ensure no duplicate values in general tree."""
        existing_values = {int(row.get("vrijednost", 0)) for row in rows if "vrijednost" in row}
        if new_value in existing_values:
            raise ValidationError(f"General tree already contains value {new_value}")

    # Public API - comprehensive checks
    
    @staticmethod
    def validate_bst_insertion(rows: list[dict], value: int) -> None:
        """Comprehensive validation before BST insertion."""
        TreeValidator.validate_value(value, "bst")
        TreeValidator.check_no_duplicates_bst(rows, value)
        TreeValidator.validate_parent_child_consistency(rows, "bst")

    @staticmethod
    def validate_avl_insertion(rows: list[dict], value: int) -> None:
        """Comprehensive validation before AVL insertion."""
        TreeValidator.validate_value(value, "avl")
        TreeValidator.check_no_duplicates_avl(rows, value)
        TreeValidator.validate_parent_child_consistency(rows, "avl")

    @staticmethod
    def validate_rbtree_insertion(rows: list[dict], value: int) -> None:
        """Comprehensive validation before Red-Black tree insertion."""
        TreeValidator.validate_value(value, "rbtree")
        TreeValidator.check_no_duplicates_rbtree(rows, value)
        TreeValidator.validate_parent_child_consistency(rows, "rbtree")

    @staticmethod
    def validate_btree_insertion(rows: list[dict], value: int) -> None:
        """Comprehensive validation before B-Tree insertion."""
        TreeValidator.validate_value(value, "btree")
        TreeValidator.check_no_duplicates_btree(rows, value)
        TreeValidator.validate_btree_degree(rows, min_degree=2)

    @staticmethod
    def validate_bplus_insertion(rows: list[dict], value: int) -> None:
        """Comprehensive validation before B+ Tree insertion."""
        TreeValidator.validate_value(value, "bplustree")
        TreeValidator.check_no_duplicates_bplus(rows, value)
        TreeValidator.validate_bplus_order(rows, order=4)

    @staticmethod
    def validate_general_tree_insertion(rows: list[dict], value: int, parent_id: int | None) -> None:
        """Comprehensive validation before general tree insertion."""
        TreeValidator.validate_value(value, "tree")
        TreeValidator.check_general_tree_no_duplicates(rows, value)
        
        # Validate parent exists if specified
        if parent_id is not None:
            parent_exists = any(int(row.get("id", 0)) == parent_id for row in rows)
            if not parent_exists:
                raise ValidationError(f"Parent node {parent_id} does not exist")

    @staticmethod
    def validate_tree_integrity(rows: list[dict], tree_type: str) -> None:
        """Full integrity check for any tree type."""
        if not rows:
            return
        
        try:
            TreeValidator.validate_parent_child_consistency(rows, tree_type)
            TreeValidator.check_no_cycles(rows, tree_type)
            TreeValidator.check_single_root(rows, tree_type)
            TreeValidator.check_no_orphans(rows)
            
            if tree_type in ("bst", "avl", "rbtree"):
                TreeValidator.check_bst_property(rows)
            elif tree_type == "btree":
                TreeValidator.validate_btree_degree(rows, min_degree=2)
            elif tree_type == "bplustree":
                TreeValidator.validate_bplus_order(rows, order=4)
        except ValidationError as e:
            raise ValidationError(f"Tree integrity check failed for {tree_type}: {str(e)}")
