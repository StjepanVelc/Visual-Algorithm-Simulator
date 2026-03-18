"""Layout calculation for tree rendering on canvas."""

from collections import defaultdict


def build_general_tree_layout(rows: list[dict]) -> tuple[dict[int, tuple[float, int]], list[tuple[int, int]]]:
    """Calculate layout positions for general tree nodes."""
    if not rows:
        return {}, []

    nodes = {row["id"]: row for row in rows}
    children: dict[int, list[int]] = defaultdict(list)
    roots: list[int] = []
    edges: list[tuple[int, int]] = []

    for row in rows:
        parent_id = row["parent_id"]
        node_id = row["id"]
        if parent_id is None:
            roots.append(node_id)
        else:
            children[parent_id].append(node_id)
            edges.append((parent_id, node_id))

    def sort_key(node_id: int) -> tuple[int, int]:
        redoslijed = nodes[node_id].get("redoslijed")
        return (redoslijed if redoslijed is not None else 0, node_id)

    for parent_id in children:
        children[parent_id].sort(key=sort_key)
    roots.sort(key=sort_key)

    positions: dict[int, tuple[float, int]] = {}
    next_x = [0]

    def dfs(node_id: int, depth: int) -> float:
        child_ids = children.get(node_id, [])
        if not child_ids:
            x = float(next_x[0])
            next_x[0] += 1
            positions[node_id] = (x, depth)
            return x

        child_x = [dfs(child_id, depth + 1) for child_id in child_ids]
        x = sum(child_x) / len(child_x)
        positions[node_id] = (x, depth)
        return x

    for root_id in roots:
        dfs(root_id, 0)

    return positions, edges


def build_bst_layout(rows: list[dict]) -> tuple[dict[int, tuple[float, int]], list[tuple[int, int]]]:
    """Calculate layout positions for BST nodes."""
    if not rows:
        return {}, []

    nodes = {row["id"]: row for row in rows}
    root_id = next((row["id"] for row in rows if row["parent_id"] is None), None)
    if root_id is None:
        return {}, []

    positions: dict[int, tuple[float, int]] = {}
    edges: list[tuple[int, int]] = []
    next_x = [0]

    def dfs(node_id: int, depth: int) -> float:
        node = nodes[node_id]
        child_x: list[float] = []
        left_id = node.get("lijevi_id")
        right_id = node.get("desni_id")

        if left_id is not None and left_id in nodes:
            edges.append((node_id, left_id))
            child_x.append(dfs(left_id, depth + 1))

        if right_id is not None and right_id in nodes:
            edges.append((node_id, right_id))
            child_x.append(dfs(right_id, depth + 1))

        if child_x:
            x = sum(child_x) / len(child_x)
        else:
            x = float(next_x[0])
            next_x[0] += 1

        positions[node_id] = (x, depth)
        return x

    dfs(root_id, 0)
    return positions, edges
