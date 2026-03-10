# ui/expenses_screen.py

from PySide6.QtCore import Qt, QDate
from ui.crud_screen import CrudScreen
from ui.master_data.expense_form import ExpenseForm

EXPENSE_HEADERS = [
    "Expense ID", "Date", "Type", "Description",
    "Payee Name", "Phone 1", "Phone 2", "Amount",
    "Active", "Created At", "Updated At"
]

EXPENSE_QUERY = """
SELECT *
FROM expense
ORDER BY expense_id
"""

class ExpensesScreen(CrudScreen):

    def __init__(self):
        super().__init__("expense", EXPENSE_HEADERS, ExpenseForm, EXPENSE_QUERY)
        self.hide_columns()
        self.format_amount_column()
        self.format_date_column()

    def hide_columns(self):
        self.table.hideColumn(0)   # expense_id
        self.table.hideColumn(8)   # is_active
        self.table.hideColumn(9)   # created_at
        self.table.hideColumn(10)  # updated_at

    def format_amount_column(self):
        for row in range(self.table.rowCount()):
            col = 7  # Amount column
            item = self.table.item(row, col)
            if item:
                try:
                    value = float(item.text())
                    item.setText(f"₹ {value:,.2f}")
                    item.setTextAlignment(int(Qt.AlignmentFlag.AlignRight) | int(Qt.AlignmentFlag.AlignVCenter))
                except ValueError:
                    pass

    def format_date_column(self):
        col = 1  # Date column
        for row in range(self.table.rowCount()):
            item = self.table.item(row, col)
            if item:
                try:
                    qdate = QDate.fromString(item.text(), "yyyy-MM-dd")
                    if qdate.isValid():
                        item.setText(qdate.toString("d-MMM-yyyy"))
                except Exception:
                    pass