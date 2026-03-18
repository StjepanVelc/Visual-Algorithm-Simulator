import html
from pathlib import Path

from services.models import AdtState


def build_general_tree_lines(rows: list[dict]) -> list[str]:
    if not rows:
        return []

    nodes = {row["id"]: row for row in rows}
    children: dict[int, list[int]] = {}
    roots: list[int] = []

    for row in rows:
        parent_id = row["parent_id"]
        if parent_id is None:
            roots.append(row["id"])
        else:
            children.setdefault(parent_id, []).append(row["id"])

    def sort_key(node_id: int) -> tuple[int, int]:
        node = nodes[node_id]
        redoslijed = node["redoslijed"]
        return ((redoslijed if redoslijed is not None else 0), node_id)

    lines: list[str] = []

    def walk(node_id: int, prefix: str) -> None:
        node = nodes[node_id]
        lines.append(f"{prefix}{node['vrijednost']}")
        for child_id in sorted(children.get(node_id, []), key=sort_key):
            walk(child_id, prefix + "  ")

    for root_id in sorted(roots, key=sort_key):
        walk(root_id, "")

    return lines


def build_bst_tree_lines(rows: list[dict]) -> list[str]:
    if not rows:
        return []

    nodes = {row["id"]: row for row in rows}
    root_id = next((row["id"] for row in rows if row["parent_id"] is None), None)
    if root_id is None:
        return []

    lines: list[str] = []

    def walk(node_id: int, prefix: str, label: str) -> None:
        node = nodes[node_id]
        lines.append(f"{prefix}{label}{node['vrijednost']}")
        child_prefix = prefix + "  "
        left_id = node["lijevi_id"]
        right_id = node["desni_id"]
        if left_id is not None:
            walk(left_id, child_prefix, "L-")
        if right_id is not None:
            walk(right_id, child_prefix, "R-")

    walk(root_id, "", "")
    return lines


def build_state(
    label: str,
    hash_rows: list[dict],
    recursion_rows: list[dict],
    opce_rows: list[dict],
    bst_rows: list[dict],
    stack_queue_rows: list[dict],
) -> AdtState:
    return AdtState(
        label=label,
        hash_rows=hash_rows,
        recursion_rows=recursion_rows,
        opce_rows=opce_rows,
        bst_rows=bst_rows,
        stack_queue_rows=stack_queue_rows,
        opce_tree=build_general_tree_lines(opce_rows),
        bst_tree=build_bst_tree_lines(bst_rows),
    )


def html_table(title: str, rows: list[dict]) -> str:
    safe_title = html.escape(title)
    if not rows:
        return f"<h3>{safe_title}</h3><p>Nema podataka.</p>"

    headers = list(rows[0].keys())
    header_html = "".join(f"<th>{html.escape(str(header))}</th>" for header in headers)
    body_rows = []
    for row in rows:
        cells = "".join(f"<td>{html.escape(str(row.get(header, '')))}</td>" for header in headers)
        body_rows.append(f"<tr>{cells}</tr>")

    body_html = "".join(body_rows)
    return (
        f"<h3>{safe_title}</h3>"
        "<table>"
        f"<thead><tr>{header_html}</tr></thead>"
        f"<tbody>{body_html}</tbody>"
        "</table>"
    )


def html_pre(title: str, lines: list[str]) -> str:
    safe_title = html.escape(title)
    content = "\n".join(html.escape(line) for line in lines) if lines else "(nema podataka)"
    return f"<h3>{safe_title}</h3><pre>{content}</pre>"


def build_html_report(states: list[AdtState], output_path: Path) -> None:
    sections = []
    for state in states:
        label = html.escape(state.label)
        sections.append(f"<h2>Stanje: {label}</h2>")
        sections.append(html_table("Hash tablica - bucket lanci", state.hash_rows))
        sections.append(html_table("Rekurzija - stablo poziva", state.recursion_rows))
        sections.append(html_table("Opce stablo - roditelj/dijete", state.opce_rows))
        sections.append(html_pre("Opce stablo - prikaz", state.opce_tree))
        sections.append(html_table("BST - cvorovi", state.bst_rows))
        sections.append(html_pre("BST - prikaz", state.bst_tree))
        sections.append(html_table("Stog i red - elementi", state.stack_queue_rows))

    html_doc = (
        "<!DOCTYPE html>"
        "<html lang=\"hr\">"
        "<head>"
        "<meta charset=\"utf-8\">"
        "<title>ADT izvjestaj</title>"
        "<style>"
        "body{font-family:Arial, sans-serif; margin:24px; color:#1b1b1b;}"
        "h1{margin-bottom:8px;} h2{margin-top:32px;}"
        "table{border-collapse:collapse; width:100%; margin:8px 0 16px;}"
        "th,td{border:1px solid #ccc; padding:6px 8px; text-align:left;}"
        "th{background:#f2f2f2;}"
        "pre{background:#f8f8f8; padding:12px; border:1px solid #ddd;}"
        "</style>"
        "</head>"
        "<body>"
        "<h1>ADT izvjestaj</h1>"
        + "".join(sections)
        + "</body></html>"
    )

    output_path.write_text(html_doc, encoding="utf-8")
