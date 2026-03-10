# ui/owners_screen.py

from PySide6.QtCore import Qt, QDate  # <-- import QDate here
from ui.crud_screen import CrudScreen
from ui.master_data.owner_form import OwnerForm

OWNER_HEADERS = [
    "Owner ID", "Title", "First Name", "Last Name", "Phone 1",
    "Phone 2", "Email", "Address", "City", "State", "Country",
    "Paid Capital", "Birthday", "Anniversary",
    "Active", "Created At", "Updated At"
]

OWNER_QUERY = """
SELECT *
FROM owner
ORDER BY owner_id
"""

class OwnersScreen(CrudScreen):

    def __init__(self):
        super().__init__("owner", OWNER_HEADERS, OwnerForm, OWNER_QUERY)
        self.hide_columns()
        self.format_paid_capital_column()
        self.format_date_columns()

    def hide_columns(self):
        self.table.hideColumn(0)   # owner_id
        self.table.hideColumn(14)  # is_active
        self.table.hideColumn(15)  # created_at
        self.table.hideColumn(16)  # updated_at

    def format_paid_capital_column(self):
        for row in range(self.table.rowCount()):
            col = 11  # Paid Capital column
            item = self.table.item(row, col)
            if item:
                try:
                    value = float(item.text())
                    item.setText(f"₹ {value:,.2f}")
                    item.setTextAlignment(int(Qt.AlignmentFlag.AlignRight) | int(Qt.AlignmentFlag.AlignVCenter))
                except ValueError:
                    pass

    def format_date_columns(self):
        for row in range(self.table.rowCount()):
            for col in [12, 13]:  # Birthday and Anniversary
                item = self.table.item(row, col)
                if item:
                    try:
                        qdate = QDate.fromString(item.text(), "yyyy-MM-dd")
                        if qdate.isValid():
                            item.setText(qdate.toString("d-MMM-yyyy"))
                    except Exception:
                        pass