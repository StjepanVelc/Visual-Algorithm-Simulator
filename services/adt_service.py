from pathlib import Path

from data.hash_repository import (
    add_hash_node as repo_add_hash_node,
    delete_hash_node as repo_delete_hash_node,
    fetch_hash_rows,
    update_hash_node as repo_update_hash_node,
)
from data.io_repository import export_sql as repo_export_sql, import_sql as repo_import_sql
from data.linear_repository import fetch_stack_queue_rows
from data.recursion_repository import (
    add_recursion_call as repo_add_recursion_call,
    delete_recursion_call as repo_delete_recursion_call,
    fetch_recursion_rows,
    update_recursion_call as repo_update_recursion_call,
)
from data.schema import build_db
from data.tree_repository import (
    add_bst_node as repo_add_bst_node,
    add_general_tree_node as repo_add_general_tree_node,
    delete_bst_node as repo_delete_bst_node,
    delete_general_tree_node as repo_delete_general_tree_node,
    fetch_bst_rows,
    fetch_general_tree_rows,
    insert_bst_node_auto as repo_insert_bst_node_auto,
    update_bst_node_value as repo_update_bst_node_value,
    update_general_tree_node as repo_update_general_tree_node,
)
from services.models import AdtState
from services.reporting import build_html_report, build_state
from services.validation_service import TreeValidator, ValidationError


def build_database(db_path: Path) -> None:
    build_db(db_path)


def collect_state(db_path: Path, label: str) -> AdtState:
    return build_state(
        label=label,
        hash_rows=fetch_hash_rows(db_path),
        recursion_rows=fetch_recursion_rows(db_path),
        opce_rows=fetch_general_tree_rows(db_path),
        bst_rows=fetch_bst_rows(db_path),
        stack_queue_rows=fetch_stack_queue_rows(db_path),
    )


def add_hash_node(db_path: Path, bucket_index: int, key: str, value: str) -> int:
    return repo_add_hash_node(db_path, bucket_index, key, value)


def update_hash_node(db_path: Path, node_id: int, key: str, value: str) -> None:
    repo_update_hash_node(db_path, node_id, key, value)


def delete_hash_node(db_path: Path, node_id: int) -> None:
    repo_delete_hash_node(db_path, node_id)


def add_recursion_call(
    db_path: Path,
    oznaka: str,
    funkcija: str,
    argument: str,
    povrat: str | None,
    parent_id: int | None,
) -> int:
    return repo_add_recursion_call(db_path, oznaka, funkcija, argument, povrat, parent_id)


def update_recursion_call(
    db_path: Path,
    call_id: int,
    oznaka: str,
    funkcija: str,
    argument: str,
    povrat: str | None,
    parent_id: int | None,
) -> None:
    repo_update_recursion_call(db_path, call_id, oznaka, funkcija, argument, povrat, parent_id)


def delete_recursion_call(db_path: Path, call_id: int) -> None:
    repo_delete_recursion_call(db_path, call_id)


def add_general_tree_node(
    db_path: Path,
    vrijednost: str,
    parent_id: int | None,
    redoslijed: int | None,
) -> int:
    # Validate before adding
    state = collect_state(db_path, "temp")
    try:
        value = int(vrijednost)
        TreeValidator.validate_general_tree_insertion(state.opce_rows, value, parent_id)
    except (ValueError, ValidationError) as e:
        raise ValueError(str(e))
    
    return repo_add_general_tree_node(db_path, vrijednost, parent_id, redoslijed)


def update_general_tree_node(
    db_path: Path,
    node_id: int,
    vrijednost: str,
    parent_id: int | None,
    redoslijed: int | None,
) -> None:
    repo_update_general_tree_node(db_path, node_id, vrijednost, parent_id, redoslijed)


def delete_general_tree_node(db_path: Path, node_id: int) -> None:
    repo_delete_general_tree_node(db_path, node_id)


def add_bst_node(db_path: Path, vrijednost: str, parent_id: int, side: str) -> int:
    return repo_add_bst_node(db_path, vrijednost, parent_id, side)


def insert_bst_node_auto(db_path: Path, vrijednost: str) -> dict:
    # Validate before inserting
    state = collect_state(db_path, "temp")
    try:
        value = int(vrijednost)
        TreeValidator.validate_bst_insertion(state.bst_rows, value)
    except (ValueError, ValidationError) as e:
        raise ValueError(str(e))
    
    return repo_insert_bst_node_auto(db_path, vrijednost)


def update_bst_node_value(db_path: Path, node_id: int, vrijednost: str) -> None:
    repo_update_bst_node_value(db_path, node_id, vrijednost)


def delete_bst_node(db_path: Path, node_id: int) -> None:
    repo_delete_bst_node(db_path, node_id)


def export_sql(db_path: Path, sql_path: Path) -> None:
    repo_export_sql(db_path, sql_path)


def import_sql(db_path: Path, sql_path: Path, replace: bool = True) -> None:
    repo_import_sql(db_path, sql_path, replace)


def generate_report(db_path: Path, report_dir: Path) -> Path:
    current_state = collect_state(db_path, "trenutno")

    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "stabla.html"
    build_html_report([current_state], report_path)
    return report_path
