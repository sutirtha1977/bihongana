from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QTableWidget, QTableWidgetItem, QFrame, QSizePolicy, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QCategoryAxis, QValueAxis
from database.connection import get_db_connection, close_db_connection
from config.logger import log
from ui.widgets.styles import TABLE_STYLE
import datetime

class DashboardScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Dashboard")
        self.resize(1400, 800)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20,20,20,20)
        self.main_layout.setSpacing(12)

        # Title
        title = QLabel("Inventory & Sales Dashboard")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size:28px; font-weight:700; color:#2c3e50;")
        self.main_layout.addWidget(title)

        # Filters
        filter_frame = QFrame()
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(0,0,0,0)
        filter_layout.setSpacing(12)

        self.seller_selector = QComboBox()
        self.seller_selector.addItem("All Sellers")
        self.load_sellers()
        self.seller_selector.currentIndexChanged.connect(self.refresh_dashboard)

        self.report_selector = QComboBox()
        self.report_selector.addItems([
            "Select Report",
            "Expense Vs Inventory Comparison",
            "Available Inventory Data"
        ])
        self.report_selector.currentIndexChanged.connect(self.refresh_dashboard)

        filter_layout.addWidget(QLabel("Filter by Seller:"))
        filter_layout.addWidget(self.seller_selector)
        filter_layout.addWidget(QLabel("Select Report:"))
        filter_layout.addWidget(self.report_selector)
        filter_layout.addStretch()
        self.main_layout.addWidget(filter_frame)

        # KPI cards
        self.kpi_frame = QFrame()
        kpi_layout = QHBoxLayout(self.kpi_frame)
        kpi_layout.setSpacing(20)
        self.kpi_cards = {}
        for kpi_name in ["Total Inventory", "Total Sales", "Total Expenses"]:
            card = QLabel(f"{kpi_name}\n0")
            card.setStyleSheet("""
                QLabel {
                    background: #3498db; color: #fff;
                    font-size:16px; font-weight:600;
                    padding:20px; border-radius:8px;
                }
            """)
            card.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            kpi_layout.addWidget(card)
            self.kpi_cards[kpi_name] = card
        self.main_layout.addWidget(self.kpi_frame)

        # Chart
        self.chart_view = QChartView()
        self.chart_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.main_layout.addWidget(self.chart_view, 3)

        # Table
        self.table_frame = QFrame()
        table_layout = QVBoxLayout(self.table_frame)
        table_layout.setContentsMargins(0,0,0,0)
        self.report_table = QTableWidget()
        self.report_table.setAlternatingRowColors(True)
        self.report_table.setStyleSheet(TABLE_STYLE)
        self.report_table.horizontalHeader().setStretchLastSection(True)
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table_layout.addWidget(self.report_table)
        self.main_layout.addWidget(self.table_frame, 2)

        self.refresh_dashboard()

    # ---------------- Load sellers ----------------
    def load_sellers(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT unique_name FROM seller ORDER BY unique_name")
            sellers = cursor.fetchall()
            for s in sellers:
                self.seller_selector.addItem(s[0])
        finally:
            close_db_connection(conn)

    # ---------------- Refresh dashboard ----------------
    def refresh_dashboard(self):
        seller_filter = self.seller_selector.currentText()
        report_index = self.report_selector.currentIndex()
        self.update_kpis(seller_filter)
        self.update_chart(seller_filter)
        self.update_table(report_index, seller_filter)

    # ---------------- Update KPI cards ----------------
    def update_kpis(self, seller):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Total Inventory
            q_inv = "SELECT COUNT(*) FROM inventory"
            if seller != "All Sellers":
                q_inv += " WHERE seller_id = (SELECT seller_id FROM seller WHERE unique_name=?)"
                cursor.execute(q_inv, (seller,))
            else:
                cursor.execute(q_inv)
            total_inventory = cursor.fetchone()[0]
            self.kpi_cards["Total Inventory"].setText(f"Total Inventory\n{total_inventory}")

            # Total Sales
            q_sales = "SELECT COUNT(*) FROM sales"
            if seller != "All Sellers":
                q_sales += " WHERE inventory_id IN (SELECT inventory_id FROM inventory WHERE seller_id = (SELECT seller_id FROM seller WHERE unique_name=?))"
                cursor.execute(q_sales, (seller,))
            else:
                cursor.execute(q_sales)
            total_sales = cursor.fetchone()[0]
            self.kpi_cards["Total Sales"].setText(f"Total Sales\n{total_sales}")

            # Total Expenses
            q_exp = "SELECT SUM(amount) FROM expense"
            if seller != "All Sellers":
                q_exp += " WHERE payee_name = ?"
                cursor.execute(q_exp, (seller,))
            else:
                cursor.execute(q_exp)
            total_exp = cursor.fetchone()[0] or 0
            self.kpi_cards["Total Expenses"].setText(f"Total Expenses\n₹ {total_exp:,.2f}")
        finally:
            close_db_connection(conn)

    # ---------------- Update chart ----------------
    def update_chart(self, seller):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            today = datetime.date.today()
            months = [(today.replace(day=1) - datetime.timedelta(days=30*i)).strftime("%b %Y") for i in reversed(range(6))]
            sales_data, expense_data = [], []

            for month in months:
                first_day = datetime.datetime.strptime(month, "%b %Y")
                last_day = (first_day + datetime.timedelta(days=31)).replace(day=1)

                # Sales count
                q_sales = "SELECT COUNT(*) FROM sales WHERE sale_date BETWEEN ? AND ?"
                if seller != "All Sellers":
                    q_sales += " AND inventory_id IN (SELECT inventory_id FROM inventory WHERE seller_id=(SELECT seller_id FROM seller WHERE unique_name=?))"
                    cursor.execute(q_sales, (first_day, last_day, seller))
                else:
                    cursor.execute(q_sales, (first_day, last_day))
                sales_data.append(cursor.fetchone()[0])

                # Expenses sum
                q_exp = "SELECT SUM(amount) FROM expense WHERE expense_date BETWEEN ? AND ?"
                if seller != "All Sellers":
                    q_exp += " AND payee_name=?"
                    cursor.execute(q_exp, (first_day, last_day, seller))
                else:
                    cursor.execute(q_exp, (first_day, last_day))
                expense_data.append(cursor.fetchone()[0] or 0)

            chart = QChart()
            chart.setTitle("Monthly Sales vs Expenses")

            series_sales = QLineSeries()
            series_sales.setName("Sales")
            for i, val in enumerate(sales_data):
                series_sales.append(i, val)

            series_exp = QLineSeries()
            series_exp.setName("Expenses")
            for i, val in enumerate(expense_data):
                series_exp.append(i, val)

            chart.addSeries(series_sales)
            chart.addSeries(series_exp)

            axisX = QCategoryAxis()
            for i, month in enumerate(months):
                axisX.append(month, i)
            axisX.setLabelsAngle(-45)
            chart.addAxis(axisX, Qt.AlignBottom)
            series_sales.attachAxis(axisX)
            series_exp.attachAxis(axisX)

            axisY = QValueAxis()
            axisY.setTitleText("Count / Amount")
            chart.addAxis(axisY, Qt.AlignLeft)
            series_sales.attachAxis(axisY)
            series_exp.attachAxis(axisY)

            chart.legend().setAlignment(Qt.AlignTop)
            self.chart_view.setChart(chart)
        finally:
            close_db_connection(conn)

    # ---------------- Update table ----------------
    def update_table(self, report_index, seller):
        self.report_table.clear()
        if report_index == 0:
            self.report_table.setRowCount(0)
            self.report_table.setColumnCount(0)
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            if report_index == 1:
                query = """
                    SELECT s.unique_name AS Seller,
                           COALESCE(SUM(inv.purchase_price),0) AS Inventory_Total,
                           COALESCE(SUM(exp.amount),0) AS Expense_Total,
                           COALESCE(SUM(exp.amount),0)-COALESCE(SUM(inv.purchase_price),0) AS Difference
                    FROM seller s
                    LEFT JOIN inventory inv ON inv.seller_id = s.seller_id
                    LEFT JOIN expense exp ON exp.payee_name = s.unique_name
                """
                if seller != "All Sellers":
                    query += " WHERE s.unique_name=? GROUP BY s.unique_name"
                    cursor.execute(query, (seller,))
                else:
                    query += " GROUP BY s.unique_name"
                    cursor.execute(query)
                rows = cursor.fetchall()
                headers = [desc[0] for desc in cursor.description]
                self.populate_table(self.report_table, headers, rows, currency_cols=[1,2,3])
            elif report_index == 2:
                query = "SELECT type, item_description, material, size, purchase_price, price_tag FROM inventory WHERE sold=0"
                if seller != "All Sellers":
                    query += " AND seller_id=(SELECT seller_id FROM seller WHERE unique_name=?)"
                    cursor.execute(query, (seller,))
                else:
                    cursor.execute(query)
                rows = cursor.fetchall()
                headers = [desc[0] for desc in cursor.description]
                self.populate_table(self.report_table, headers, rows, currency_cols=[4,5])
        finally:
            close_db_connection(conn)

    # ---------------- Populate table ----------------
    def populate_table(self, table_widget, headers, rows, currency_cols=None):
        if currency_cols is None:
            currency_cols = []

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