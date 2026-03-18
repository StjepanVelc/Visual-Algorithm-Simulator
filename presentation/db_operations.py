"""Database operations (create, export, import, report generation)."""

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

from services.adt_service import build_database, export_sql, generate_report, import_sql
from presentation.utils import resolve_paths, ensure_db


def on_build_db() -> None:
    """Create a new database."""
    db_path, _ = resolve_paths()
    build_database(db_path)
    messagebox.showinfo("ADT", f"Database created: {db_path}")


def on_generate_report() -> None:
    """Generate HTML report."""
    db_path, report_dir = resolve_paths()
    if not db_path.exists():
        messagebox.showwarning("ADT", "Database does not exist. Create it first.")
        return

    report_path = generate_report(db_path, report_dir)
    messagebox.showinfo("ADT", f"HTML report for current state: {report_path}")


def on_export_sql() -> None:
    """Export database to SQL file."""
    db_path = ensure_db()
    if not db_path:
        return

    sql_path = filedialog.asksaveasfilename(
        title="Save SQL",
        defaultextension=".sql",
        filetypes=[("SQL", "*.sql")],
    )
    if not sql_path:
        return

    export_sql(db_path, Path(sql_path))
    messagebox.showinfo("ADT", f"SQL saved: {sql_path}")


def on_import_sql() -> None:
    """Import database from SQL file."""
    db_path, _ = resolve_paths()
    sql_path = filedialog.askopenfilename(
        title="Load SQL",
        filetypes=[("SQL", "*.sql")],
    )
    if not sql_path:
        return

    import_sql(db_path, Path(sql_path), replace=True)
    messagebox.showinfo("ADT", f"SQL loaded into database: {db_path}")
