from __future__ import annotations

from bisect import bisect_left, bisect_right
from collections import deque
from dataclasses import dataclass, field
from typing import Any

from services.validation_service import TreeValidator, ValidationError

SUPPORTED_TYPES = {"avl", "btree", "bplustree", "rbtree"}

BTREE_MIN_DEGREE = 2
BPLUS_ORDER = 4
BPLUS_MAX_KEYS = BPLUS_ORDER - 1
BPLUS_MIN_INTERNAL_CHILDREN = 2
BPLUS_MIN_LEAF_KEYS = 2


@dataclass
class BinaryNode:
    value: int
    left: BinaryNode | None = None
    right: BinaryNode | None = None


@dataclass
class BTreeNode:
    keys: list[int] = field(default_factory=list)
    children: list[BTreeNode] = field(default_factory=list)
    leaf: bool = True


@dataclass
class BPlusNode:
    keys: list[int] = field(default_factory=list)
    children: list[BPlusNode] = field(default_factory=list)
    leaf: bool = True
    next_leaf: BPlusNode | None = None


_VALUE_STATE: dict[tuple[str, int], list[int]] = {}
_BTREE_STATE: dict[tuple[str, int], BTreeNode | None] = {}
_BPLUS_STATE: dict[tuple[str, int], BPlusNode | None] = {}


def _ensure_supported(tree_type: str) -> None:
    if tree_type not in SUPPORTED_TYPES:
        raise ValueError(f"Unsupported tree type: {tree_type}")


def _state_key(tree_type: str, db_id: int) -> tuple[str, int]:
    _ensure_supported(tree_type)
    return tree_type, db_id


def _normalize_unique(values: list[int]) -> list[int]:
    seen: set[int] = set()
    normalized: list[int] = []
    for value in values:
        item = int(value)
        if item in seen:
            continue
        seen.add(item)
        normalized.append(item)
    return normalized


def _get_binary_values(tree_type: str, db_id: int) -> list[int]:
    return list(_VALUE_STATE.get(_state_key(tree_type, db_id), []))


def _set_binary_values(tree_type: str, db_id: int, values: list[int]) -> None:
    _VALUE_STATE[_state_key(tree_type, db_id)] = _normalize_unique(values)


def _build_balanced_binary_tree(values: list[int]) -> BinaryNode | None:
    ordered = sorted(set(values))

    def build(items: list[int]) -> BinaryNode | None:
        if not items:
            return None
        mid = len(items) // 2
        node = BinaryNode(items[mid])
        node.left = build(items[:mid])
        node.right = build(items[mid + 1 :])
        return node

    return build(ordered)


def _binary_search_path(root: BinaryNode | None, target: int) -> tuple[list[int], bool]:
    path: list[int] = []
    current = root
    while current is not None:
        path.append(current.value)
        if current.value == target:
            return path, True
        if target < current.value:
            current = current.left
        else:
            current = current.right
    return path, False


def _binary_traverse(root: BinaryNode | None, method: str) -> list[int]:
    if root is None:
        return []

    mode = method.lower()
    if mode == "bfs":
        order: list[int] = []
        queue: deque[BinaryNode] = deque([root])
        while queue:
            node = queue.popleft()
            order.append(node.value)
            if node.left is not None:
                queue.append(node.left)
            if node.right is not None:
                queue.append(node.right)
        return order

    if mode == "dfs":
        order: list[int] = []

        def visit(node: BinaryNode | None) -> None:
            if node is None:
                return
            order.append(node.value)
            visit(node.left)
            visit(node.right)

        visit(root)
        return order

    raise ValueError("Traversal method must be bfs or dfs")


def _serialize_binary_tree(root: BinaryNode | None, tree_type: str) -> dict[str, Any]:
    if root is None:
        return {"nodes": [], "keys": [], "root": None}

    nodes: list[dict[str, Any]] = []
    id_counter = 1

    def color_for_depth(depth: int) -> str:
        if tree_type != "rbtree":
            return "balanced"
        return "black" if depth % 2 == 0 else "red"

    def walk(node: BinaryNode | None, parent_id: int | None, depth: int) -> int | None:
        nonlocal id_counter
        if node is None:
            return None

        node_id = id_counter
        id_counter += 1

        left_id = walk(node.left, node_id, depth + 1)
        right_id = walk(node.right, node_id, depth + 1)

        nodes.append(
            {
                "id": node_id,
                "parent_id": parent_id,
                "vrijednost": node.value,
                "lijevi_id": left_id,
                "desni_id": right_id,
                "color": color_for_depth(depth),
            }
        )
        return node_id

    root_id = walk(root, None, 0)
    nodes.sort(key=lambda item: item["id"])
    return {
        "nodes": nodes,
        "keys": sorted(node["vrijednost"] for node in nodes),
        "root": root_id,
    }


def _split_btree_child(parent: BTreeNode, child_index: int) -> None:
    child = parent.children[child_index]
    right = BTreeNode(leaf=child.leaf)
    median = child.keys[BTREE_MIN_DEGREE - 1]

    right.keys = child.keys[BTREE_MIN_DEGREE:]
    child.keys = child.keys[: BTREE_MIN_DEGREE - 1]

    if not child.leaf:
        right.children = child.children[BTREE_MIN_DEGREE:]
        child.children = child.children[:BTREE_MIN_DEGREE]

    parent.keys.insert(child_index, median)
    parent.children.insert(child_index + 1, right)


def _btree_insert_non_full(node: BTreeNode, key: int) -> None:
    if node.leaf:
        idx = bisect_left(node.keys, key)
        if idx < len(node.keys) and node.keys[idx] == key:
            return
        node.keys.insert(idx, key)
        return

    idx = bisect_right(node.keys, key)
    child = node.children[idx]
    if len(child.keys) == (2 * BTREE_MIN_DEGREE - 1):
        _split_btree_child(node, idx)
        if key > node.keys[idx]:
            idx += 1
    _btree_insert_non_full(node.children[idx], key)


def _create_btree() -> BTreeNode | None:
    return None


def _get_btree(tree_type: str, db_id: int) -> BTreeNode | None:
    return _BTREE_STATE.get(_state_key(tree_type, db_id), _create_btree())


def _set_btree(tree_type: str, db_id: int, root: BTreeNode | None) -> None:
    _BTREE_STATE[_state_key(tree_type, db_id)] = root


def _btree_insert(tree_type: str, db_id: int, key: int) -> BTreeNode:
    root = _get_btree(tree_type, db_id)
    if root is None:
        root = BTreeNode(keys=[key], leaf=True)
        _set_btree(tree_type, db_id, root)
        return root

    if _btree_contains(root, key):
        return root

    if len(root.keys) == (2 * BTREE_MIN_DEGREE - 1):
        new_root = BTreeNode(leaf=False, children=[root])
        _split_btree_child(new_root, 0)
        root = new_root

    _btree_insert_non_full(root, key)
    _set_btree(tree_type, db_id, root)
    return root


def _btree_contains(node: BTreeNode | None, key: int) -> bool:
    if node is None:
        return False
    idx = bisect_left(node.keys, key)
    if idx < len(node.keys) and node.keys[idx] == key:
        return True
    if node.leaf:
        return False
    return _btree_contains(node.children[idx], key)


def _btree_get_predecessor(node: BTreeNode) -> int:
    current = node
    while not current.leaf:
        current = current.children[-1]
    return current.keys[-1]


def _btree_get_successor(node: BTreeNode) -> int:
    current = node
    while not current.leaf:
        current = current.children[0]
    return current.keys[0]


def _btree_merge_children(parent: BTreeNode, index: int) -> None:
    left = parent.children[index]
    right = parent.children[index + 1]
    left.keys.append(parent.keys[index])
    left.keys.extend(right.keys)
    if not left.leaf:
        left.children.extend(right.children)
    parent.keys.pop(index)
    parent.children.pop(index + 1)


def _btree_borrow_from_prev(parent: BTreeNode, index: int) -> None:
    child = parent.children[index]
    sibling = parent.children[index - 1]

    child.keys.insert(0, parent.keys[index - 1])
    parent.keys[index - 1] = sibling.keys.pop()

    if not sibling.leaf:
        child.children.insert(0, sibling.children.pop())


def _btree_borrow_from_next(parent: BTreeNode, index: int) -> None:
    child = parent.children[index]
    sibling = parent.children[index + 1]

    child.keys.append(parent.keys[index])
    parent.keys[index] = sibling.keys.pop(0)

    if not sibling.leaf:
        child.children.append(sibling.children.pop(0))


def _btree_fill_child(parent: BTreeNode, index: int) -> None:
    if index > 0 and len(parent.children[index - 1].keys) >= BTREE_MIN_DEGREE:
        _btree_borrow_from_prev(parent, index)
    elif index < len(parent.children) - 1 and len(parent.children[index + 1].keys) >= BTREE_MIN_DEGREE:
        _btree_borrow_from_next(parent, index)
    elif index < len(parent.children) - 1:
        _btree_merge_children(parent, index)
    else:
        _btree_merge_children(parent, index - 1)


def _btree_delete_from_node(node: BTreeNode, key: int) -> bool:
    idx = bisect_left(node.keys, key)

    if idx < len(node.keys) and node.keys[idx] == key:
        if node.leaf:
            node.keys.pop(idx)
            return True

        if len(node.children[idx].keys) >= BTREE_MIN_DEGREE:
            predecessor = _btree_get_predecessor(node.children[idx])
            node.keys[idx] = predecessor
            return _btree_delete_from_node(node.children[idx], predecessor)

        if len(node.children[idx + 1].keys) >= BTREE_MIN_DEGREE:
            successor = _btree_get_successor(node.children[idx + 1])
            node.keys[idx] = successor
            return _btree_delete_from_node(node.children[idx + 1], successor)

        _btree_merge_children(node, idx)
        return _btree_delete_from_node(node.children[idx], key)

    if node.leaf:
        return False

    child_index = idx
    if len(node.children[child_index].keys) < BTREE_MIN_DEGREE:
        _btree_fill_child(node, child_index)
        if child_index > len(node.keys):
            child_index -= 1

    return _btree_delete_from_node(node.children[child_index], key)


def _btree_delete(tree_type: str, db_id: int, key: int) -> BTreeNode | None:
    root = _get_btree(tree_type, db_id)
    if root is None:
        return None

    removed = _btree_delete_from_node(root, key)
    if not removed:
        return root

    if not root.keys and not root.leaf:
        root = root.children[0]
    elif not root.keys and root.leaf:
        root = None

    _set_btree(tree_type, db_id, root)
    return root


def _btree_search_path(root: BTreeNode | None, target: int) -> tuple[list[int], bool]:
    path: list[int] = []
    current = root
    while current is not None:
        if not current.keys:
            break
        idx = bisect_left(current.keys, target)
        if idx < len(current.keys) and current.keys[idx] == target:
            path.append(current.keys[idx])
            return path, True
        marker_index = min(idx, len(current.keys) - 1)
        path.append(current.keys[marker_index])
        if current.leaf:
            return path, False
        current = current.children[idx]
    return path, False


def _btree_traverse(root: BTreeNode | None, method: str) -> list[int]:
    if root is None:
        return []

    mode = method.lower()
    if mode == "bfs":
        order: list[int] = []
        queue: deque[BTreeNode] = deque([root])
        while queue:
            node = queue.popleft()
            order.extend(node.keys)
            for child in node.children:
                queue.append(child)
        return order

    if mode == "dfs":
        order: list[int] = []

        def visit(node: BTreeNode) -> None:
            order.extend(node.keys)
            for child in node.children:
                visit(child)

        visit(root)
        return order

    raise ValueError("Traversal method must be bfs or dfs")


def _btree_levels(root: BTreeNode | None) -> list[list[list[int]]]:
    if root is None:
        return []
    levels: list[list[list[int]]] = []
    queue: deque[tuple[BTreeNode, int]] = deque([(root, 0)])
    while queue:
        node, depth = queue.popleft()
        if len(levels) <= depth:
            levels.append([])
        levels[depth].append(list(node.keys))
        for child in node.children:
            queue.append((child, depth + 1))
    return levels


def _bplus_first_key(node: BPlusNode) -> int:
    current = node
    while not current.leaf:
        current = current.children[0]
    return current.keys[0]


def _bplus_refresh_keys(node: BPlusNode) -> None:
    if node.leaf:
        return
    node.keys = [_bplus_first_key(child) for child in node.children[1:]]


def _bplus_leaf_overflow(node: BPlusNode) -> bool:
    return len(node.keys) > BPLUS_MAX_KEYS


def _bplus_internal_overflow(node: BPlusNode) -> bool:
    return len(node.children) > BPLUS_ORDER


def _bplus_split_leaf(node: BPlusNode) -> BPlusNode:
    mid = len(node.keys) // 2
    right = BPlusNode(keys=node.keys[mid:], leaf=True, next_leaf=node.next_leaf)
    node.keys = node.keys[:mid]
    node.next_leaf = right
    return right


def _bplus_split_internal(node: BPlusNode) -> BPlusNode:
    mid = len(node.children) // 2
    right = BPlusNode(children=node.children[mid:], leaf=False)
    node.children = node.children[:mid]
    _bplus_refresh_keys(node)
    _bplus_refresh_keys(right)
    return right


def _bplus_insert_into_node(node: BPlusNode, key: int) -> BPlusNode | None:
    if node.leaf:
        idx = bisect_left(node.keys, key)
        if idx < len(node.keys) and node.keys[idx] == key:
            return None
        node.keys.insert(idx, key)
        if _bplus_leaf_overflow(node):
            return _bplus_split_leaf(node)
        return None

    idx = bisect_right(node.keys, key)
    right = _bplus_insert_into_node(node.children[idx], key)
    if right is not None:
        node.children.insert(idx + 1, right)
    _bplus_refresh_keys(node)
    if _bplus_internal_overflow(node):
        return _bplus_split_internal(node)
    return None


def _get_bplus(tree_type: str, db_id: int) -> BPlusNode | None:
    return _BPLUS_STATE.get(_state_key(tree_type, db_id))


def _set_bplus(tree_type: str, db_id: int, root: BPlusNode | None) -> None:
    _BPLUS_STATE[_state_key(tree_type, db_id)] = root


def _bplus_insert(tree_type: str, db_id: int, key: int) -> BPlusNode:
    root = _get_bplus(tree_type, db_id)
    if root is None:
        root = BPlusNode(keys=[key], leaf=True)
        _set_bplus(tree_type, db_id, root)
        return root

    if _bplus_contains(root, key):
        return root

    right = _bplus_insert_into_node(root, key)
    if right is not None:
        root = BPlusNode(children=[root, right], leaf=False)
        _bplus_refresh_keys(root)

    _set_bplus(tree_type, db_id, root)
    return root


def _bplus_contains(node: BPlusNode | None, key: int) -> bool:
    if node is None:
        return False
    current = node
    while not current.leaf:
        idx = bisect_right(current.keys, key)
        current = current.children[idx]
    idx = bisect_left(current.keys, key)
    return idx < len(current.keys) and current.keys[idx] == key


def _bplus_minimum_ok(node: BPlusNode, is_root: bool) -> bool:
    if is_root:
        return True
    if node.leaf:
        return len(node.keys) >= BPLUS_MIN_LEAF_KEYS
    return len(node.children) >= BPLUS_MIN_INTERNAL_CHILDREN


def _bplus_borrow_from_left(parent: BPlusNode, index: int) -> None:
    child = parent.children[index]
    left = parent.children[index - 1]

    if child.leaf:
        child.keys.insert(0, left.keys.pop())
        _bplus_refresh_keys(parent)
        return

    child.children.insert(0, left.children.pop())
    _bplus_refresh_keys(left)
    _bplus_refresh_keys(child)
    _bplus_refresh_keys(parent)


def _bplus_borrow_from_right(parent: BPlusNode, index: int) -> None:
    child = parent.children[index]
    right = parent.children[index + 1]

    if child.leaf:
        child.keys.append(right.keys.pop(0))
        _bplus_refresh_keys(parent)
        return

    child.children.append(right.children.pop(0))
    _bplus_refresh_keys(right)
    _bplus_refresh_keys(child)
    _bplus_refresh_keys(parent)


def _bplus_merge_children(parent: BPlusNode, index: int) -> None:
    left = parent.children[index]
    right = parent.children[index + 1]

    if left.leaf:
        left.keys.extend(right.keys)
        left.next_leaf = right.next_leaf
    else:
        left.children.extend(right.children)
        _bplus_refresh_keys(left)

    parent.children.pop(index + 1)
    _bplus_refresh_keys(parent)


def _bplus_rebalance_child(parent: BPlusNode, index: int) -> None:
    child = parent.children[index]
    if _bplus_minimum_ok(child, is_root=False):
        _bplus_refresh_keys(parent)
        return

    left_ok = index > 0 and (
        len(parent.children[index - 1].keys) > BPLUS_MIN_LEAF_KEYS
        if child.leaf
        else len(parent.children[index - 1].children) > BPLUS_MIN_INTERNAL_CHILDREN
    )
    right_ok = index < len(parent.children) - 1 and (
        len(parent.children[index + 1].keys) > BPLUS_MIN_LEAF_KEYS
        if child.leaf
        else len(parent.children[index + 1].children) > BPLUS_MIN_INTERNAL_CHILDREN
    )

    if left_ok:
        _bplus_borrow_from_left(parent, index)
        return
    if right_ok:
        _bplus_borrow_from_right(parent, index)
        return

    if index < len(parent.children) - 1:
        _bplus_merge_children(parent, index)
    else:
        _bplus_merge_children(parent, index - 1)


def _bplus_delete_from_node(node: BPlusNode, key: int, is_root: bool = False) -> bool:
    if node.leaf:
        idx = bisect_left(node.keys, key)
        if idx >= len(node.keys) or node.keys[idx] != key:
            return False
        node.keys.pop(idx)
        return True

    idx = bisect_right(node.keys, key)
    removed = _bplus_delete_from_node(node.children[idx], key, is_root=False)
    if not removed:
        return False

    _bplus_rebalance_child(node, idx)
    _bplus_refresh_keys(node)
    return True


def _bplus_delete(tree_type: str, db_id: int, key: int) -> BPlusNode | None:
    root = _get_bplus(tree_type, db_id)
    if root is None:
        return None

    removed = _bplus_delete_from_node(root, key, is_root=True)
    if not removed:
        return root

    if not root.leaf and len(root.children) == 1:
        root = root.children[0]
    elif root.leaf and not root.keys:
        root = None
    else:
        _bplus_refresh_keys(root)

    _set_bplus(tree_type, db_id, root)
    return root


def _bplus_search_path(root: BPlusNode | None, target: int) -> tuple[list[int], bool]:
    path: list[int] = []
    current = root

    while current is not None and not current.leaf:
        idx = bisect_right(current.keys, target)
        if current.keys:
            marker = current.keys[min(max(idx - 1, 0), len(current.keys) - 1)]
            path.append(marker)
        current = current.children[idx]

    if current is None:
        return path, False

    idx = bisect_left(current.keys, target)
    if idx < len(current.keys) and current.keys[idx] == target:
        path.append(current.keys[idx])
        return path, True

    if current.keys:
        path.append(current.keys[min(idx, len(current.keys) - 1)])
    return path, False


def _bplus_traverse(root: BPlusNode | None, method: str) -> list[int]:
    if root is None:
        return []

    mode = method.lower()
    if mode == "bfs":
        order: list[int] = []
        queue: deque[BPlusNode] = deque([root])
        while queue:
            node = queue.popleft()
            order.extend(node.keys)
            for child in node.children:
                queue.append(child)
        return order

    if mode == "dfs":
        order: list[int] = []

        def visit(node: BPlusNode) -> None:
            order.extend(node.keys)
            for child in node.children:
                visit(child)

        visit(root)
        return order

    raise ValueError("Traversal method must be bfs or dfs")


def _bplus_levels(root: BPlusNode | None) -> list[list[list[int]]]:
    if root is None:
        return []
    levels: list[list[list[int]]] = []
    queue: deque[tuple[BPlusNode, int]] = deque([(root, 0)])
    while queue:
        node, depth = queue.popleft()
        if len(levels) <= depth:
            levels.append([])
        levels[depth].append(list(node.keys))
        for child in node.children:
            queue.append((child, depth + 1))
    return levels


def _bplus_leaf_chain(root: BPlusNode | None) -> list[int]:
    if root is None:
        return []
    current = root
    while not current.leaf:
        current = current.children[0]
    chain: list[int] = []
    while current is not None:
        chain.extend(current.keys)
        current = current.next_leaf
    return chain


def _serialize_btree_nodes(root: BTreeNode | None) -> tuple[list[dict[str, Any]], int | None]:
    if root is None:
        return [], None

    nodes: list[dict[str, Any]] = []
    next_id = 1

    def walk(node: BTreeNode, parent_id: int | None = None) -> int:
        nonlocal next_id
        node_id = next_id
        next_id += 1
        child_ids: list[int] = []
        for child in node.children:
            child_ids.append(walk(child, node_id))
        nodes.append(
            {
                "id": node_id,
                "parent_id": parent_id,
                "keys": list(node.keys),
                "child_ids": child_ids,
                "leaf": node.leaf,
            }
        )
        return node_id

    root_id = walk(root)
    nodes.sort(key=lambda item: item["id"])
    return nodes, root_id


def _serialize_bplus_nodes(root: BPlusNode | None) -> tuple[list[dict[str, Any]], int | None]:
    if root is None:
        return [], None

    nodes: list[dict[str, Any]] = []
    next_id = 1

    def walk(node: BPlusNode, parent_id: int | None = None) -> int:
        nonlocal next_id
        node_id = next_id
        next_id += 1
        child_ids: list[int] = []
        for child in node.children:
            child_ids.append(walk(child, node_id))
        nodes.append(
            {
                "id": node_id,
                "parent_id": parent_id,
                "keys": list(node.keys),
                "child_ids": child_ids,
                "leaf": node.leaf,
            }
        )
        return node_id

    root_id = walk(root)
    nodes.sort(key=lambda item: item["id"])
    return nodes, root_id


def _serialize_btree(root: BTreeNode | None) -> dict[str, Any]:
    keys = _btree_traverse(root, "bfs") if root is not None else []
    nodes, root_id = _serialize_btree_nodes(root)
    return {
        "keys": sorted(set(keys)),
        "levels": _btree_levels(root),
        "leaf_chain": [],
        "nodes": nodes,
        "root": root_id,
    }


def _serialize_bplus(root: BPlusNode | None) -> dict[str, Any]:
    keys = _bplus_leaf_chain(root)
    nodes, root_id = _serialize_bplus_nodes(root)
    return {
        "keys": keys,
        "levels": _bplus_levels(root),
        "leaf_chain": keys,
        "nodes": nodes,
        "root": root_id,
    }


def get_tree_state(tree_type: str, db_id: int) -> dict[str, Any]:
    _ensure_supported(tree_type)

    if tree_type in {"avl", "rbtree"}:
        root = _build_balanced_binary_tree(_get_binary_values(tree_type, db_id))
        return {
            "treeType": tree_type,
            "size": len(_get_binary_values(tree_type, db_id)),
            **_serialize_binary_tree(root, tree_type),
        }

    if tree_type == "btree":
        root = _get_btree(tree_type, db_id)
        payload = _serialize_btree(root)
        return {"treeType": tree_type, "size": len(payload["keys"]), **payload}

    root = _get_bplus(tree_type, db_id)
    payload = _serialize_bplus(root)
    return {"treeType": tree_type, "size": len(payload["keys"]), **payload}


def insert_tree_value(tree_type: str, db_id: int, value: int) -> dict[str, Any]:
    _ensure_supported(tree_type)
    target = int(value)
    
    # Get current values for validation
    try:
        if tree_type == "avl":
            current_values = _get_binary_values(tree_type, db_id)
            TreeValidator.validate_avl_insertion([{"vrijednost": v} for v in current_values], target)
        elif tree_type == "rbtree":
            current_values = _get_binary_values(tree_type, db_id)
            TreeValidator.validate_rbtree_insertion([{"vrijednost": v} for v in current_values], target)
        elif tree_type == "btree":
            root = _get_btree(tree_type, db_id)
            if root and _btree_contains(root, target):
                raise ValidationError(f"B-Tree already contains value {target}")
        elif tree_type == "bplustree":
            root = _get_bplus(tree_type, db_id)
            if root and _bplus_contains(root, target):
                raise ValidationError(f"B+ tree already contains value {target}")
    except ValidationError as e:
        raise ValueError(str(e))

    if tree_type in {"avl", "rbtree"}:
        values = _get_binary_values(tree_type, db_id)
        values.append(target)
        _set_binary_values(tree_type, db_id, values)
        return get_tree_state(tree_type, db_id)

    if tree_type == "btree":
        _btree_insert(tree_type, db_id, target)
        return get_tree_state(tree_type, db_id)

    _bplus_insert(tree_type, db_id, target)
    return get_tree_state(tree_type, db_id)


def delete_tree_value(tree_type: str, db_id: int, value: int) -> dict[str, Any]:
    _ensure_supported(tree_type)
    target = int(value)
    
    # Get current state for validation
    current_state = get_tree_state(tree_type, db_id)
    
    # Validate that value exists
    if tree_type in {"avl", "rbtree"}:
        current_values = _get_binary_values(tree_type, db_id)
        if target not in current_values:
            raise ValueError(f"Value {target} not found in {tree_type} tree")
    elif tree_type == "btree":
        root = _get_btree(tree_type, db_id)
        if not _btree_contains(root, target):
            raise ValueError(f"Value {target} not found in B-tree")
    elif tree_type == "bplustree":
        root = _get_bplus(tree_type, db_id)
        if not _bplus_contains(root, target):
            raise ValueError(f"Value {target} not found in B+ tree")

    if tree_type in {"avl", "rbtree"}:
        values = [item for item in _get_binary_values(tree_type, db_id) if item != target]
        _set_binary_values(tree_type, db_id, values)
        return get_tree_state(tree_type, db_id)

    if tree_type == "btree":
        _btree_delete(tree_type, db_id, target)
        return get_tree_state(tree_type, db_id)

    _bplus_delete(tree_type, db_id, target)
    return get_tree_state(tree_type, db_id)


def search_tree_value(tree_type: str, db_id: int, value: int) -> tuple[list[int], bool]:
    _ensure_supported(tree_type)
    target = int(value)

    if tree_type in {"avl", "rbtree"}:
        root = _build_balanced_binary_tree(_get_binary_values(tree_type, db_id))
        return _binary_search_path(root, target)

    if tree_type == "btree":
        return _btree_search_path(_get_btree(tree_type, db_id), target)

    return _bplus_search_path(_get_bplus(tree_type, db_id), target)


def traverse_tree(tree_type: str, db_id: int, method: str) -> list[int]:
    _ensure_supported(tree_type)

    if tree_type in {"avl", "rbtree"}:
        root = _build_balanced_binary_tree(_get_binary_values(tree_type, db_id))
        return _binary_traverse(root, method)

    if tree_type == "btree":
        return _btree_traverse(_get_btree(tree_type, db_id), method)

    return _bplus_traverse(_get_bplus(tree_type, db_id), method)


def reset_tree(tree_type: str, db_id: int) -> dict[str, Any]:
    _ensure_supported(tree_type)

    if tree_type in {"avl", "rbtree"}:
        _set_binary_values(tree_type, db_id, [])
    elif tree_type == "btree":
        _set_btree(tree_type, db_id, None)
    else:
        _set_bplus(tree_type, db_id, None)

    return get_tree_state(tree_type, db_id)
