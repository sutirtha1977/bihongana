# ui/inventory_screen.py

from PySide6.QtCore import Qt
from ui.crud_screen import CrudScreen
from ui.master_data.inventory_form import InventoryForm

INVENTORY_HEADERS = [
    "Inventory ID", "Seller ID", "Unique Name", "Type", "Item Description",
    "Material", "Size", "Bill No", "Purchase Price", "Price Tag",
    "Payment Mode", "Purchase Date", "Notes", "Sold", "Active"
]

INVENTORY_QUERY = """
SELECT 
    i.inventory_id,
    i.seller_id,
    s.unique_name,
    i.type,
    i.item_description,
    i.material,
    i.size,
    i.bill_no,
    i.purchase_price,
    i.price_tag,
    i.payment_mode,
    DATE(i.purchase_date) AS purchase_date,
    i.notes,
    CASE 
        WHEN i.sold = 1 THEN 'Yes'
        ELSE 'No'
    END AS sold,
    i.is_active
FROM inventory i
LEFT JOIN seller s ON i.seller_id = s.seller_id
ORDER BY i.inventory_id;
"""

class InventoryScreen(CrudScreen):

    def __init__(self):
        super().__init__("inventory", INVENTORY_HEADERS, InventoryForm, INVENTORY_QUERY)
        self.hide_columns()
        self.format_currency_columns()

    def hide_columns(self):
        self.table.hideColumn(0)  # inventory_id
        self.table.hideColumn(1)  # seller_id
        self.table.hideColumn(14)  # is_active

    def format_currency_columns(self):
        for row in range(self.table.rowCount()):
            for col in [8, 9]:  # Purchase Price & Price Tag
                item = self.table.item(row, col)
                if item:
                    try:
                        value = float(item.text())
                        item.setText(f"₹ {value:,.2f}")
                        item.setTextAlignment(int(Qt.AlignmentFlag.AlignRight) | int(Qt.AlignmentFlag.AlignVCenter))
                    except ValueError:
                        pass