import sys
import tempfile
import unittest
from pathlib import Path

DATABASE_DIR = Path(__file__).resolve().parents[1]
if str(DATABASE_DIR) not in sys.path:
    sys.path.insert(0, str(DATABASE_DIR))

from services.adt_service import (  # noqa: E402
    add_bst_node,
    add_general_tree_node,
    add_hash_node,
    add_recursion_call,
    build_database,
    collect_state,
    delete_hash_node,
    delete_recursion_call,
    export_sql,
    generate_report,
    import_sql,
    update_bst_node_value,
    update_general_tree_node,
    update_hash_node,
    update_recursion_call,
)


class AdtServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)
        self.db_path = self.base_path / "adt.db"
        self.report_dir = self.base_path / "izvjestaji"
        build_database(self.db_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_generate_report_does_not_modify_database_state(self) -> None:
        before_state = collect_state(self.db_path, "prije")

        report_path = generate_report(self.db_path, self.report_dir)

        after_state = collect_state(self.db_path, "poslije")
        self.assertTrue(report_path.exists())
        self.assertEqual(before_state.hash_rows, after_state.hash_rows)
        self.assertEqual(before_state.recursion_rows, after_state.recursion_rows)
        self.assertEqual(before_state.opce_rows, after_state.opce_rows)
        self.assertEqual(before_state.bst_rows, after_state.bst_rows)
        self.assertEqual(before_state.stack_queue_rows, after_state.stack_queue_rows)

    def test_add_hash_node_rejects_invalid_bucket(self) -> None:
        with self.assertRaises(ValueError):
            add_hash_node(self.db_path, 99, "x", "1")

    def test_add_general_tree_node_rejects_missing_parent(self) -> None:
        with self.assertRaises(ValueError):
            add_general_tree_node(self.db_path, "Novi", 9999, 0)

    def test_add_bst_node_rejects_occupied_side(self) -> None:
        with self.assertRaises(ValueError):
            add_bst_node(self.db_path, "11", 11, "L")

    def test_hash_node_update_and_delete(self) -> None:
        new_id = add_hash_node(self.db_path, 0, "abc", "1")
        update_hash_node(self.db_path, new_id, "abc2", "2")
        state_after_update = collect_state(self.db_path, "nakon-update")
        self.assertTrue(any(row["cvor_id"] == new_id and row["kljuc"] == "abc2" for row in state_after_update.hash_rows))

        delete_hash_node(self.db_path, new_id)
        state_after_delete = collect_state(self.db_path, "nakon-delete")
        self.assertFalse(any(row["cvor_id"] == new_id for row in state_after_delete.hash_rows))

    def test_recursion_update_and_delete(self) -> None:
        new_id = add_recursion_call(self.db_path, "x", "fib", "8", None, None)
        update_recursion_call(self.db_path, new_id, "x1", "fib", "8", "21", None)
        state_after_update = collect_state(self.db_path, "nakon-update")
        self.assertTrue(any(row["id"] == new_id and row["oznaka"] == "x1" for row in state_after_update.recursion_rows))

        delete_recursion_call(self.db_path, new_id)
        state_after_delete = collect_state(self.db_path, "nakon-delete")
        self.assertFalse(any(row["id"] == new_id for row in state_after_delete.recursion_rows))

    def test_tree_update_variants(self) -> None:
        update_general_tree_node(self.db_path, 1, "CEO-UPDATED", None, 0)
        update_bst_node_value(self.db_path, 11, "80")
        state = collect_state(self.db_path, "nakon-tree-update")
        self.assertTrue(any(row["id"] == 1 and row["vrijednost"] == "CEO-UPDATED" for row in state.opce_rows))
        self.assertTrue(any(row["id"] == 11 and row["vrijednost"] == "80" for row in state.bst_rows))

    def test_export_import_roundtrip(self) -> None:
        sql_path = self.base_path / "backup.sql"
        export_sql(self.db_path, sql_path)
        self.assertTrue(sql_path.exists())

        second_db = self.base_path / "restored.db"
        import_sql(second_db, sql_path, replace=True)

        original_state = collect_state(self.db_path, "original")
        restored_state = collect_state(second_db, "restored")
        self.assertEqual(original_state.hash_rows, restored_state.hash_rows)
        self.assertEqual(original_state.recursion_rows, restored_state.recursion_rows)
        self.assertEqual(original_state.opce_rows, restored_state.opce_rows)
        self.assertEqual(original_state.bst_rows, restored_state.bst_rows)


if __name__ == "__main__":
    unittest.main()