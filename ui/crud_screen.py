# ui/crud_screen.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel,
    QTableWidget, QTableWidgetItem, QAbstractItemView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from datetime import datetime

from database.connection import get_db_connection, close_db_connection
from ui.widgets.popups import show_warning, confirm_action
from ui.widgets.styles import style_button, LINEEDIT_STYLE, TABLE_STYLE


# ---------------- Numeric item for proper numeric sorting and formatted display ----------------
class NumericTableWidgetItem(QTableWidgetItem):
    def __init__(self, value, display_text=None):
        try:
            self.value = float(value)
        except (ValueError, TypeError):
            self.value = 0.0

        self.display_text = display_text if display_text is not None else str(value)
        super().__init__(self.display_text)

    def __lt__(self, other):
        if isinstance(other, NumericTableWidgetItem):
            return self.value < other.value
        return super().__lt__(other)

    def text(self):
        # Ensures QTableWidget always shows formatted display text
        return self.display_text


# ---------------- CRUD Screen ----------------
class CrudScreen(QWidget):
    SCHEMA_NUMERIC_COLS = {
        "customer": ["customer_id", "is_active"],
        "seller": ["seller_id", "is_active"],
        "inventory": ["inventory_id", "seller_id", "purchase_price", "price_tag", "sold", "is_active"],
        "sales": ["sale_id", "inventory_id", "customer_id", "sale_price", "is_active"]
    }

    PRICE_FIELDS = {
        "inventory": ["purchase_price", "price_tag"],
        "sales": ["sale_price"]
    }

    DATE_FIELDS = {
        "inventory": ["purchase_date"],
        "sales": ["sale_date"]
    }

    def __init__(self, table_name: str, headers: list, form_class, query: str = None):
        super().__init__()
        self.table_name = table_name
        self.headers = headers
        self.form_class = form_class
        self.query = query

        # normalize column names for consistent comparison
        self.numeric_cols = set([col.lower() for col in self.SCHEMA_NUMERIC_COLS.get(self.table_name, [])])
        self.price_cols = set([col.lower() for col in self.PRICE_FIELDS.get(self.table_name, [])])
        self.date_cols = set([col.lower() for col in self.DATE_FIELDS.get(self.table_name, [])])

        self.init_ui()
        self.refresh_data()

    # ---------------- UI ----------------
    def init_ui(self):
        layout = QVBoxLayout(self)

        # Toolbar
        toolbar = QHBoxLayout()
        self.add_btn = QPushButton("Add")
        self.edit_btn = QPushButton("Edit")
        self.delete_btn = QPushButton("Delete")
        self.refresh_btn = QPushButton("Refresh")

        for btn, color in [
            (self.add_btn, "#27ae60"),
            (self.edit_btn, "#2980b9"),
            (self.delete_btn, "#c0392b"),
            (self.refresh_btn, "#7f8c8d")
        ]:
            style_button(btn, color)
            toolbar.addWidget(btn)

        toolbar.addStretch()
        toolbar.addWidget(QLabel("Search:"))

        self.search_box = QLineEdit()
        self.search_box.setFixedWidth(220)
        self.search_box.setStyleSheet(LINEEDIT_STYLE)
        toolbar.addWidget(self.search_box)

        layout.addLayout(toolbar)

        # Table
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setStyleSheet(TABLE_STYLE)
        layout.addWidget(self.table)

        # Signals
        self.add_btn.clicked.connect(self.add_item)
        self.edit_btn.clicked.connect(self.edit_item)
        self.delete_btn.clicked.connect(self.delete_item)
        self.refresh_btn.clicked.connect(self.refresh_data)
        self.search_box.textChanged.connect(self.search_items)

    # ---------------- Load Data ----------------
    def load_data(self):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            if self.query:
                cursor.execute(self.query)
            else:
                cursor.execute(f"SELECT * FROM {self.table_name} ORDER BY {self.table_name}_id")
            rows = cursor.fetchall()
        finally:
            close_db_connection(conn)

        self.table.setSortingEnabled(False)
        self.table.clearContents()
        self.table.setRowCount(len(rows))
        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)

        default_font = QFont("Arial", 12)
        header_lower = [h.lower().replace(" ", "_") for h in self.headers]

        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                col_name = header_lower[c]

                # ---------------- Numeric/boolean fields ----------------
                if col_name in self.numeric_cols:
                    item = NumericTableWidgetItem(val)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # ---------------- Price fields ----------------
                elif col_name in self.price_cols and val is not None:
                    display_val = f"₹{float(val):.2f}"
                    item = NumericTableWidgetItem(val, display_text=display_val)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # ---------------- Date fields ----------------
                elif col_name in self.date_cols and val is not None:
                    try:
                        date_obj = datetime.strptime(str(val), "%Y-%m-%d")
                        display_val = date_obj.strftime("%-d-%b-%Y")
                    except Exception:
                        display_val = str(val)
                    item = QTableWidgetItem(display_val)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # ---------------- Other fields ----------------
                else:
                    item = QTableWidgetItem("" if val is None else str(val))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

                item.setFont(default_font)
                self.table.setItem(r, c, item)

            # Highlight inactive rows
            for inactive_col in ("active", "is_active"):
                if inactive_col in header_lower:
                    idx = header_lower.index(inactive_col)
                    if row[idx] == 0:
                        for c2 in range(len(row)):
                            item = self.table.item(r, c2)
                            if item:
                                item.setBackground(Qt.GlobalColor.lightGray)

        self.table.setSortingEnabled(True)
        self.table.resizeColumnsToContents()

    # ---------------- Refresh ----------------
    def refresh_data(self):
        self.load_data()

    # ---------------- CRUD ----------------
    def add_item(self):
        dialog = self.form_class()
        if dialog.exec():
            self.refresh_data()

    def edit_item(self):
        row = self.table.currentRow()
        if row < 0:
            show_warning(self, f"Select a {self.table_name} first")
            return
        item = self.table.item(row, 0)
        if not item:
            show_warning(self, "Selected row has no ID")
            return
        item_id = int(item.text())
        dialog = self.form_class(item_id)
        if dialog.exec():
            self.refresh_data()

    def delete_item(self):
        row = self.table.currentRow()
        if row < 0:
            show_warning(self, f"Select a {self.table_name} to delete")
            return
        item = self.table.item(row, 0)
        if not item:
            show_warning(self, "Selected row has no ID")
            return
        item_id = int(item.text())
        if confirm_action(self, f"Delete {self.table_name} ID {item_id}?"):
            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(f"DELETE FROM {self.table_name} WHERE {self.table_name}_id = ?", (item_id,))
                conn.commit()
            finally:
                close_db_connection(conn)
            self.refresh_data()

    # ---------------- Search ----------------
    def search_items(self):
        text = self.search_box.text().lower()
        for r in range(self.table.rowCount()):
            show = False
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                if item and text in item.text().lower():
                    show = True
                    break
            self.table.setRowHidden(r, not show)