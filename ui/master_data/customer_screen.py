# ui/customers_screen.py

from PySide6.QtCore import Qt, QDate
from ui.crud_screen import CrudScreen
from ui.master_data.customer_form import CustomerForm

CUSTOMER_HEADERS = [
    "Customer ID", "Title", "Unique Name", "First Name", "Last Name",
    "Phone 1", "Phone 2", "Email", "Address",
    "City", "State", "Country", "Exhibition", "Customer Type",
    "Notes", "Birthday", "Anniversary",
    "Active", "Created At", "Updated At"
]

CUSTOMER_QUERY = """
SELECT *
FROM customer
ORDER BY customer_id
"""

class CustomersScreen(CrudScreen):

    def __init__(self):
        super().__init__("customer", CUSTOMER_HEADERS, CustomerForm, CUSTOMER_QUERY)
        self.hide_columns()
        self.format_date_columns()

    def hide_columns(self):
        self.table.hideColumn(0)   # customer_id
        self.table.hideColumn(17)  # is_active
        self.table.hideColumn(18)  # created_at
        self.table.hideColumn(19)  # updated_at

    def format_date_columns(self):
        for row in range(self.table.rowCount()):
            for col in [15, 16]:  # Birthday and Anniversary
                item = self.table.item(row, col)
                if item:
                    try:
                        qdate = QDate.fromString(item.text(), "yyyy-MM-dd")
                        if qdate.isValid():
                            item.setText(qdate.toString("d-MMM-yyyy"))
                    except Exception:
                        pass