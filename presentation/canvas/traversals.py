"""Tree traversal algorithms for visualization."""

from collections import defaultdict


def build_bst_traversal_order(rows: list[dict], mode: str, search_value: str | None = None) -> list[int]:
    """Build traversal order for BST based on mode (BFS, DFS, or Search)."""
    nodes = {int(row["id"]): row for row in rows}
    root_id = next((int(row["id"]) for row in rows if row.get("parent_id") is None), None)
    if root_id is None:
        return []

    if mode == "BFS":
        order: list[int] = []
        queue = [root_id]
        while queue:
            node_id = queue.pop(0)
            order.append(node_id)
            node = nodes[node_id]
            if node.get("lijevi_id") is not None and int(node["lijevi_id"]) in nodes:
                queue.append(int(node["lijevi_id"]))
            if node.get("desni_id") is not None and int(node["desni_id"]) in nodes:
                queue.append(int(node["desni_id"]))
        return order

    if mode == "DFS":
        order = []

        def dfs(node_id: int) -> None:
            order.append(node_id)
            node = nodes[node_id]
            if node.get("lijevi_id") is not None and int(node["lijevi_id"]) in nodes:
                dfs(int(node["lijevi_id"]))
            if node.get("desni_id") is not None and int(node["desni_id"]) in nodes:
                dfs(int(node["desni_id"]))

        dfs(root_id)
        return order

    if mode == "BST Search" and search_value is not None:
        def cmp_key(value: str) -> tuple[int, float | str]:
            try:
                return (0, float(value))
            except (TypeError, ValueError):
                return (1, str(value))

        target = cmp_key(search_value)
        order = []
        current = root_id
        while True:
            node = nodes.get(current)
            if node is None:
                break
            order.append(current)
            node_key = cmp_key(str(node.get("vrijednost", "")))
            if node_key == target:
                break
            if target < node_key:
                left = node.get("lijevi_id")
                if left is None:
                    break
                current = int(left)
            else:
                right = node.get("desni_id")
                if right is None:
                    break
                current = int(right)
        return order

    return []


def build_general_traversal_order(rows: list[dict], mode: str) -> list[int]:
    """Build traversal order for general tree based on mode (BFS or DFS)."""
    nodes = {int(row["id"]): row for row in rows}
    children: dict[int, list[int]] = defaultdict(list)
    roots: list[int] = []

    for row in rows:
        node_id = int(row["id"])
        parent_id = row.get("parent_id")
        if parent_id is None:
            roots.append(node_id)
        else:
            children[int(parent_id)].append(node_id)

    def sort_key(node_id: int) -> tuple[int, int]:
        red = nodes[node_id].get("redoslijed")
        return (int(red) if red is not None else 0, node_id)

    roots.sort(key=sort_key)
    for parent_id in children:
        children[parent_id].sort(key=sort_key)

    if mode == "BFS":
        order: list[int] = []
        queue = roots[:]
        while queue:
            node_id = queue.pop(0)
            order.append(node_id)
            queue.extend(children.get(node_id, []))
        return order

    if mode == "DFS":
        order: list[int] = []

        def dfs(node_id: int) -> None:
            order.append(node_id)
            for child_id in children.get(node_id, []):
                dfs(child_id)

        for root_id in roots:
            dfs(root_id)
        return order

    return []
