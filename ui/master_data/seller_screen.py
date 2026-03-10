from ui.crud_screen import CrudScreen
from ui.master_data.seller_form import SellerForm


SELLER_HEADERS = [
    "Seller ID", "Unique Name", "Shop Name", "Owner Name", "Selling Items",
    "Phone 1", "Phone 2", "Email", "Address",
    "Landmark", "City", "State", "Country",
    "Min Purchase", "Timings", "Notes",
    "Active", "Created At", "Updated At"
]


SELLER_QUERY = """
SELECT *
FROM seller
ORDER BY seller_id
"""


class SellersScreen(CrudScreen):

    def __init__(self):
        super().__init__("seller", SELLER_HEADERS, SellerForm, SELLER_QUERY)

        self.hide_columns()

    def hide_columns(self):

        self.table.hideColumn(0)   # seller_id
        self.table.hideColumn(16)  # is_active
        self.table.hideColumn(17)  # created_at
        self.table.hideColumn(18)  # updated_at