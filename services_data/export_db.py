import pandas as pd
from PySide6.QtWidgets import QMessageBox
from database.connection import get_db_connection, close_db_connection
from config.logger import log
from config.paths import BIHONGANA_XLSX

def export_database(parent_widget):
    """
    Export all tables to a single XLSX file at BIHONGANA_XLSX.
    Excludes *_id, created_at, updated_at, is_active columns.
    For inventory table, replaces seller_id with seller's unique_name as shop_name.
    """
    try:
        file_path = str(BIHONGANA_XLSX)
        conn = get_db_connection()
        c = conn.cursor()

        # Get all table names
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in c.fetchall()]

        if not tables:
            QMessageBox.warning(parent_widget, "Export Database", "No tables found in database")
            return

        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            for table in tables:
                c.execute(f"PRAGMA table_info({table})")
                columns_info = c.fetchall()
                all_cols = [col[1] for col in columns_info]

                if table == "inventory":
                    # Keep inventory columns except ids, timestamps, is_active, seller_id
                    keep_cols = [
                        col for col in all_cols
                        if not (col.lower().endswith("_id") or col in ("created_at", "updated_at", "is_active", "seller_id"))
                    ]
                    # Fully qualify inventory columns with i.
                    select_cols = ", ".join([f"i.{col}" for col in keep_cols])
                    # Add seller unique_name
                    query = f"""
                        SELECT {select_cols}, s.unique_name AS shop_name
                        FROM inventory i
                        LEFT JOIN seller s ON i.seller_id = s.seller_id
                    """
                    df = pd.read_sql_query(query, conn)

                    # Move shop_name to the end or start as desired
                    df = df[['shop_name'] + [col for col in df.columns if col != 'shop_name']]

                else:
                    # Other tables: exclude *_id, timestamps, is_active
                    keep_cols = [
                        col for col in all_cols
                        if not (col.lower().endswith("_id") or col in ("created_at", "updated_at", "is_active"))
                    ]
                    if not keep_cols:
                        log(f"⚠️ Skipping table '{table}' (no columns to export)")
                        continue
                    select_cols = ", ".join(keep_cols)
                    df = pd.read_sql_query(f"SELECT {select_cols} FROM {table}", conn)

                df.to_excel(writer, sheet_name=table, index=False)

        close_db_connection(conn)
        QMessageBox.information(parent_widget, "Export Database",
                                f"Database exported successfully to:\n{file_path}")
        log(f"🎉 Database exported successfully to '{file_path}'")

    except Exception as e:
        log(f"❌ Failed to export database: {e}")
        close_db_connection(conn)
        QMessageBox.critical(parent_widget, "Export Database", f"Export failed:\n{e}")