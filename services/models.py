from dataclasses import dataclass


@dataclass(slots=True)
class AdtState:
    label: str
    hash_rows: list[dict]
    recursion_rows: list[dict]
    opce_rows: list[dict]
    bst_rows: list[dict]
    stack_queue_rows: list[dict]
    opce_tree: list[str]
    bst_tree: list[str]