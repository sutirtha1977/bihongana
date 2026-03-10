from PySide6.QtWidgets import (
    QLineEdit, QTextEdit, QCheckBox,
    QComboBox, QMessageBox, QDateEdit, QDoubleSpinBox
)

from PySide6.QtCore import QDate

from ui.forms.base_form import BaseForm
from database.connection import get_db_connection, close_db_connection
from ui.widgets.styles import LINEEDIT_STYLE
from config.logger import log

from ui.utils.form_helpers import clean_text
from ui.utils.ui_helpers import apply_style


class InventoryForm(BaseForm):

    def __init__(self, inventory_id=None):

        super().__init__("Inventory", 600, 700)

        self.inventory_id = inventory_id

        # ---------------- Seller ----------------
        self.seller = QComboBox()
        self.load_sellers()

        # ---------------- Fields ----------------
        self.type = QLineEdit()
        self.item_description = QTextEdit()
        self.material = QLineEdit()
        self.item_size = QLineEdit()
        self.bill_no = QLineEdit()

        self.purchase_price = QDoubleSpinBox()
        self.purchase_price.setPrefix("₹ ")
        self.purchase_price.setMaximum(1_000_000_000)
        self.purchase_price.setDecimals(2)

        self.purchase_date = QDateEdit()
        self.purchase_date.setCalendarPopup(True)
        self.purchase_date.setDisplayFormat("yyyy-MM-dd")
        self.purchase_date.setDate(QDate.currentDate())

        self.payment_mode = QLineEdit()

        self.price_tag = QDoubleSpinBox()
        self.price_tag.setPrefix("₹ ")
        self.price_tag.setMaximum(1_000_000_000)
        self.price_tag.setDecimals(2)

        self.sold = QCheckBox()

        self.notes = QTextEdit()

        self.is_active = QCheckBox()
        self.is_active.setChecked(True)

        # ---------------- Apply Styles ----------------
        apply_style(
            [
                self.seller,
                self.type,
                self.item_description,
                self.material,
                self.item_size,
                self.bill_no,
                self.payment_mode,
                self.notes,
                self.purchase_price,
                self.price_tag
            ],
            LINEEDIT_STYLE
        )

        # ---------------- Add Fields ----------------
        f = self.form_layout

        f.addRow("Seller *", self.seller)
        f.addRow("Type", self.type)
        f.addRow("Item Description", self.item_description)
        f.addRow("Material", self.material)
        f.addRow("Size", self.item_size)
        f.addRow("Bill No", self.bill_no)

        f.addRow("Purchase Price", self.purchase_price)
        f.addRow("Purchase Date", self.purchase_date)

        f.addRow("Payment Mode", self.payment_mode)

        f.addRow("Price Tag", self.price_tag)

        f.addRow("Sold", self.sold)

        f.addRow("Notes", self.notes)

        f.addRow("Active", self.is_active)

        # ---------------- Button Action ----------------
        self.save_btn.clicked.connect(self.save_inventory)

        # ---------------- Load Existing ----------------
        if self.inventory_id:
            self.load_inventory()

    # ---------------- Load Sellers ----------------
    def load_sellers(self):

        conn = None

        try:

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT seller_id, unique_name FROM seller ORDER BY unique_name"
            )

            sellers = cursor.fetchall()

            for sid, uname in sellers:
                self.seller.addItem(uname, sid)

            log(f"✅ Loaded {len(sellers)} sellers")

        except Exception as e:

            log(f"❌ Failed to load sellers: {e}")

        finally:

            close_db_connection(conn)

    # ---------------- Load Inventory ----------------
    def load_inventory(self):

        conn = None

        try:

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT seller_id, type, item_description, material, size, bill_no,
                       purchase_price, purchase_date, payment_mode, price_tag,
                       sold, notes, is_active
                FROM inventory
                WHERE inventory_id = ?
            """, (self.inventory_id,))

            row = cursor.fetchone()

            if not row:
                log(f"⚠️ Inventory ID {self.inventory_id} not found")
                return

            (
                seller_id, type_, desc, material, size, bill_no,
                purchase_price, purchase_date, payment_mode, price_tag,
                sold, notes, active
            ) = row

            index = self.seller.findData(seller_id)

            if index >= 0:
                self.seller.setCurrentIndex(index)

            self.type.setText(type_ or "")
            self.item_description.setPlainText(desc or "")
            self.material.setText(material or "")
            self.item_size.setText(size or "")
            self.bill_no.setText(bill_no or "")

            self.purchase_price.setValue(float(purchase_price or 0))

            if purchase_date:
                self.purchase_date.setDate(
                    QDate.fromString(purchase_date, "yyyy-MM-dd")
                )

            self.payment_mode.setText(payment_mode or "")

            self.price_tag.setValue(float(price_tag or 0))

            self.sold.setChecked(bool(sold))

            self.notes.setPlainText(notes or "")

            self.is_active.setChecked(bool(active))

            log(f"✅ Loaded inventory ID {self.inventory_id}")

        except Exception as e:

            log(f"❌ Failed to load inventory: {e}")

            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load inventory:\n{e}"
            )

        finally:

            close_db_connection(conn)

    # ---------------- Save Inventory ----------------
    def save_inventory(self):

        if self.seller.currentIndex() < 0:

            QMessageBox.warning(
                self,
                "Validation",
                "Seller must be selected."
            )
            return

        seller_id = self.seller.currentData()

        data = (
            seller_id,
            clean_text(self.type.text()),
            clean_text(self.item_description.toPlainText()),
            clean_text(self.material.text()),
            clean_text(self.item_size.text()),
            clean_text(self.bill_no.text()),
            self.purchase_price.value(),
            self.purchase_date.date().toString("yyyy-MM-dd"),
            clean_text(self.payment_mode.text()),
            self.price_tag.value(),
            int(self.sold.isChecked()),
            clean_text(self.notes.toPlainText()),
            int(self.is_active.isChecked())
        )

        conn = None

        try:

            conn = get_db_connection()
            cursor = conn.cursor()

            if self.inventory_id:

                cursor.execute("""
                    UPDATE inventory SET
                        seller_id=?, type=?, item_description=?, material=?, size=?, bill_no=?,
                        purchase_price=?, purchase_date=?, payment_mode=?, price_tag=?,
                        sold=?, notes=?, is_active=?
                    WHERE inventory_id=?
                """, data + (self.inventory_id,))

                log(f"✅ Updated inventory ID {self.inventory_id}")

            else:

                cursor.execute("""
                    INSERT INTO inventory(
                        seller_id, type, item_description, material, size, bill_no,
                        purchase_price, purchase_date, payment_mode, price_tag,
                        sold, notes, is_active
                    )
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, data)

                log("✅ Inserted new inventory item")

            conn.commit()

            self.accept()

        except Exception as e:

            log(f"❌ Failed to save inventory: {e}")

            QMessageBox.critical(
                self,
                "Error",
                f"Database error: {e}"
            )

        finally:

            close_db_connection(conn)