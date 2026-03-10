# from PySide6.QtWidgets import (
#     QWidget, QVBoxLayout, QLabel, QComboBox, QTableWidget, QTableWidgetItem, 
#     QHeaderView, QFrame, QSpacerItem, QSizePolicy
# )
# from PySide6.QtCore import Qt
# from database.connection import get_db_connection, close_db_connection
# from ui.widgets.styles import TABLE_STYLE

# class ReportingScreen(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Reports")
#         self.resize(1000, 700)

#         main_layout = QVBoxLayout(self)
#         main_layout.setSpacing(12)
#         main_layout.setContentsMargins(20, 20, 20, 20)

#         # Title
#         title = QLabel("Reports & Analytics")
#         title.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         title.setStyleSheet("font-size:28px; font-weight:700; color:#2c3e50;")
#         main_layout.addWidget(title)

#         # ---------------- Dropdown Wrapper ----------------
#         dropdown_frame = QFrame()
#         dropdown_layout = QVBoxLayout(dropdown_frame)
#         dropdown_layout.setContentsMargins(0, 0, 0, 0)
#         dropdown_layout.setSpacing(6)
#         dropdown_label = QLabel("Select Report Type:")
#         self.report_selector = QComboBox()
#         self.report_selector.addItems([
#             "Select Report",
#             "Expense Vs Inventory Comparison",
#             "Available Inventory Data"
#         ])
#         self.report_selector.setStyleSheet("""
#             QComboBox { font-size: 14px; padding: 6px; min-height:28px; }
#         """)
#         self.report_selector.currentIndexChanged.connect(self.load_report_by_index)
#         dropdown_layout.addWidget(dropdown_label)
#         dropdown_layout.addWidget(self.report_selector)
#         main_layout.addWidget(dropdown_frame)

#         # ---------------- Create Table Frames ----------------
#         self.table_wrappers = {}
#         self._create_table_wrapper("Expense Breakdown", main_layout)
#         self._create_table_wrapper("Inventory Purchase", main_layout)
#         self._create_table_wrapper("Available Inventory", main_layout)

#         # Add a vertical spacer at the bottom to keep dropdown at top
#         spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
#         main_layout.addItem(spacer)

#         # Hide all tables initially
#         self._hide_all_tables()

#     def _create_table_wrapper(self, label_text, parent_layout):
#         frame = QFrame()
#         frame.setStyleSheet("QFrame { border: 1px solid #e4e7ea; border-radius: 6px; background: #fff; }")
#         layout = QVBoxLayout(frame)
#         layout.setContentsMargins(10, 10, 10, 10)
#         layout.setSpacing(6)

#         label = QLabel(f"{label_text} Rows: 0")
#         label.setStyleSheet("font-weight:600; font-size:13px; color:#2c3e50;")
#         table = QTableWidget()
#         table.setAlternatingRowColors(True)
#         table.setStyleSheet(TABLE_STYLE)
#         table.horizontalHeader().setStretchLastSection(True)
#         table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
#         table.verticalHeader().setVisible(False)

#         layout.addWidget(label)
#         layout.addWidget(table)

#         parent_layout.addWidget(frame)
#         self.table_wrappers[label_text] = {"frame": frame, "label": label, "table": table}
#         frame.hide()

#     def _hide_all_tables(self):
#         for wrapper in self.table_wrappers.values():
#             wrapper["frame"].hide()

#     def load_report_by_index(self, index):
#         self._hide_all_tables()
#         if index == 0:
#             return

#         conn = get_db_connection()
#         cursor = conn.cursor()
#         try:
#             if index == 1:
#                 cursor.execute("""
#                     SELECT
#                         s.unique_name AS Seller,
#                         COALESCE(inv.total_purchase, 0) AS Inventory_Total,
#                         COALESCE(exp.total_expense, 0) AS Expense_Total,
#                         (COALESCE(exp.total_expense, 0) - COALESCE(inv.total_purchase, 0)) AS Difference
#                     FROM seller s
#                     LEFT JOIN (
#                         SELECT seller_id, SUM(purchase_price) AS total_purchase
#                         FROM inventory
#                         GROUP BY seller_id
#                     ) inv ON inv.seller_id = s.seller_id
#                     LEFT JOIN (
#                         SELECT UPPER(payee_name) AS payee, SUM(amount) AS total_expense
#                         FROM expense
#                         WHERE UPPER(expense_type) = 'GARMENTS'
#                         GROUP BY UPPER(payee_name)
#                     ) exp ON exp.payee = UPPER(s.unique_name)
#                     WHERE (COALESCE(exp.total_expense,0) - COALESCE(inv.total_purchase,0)) != 0
#                     ORDER BY s.unique_name
#                 """)
#                 headers = ["Seller", "Inventory Total", "Expense Total", "Difference"]
#                 rows = cursor.fetchall()
#                 self.populate_table(self.table_wrappers["Expense Breakdown"]["table"],
#                                     self.table_wrappers["Expense Breakdown"]["label"],
#                                     headers, rows, currency_cols=[1,2,3])
#                 self.table_wrappers["Expense Breakdown"]["frame"].show()

#             elif index == 2:
#                 cursor.execute("""
#                     SELECT type, item_description, material, size, purchase_price, price_tag
#                     FROM inventory
#                     WHERE sold = 0
#                     ORDER BY inventory_id
#                 """)
#                 headers = ["Type", "Description", "Material", "Size", "Purchase Price", "Price Tag"]
#                 rows = cursor.fetchall()
#                 self.populate_table(self.table_wrappers["Available Inventory"]["table"],
#                                     self.table_wrappers["Available Inventory"]["label"],
#                                     headers, rows, currency_cols=[4,5])
#                 self.table_wrappers["Available Inventory"]["frame"].show()
#         finally:
#             close_db_connection(conn)

#     def populate_table(self, table_widget, label, headers, rows, currency_cols=None):
#         if currency_cols is None:
#             currency_cols = []

#         label.setText(f"{label.text().split(':')[0]}: {len(rows)}")
#         table_widget.clear()
#         table_widget.setColumnCount(len(headers))
#         table_widget.setRowCount(len(rows))
#         table_widget.setHorizontalHeaderLabels(headers)

#         for r, row in enumerate(rows):
#             for c, val in enumerate(row):
#                 if c in currency_cols:
#                     display_val = f"₹ {float(val):,.2f}" if val else "₹ 0.00"
#                 else:
#                     display_val = str(val) if val is not None else ""
#                 item = QTableWidgetItem(display_val)
#                 if c in currency_cols or "ID" in headers[c] or "Total" in headers[c]:
#                     item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
#                 else:
#                     item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
#                 table_widget.setItem(r, c, item)
#         table_widget.resizeColumnsToContents()
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt
from database.connection import get_db_connection, close_db_connection
from ui.widgets.styles import TABLE_STYLE

class ReportingScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reports")
        self.resize(1200, 700)

        # ---------------- Main layout ----------------
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)

        # Title
        title = QLabel("Reports & Analytics")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size:28px; font-weight:700; color:#2c3e50;")
        main_layout.addWidget(title)  # Fixed, no stretch
        title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Dropdown / Report Selector
        dropdown_frame = QFrame()
        dropdown_layout = QVBoxLayout(dropdown_frame)
        dropdown_layout.setContentsMargins(0, 0, 0, 0)
        dropdown_layout.setSpacing(6)
        dropdown_label = QLabel("Select Report Type:")
        self.report_selector = QComboBox()
        self.report_selector.addItems([
            "Select Report",
            "Expense Vs Inventory Comparison",
            "Available Inventory Data"
        ])
        self.report_selector.setStyleSheet("QComboBox { font-size:14px; padding:6px; min-height:28px; }")
        self.report_selector.currentIndexChanged.connect(self.load_report_by_index)
        dropdown_layout.addWidget(dropdown_label)
        dropdown_layout.addWidget(self.report_selector)
        main_layout.addWidget(dropdown_frame)  # Fixed, no stretch
        dropdown_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Table Wrapper (Frame + Table)
        self.table_wrappers = {}
        self._create_table_wrapper("Report Table", main_layout)

        # Only the table stretches vertically
        main_layout.setStretchFactor(self.table_wrappers["Report Table"]["frame"], 1)

        # Hide initially
        self._hide_all_tables()

    # ---------------- Create table wrapper ----------------
    def _create_table_wrapper(self, label_text, parent_layout):
        frame = QFrame()
        frame.setStyleSheet("QFrame { border:1px solid #e4e7ea; border-radius:6px; background:#fff; }")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        label = QLabel(f"{label_text} Rows: 0")
        label.setStyleSheet("font-weight:600; font-size:13px; color:#2c3e50;")
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        table = QTableWidget()
        table.setAlternatingRowColors(True)
        table.setStyleSheet(TABLE_STYLE)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout.addWidget(label)
        layout.addWidget(table, 1)  # table stretches inside frame
        parent_layout.addWidget(frame, 1)  # frame stretches vertically

        self.table_wrappers[label_text] = {"frame": frame, "label": label, "table": table}
        frame.hide()

    # ---------------- Hide all tables ----------------
    def _hide_all_tables(self):
        for wrapper in self.table_wrappers.values():
            wrapper["frame"].hide()

    # ---------------- Load report ----------------
    def load_report_by_index(self, index):
        self._hide_all_tables()
        if index == 0:
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            if index == 1:  # Expense vs Inventory
                cursor.execute("""
                    SELECT
                        s.unique_name AS Seller,
                        COALESCE(inv.total_purchase, 0) AS Inventory_Total,
                        COALESCE(exp.total_expense, 0) AS Expense_Total,
                        (COALESCE(exp.total_expense, 0) - COALESCE(inv.total_purchase, 0)) AS Difference
                    FROM seller s
                    LEFT JOIN (
                        SELECT seller_id, SUM(purchase_price) AS total_purchase
                        FROM inventory
                        GROUP BY seller_id
                    ) inv ON inv.seller_id = s.seller_id
                    LEFT JOIN (
                        SELECT UPPER(payee_name) AS payee, SUM(amount) AS total_expense
                        FROM expense
                        WHERE UPPER(expense_type) = 'GARMENTS'
                        GROUP BY UPPER(payee_name)
                    ) exp ON exp.payee = UPPER(s.unique_name)
                    WHERE (COALESCE(exp.total_expense,0) - COALESCE(inv.total_purchase,0)) != 0
                    ORDER BY s.unique_name
                """)
                headers = [desc[0] for desc in cursor.description]  # dynamic headers
                rows = cursor.fetchall()
                self.populate_table(
                    self.table_wrappers["Report Table"]["table"],
                    self.table_wrappers["Report Table"]["label"],
                    headers,
                    rows,
                    currency_cols=[1, 2, 3]
                )
                self.table_wrappers["Report Table"]["frame"].show()

            elif index == 2:  # Available Inventory
                cursor.execute("""
                    SELECT type, item_description, material, size, purchase_price, price_tag
                    FROM inventory
                    WHERE sold = 0
                    ORDER BY inventory_id
                """)
                headers = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                self.populate_table(
                    self.table_wrappers["Report Table"]["table"],
                    self.table_wrappers["Report Table"]["label"],
                    headers,
                    rows,
                    currency_cols=[4, 5]
                )
                self.table_wrappers["Report Table"]["frame"].show()
        finally:
            close_db_connection(conn)

    # ---------------- Populate table ----------------
    def populate_table(self, table_widget, label, headers, rows, currency_cols=None):
        if currency_cols is None:
            currency_cols = []

        label.setText(f"{label.text().split(':')[0]}: {len(rows)}")
        table_widget.clear()
        table_widget.setColumnCount(len(headers))
        table_widget.setRowCount(len(rows))
        table_widget.setHorizontalHeaderLabels(headers)

        for r, row in enumerate(rows):
            for c in range(len(headers)):
                val = row[c] if c < len(row) else ""
                if c in currency_cols and val not in (None, ""):
                    display_val = f"₹ {float(val):,.2f}"
                else:
                    display_val = str(val) if val is not None else ""
                item = QTableWidgetItem(display_val)

                # Alignment
                if c in currency_cols:
                    item.setTextAlignment(int(Qt.AlignmentFlag.AlignRight) | int(Qt.AlignmentFlag.AlignVCenter))
                elif "ID" in headers[c] or "total" in headers[c].lower():
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                else:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

                table_widget.setItem(r, c, item)

        table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table_widget.verticalHeader().setVisible(False)
        table_widget.setAlternatingRowColors(True)
        table_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)