from PySide6.QtWidgets import (
    QLineEdit, QTextEdit, QCheckBox, QMessageBox
)

from ui.forms.base_form import BaseForm

from database.connection import get_db_connection, close_db_connection
from ui.widgets.styles import LINEEDIT_STYLE
from config.logger import log

from ui.utils.form_helpers import (
    clean_text,
    clean_email,
    clean_contact,
    is_valid_email,
    is_valid_contact
)

from ui.utils.ui_helpers import apply_style


class SellerForm(BaseForm):

    def __init__(self, seller_id=None):

        super().__init__("Seller", 600, 650)

        self.seller_id = seller_id

        # ---------------- Fields ----------------
        self.unique_name = QLineEdit()
        self.shop_name = QLineEdit()
        self.owner_name = QLineEdit()

        self.selling_items = QTextEdit()

        self.phone1 = QLineEdit()
        self.phone2 = QLineEdit()

        self.email = QLineEdit()

        self.address = QTextEdit()
        self.landmark = QTextEdit()

        self.city = QLineEdit()
        self.state = QLineEdit()
        self.country = QLineEdit()

        self.minimum_purchase = QLineEdit()
        self.timings = QLineEdit()

        self.notes = QTextEdit()

        self.active = QCheckBox()
        self.active.setChecked(True)

        # ---------------- Apply Styles ----------------
        apply_style(
            [
                self.unique_name,
                self.shop_name,
                self.owner_name,
                self.phone1,
                self.phone2,
                self.email,
                self.city,
                self.state,
                self.country,
                self.minimum_purchase,
                self.timings
            ],
            LINEEDIT_STYLE
        )

        apply_style(
            [
                self.selling_items,
                self.address,
                self.landmark,
                self.notes
            ],
            LINEEDIT_STYLE
        )

        # ---------------- Add fields ----------------
        f = self.form_layout

        f.addRow("Unique Name *", self.unique_name)
        f.addRow("Shop Name *", self.shop_name)
        f.addRow("Owner Name", self.owner_name)

        f.addRow("Selling Items", self.selling_items)

        f.addRow("Phone 1", self.phone1)
        f.addRow("Phone 2", self.phone2)

        f.addRow("Email", self.email)

        f.addRow("Address", self.address)
        f.addRow("Landmark", self.landmark)

        f.addRow("City", self.city)
        f.addRow("State", self.state)
        f.addRow("Country", self.country)

        f.addRow("Minimum Purchase", self.minimum_purchase)
        f.addRow("Timings", self.timings)

        f.addRow("Notes", self.notes)

        f.addRow("Active", self.active)

        # ---------------- Button Action ----------------
        self.save_btn.clicked.connect(self.save_seller)

        # ---------------- Load seller if editing ----------------
        if self.seller_id:
            self.load_seller()

    # ---------------- Load Seller ----------------
    def load_seller(self):

        conn = None

        try:

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT unique_name, shop_name, owner_name, selling_items,
                       phone_1, phone_2, email,
                       address, landmark, city, state, country,
                       minimum_purchase, timings, notes, is_active
                FROM seller
                WHERE seller_id = ?
            """, (self.seller_id,))

            row = cursor.fetchone()

            if not row:
                log(f"⚠️ Seller ID {self.seller_id} not found")
                return

            (
                unique_name, shop, owner, selling_items,
                phone1, phone2, email,
                addr, landmark, city, state, country,
                min_purchase, timings, notes, active
            ) = row

            self.unique_name.setText(unique_name or "")
            self.shop_name.setText(shop or "")
            self.owner_name.setText(owner or "")

            self.selling_items.setPlainText(selling_items or "")

            self.phone1.setText(phone1 or "")
            self.phone2.setText(phone2 or "")

            self.email.setText(email or "")

            self.address.setPlainText(addr or "")
            self.landmark.setPlainText(landmark or "")

            self.city.setText(city or "")
            self.state.setText(state or "")
            self.country.setText(country or "")

            self.minimum_purchase.setText(str(min_purchase or ""))
            self.timings.setText(timings or "")

            self.notes.setPlainText(notes or "")

            self.active.setChecked(bool(active))

            log(f"✅ Loaded seller ID {self.seller_id}")

        except Exception as e:

            log(f"❌ Failed to load seller: {e}")

        finally:

            close_db_connection(conn)

    # ---------------- Save Seller ----------------
    def save_seller(self):

        if not self.unique_name.text().strip() or not self.shop_name.text().strip():

            QMessageBox.warning(
                self,
                "Validation",
                "Unique Name and Shop Name are required"
            )
            return

        email = clean_email(self.email.text())

        if email and not is_valid_email(email):

            QMessageBox.warning(
                self,
                "Invalid Email",
                "Enter a valid email address"
            )
            return

        phone1 = clean_contact(self.phone1.text())
        phone2 = clean_contact(self.phone2.text())

        if phone1 and not is_valid_contact(phone1):

            QMessageBox.warning(
                self,
                "Invalid Phone",
                "Phone 1 is invalid"
            )
            return

        if phone2 and not is_valid_contact(phone2):

            QMessageBox.warning(
                self,
                "Invalid Phone",
                "Phone 2 is invalid"
            )
            return

        data = (
            clean_text(self.unique_name.text()),
            clean_text(self.shop_name.text()),
            clean_text(self.owner_name.text()),
            clean_text(self.selling_items.toPlainText()),
            phone1,
            phone2,
            email,
            clean_text(self.address.toPlainText()),
            clean_text(self.landmark.toPlainText()),
            clean_text(self.city.text()),
            clean_text(self.state.text()),
            clean_text(self.country.text()),
            clean_text(self.minimum_purchase.text()),
            clean_text(self.timings.text()),
            clean_text(self.notes.toPlainText()),
            int(self.active.isChecked())
        )

        conn = None

        try:

            conn = get_db_connection()
            cursor = conn.cursor()

            if self.seller_id:

                cursor.execute("""
                    UPDATE seller SET
                        unique_name=?, shop_name=?, owner_name=?, selling_items=?,
                        phone_1=?, phone_2=?, email=?, address=?, landmark=?, city=?, state=?, country=?,
                        minimum_purchase=?, timings=?, notes=?, is_active=?
                    WHERE seller_id=?
                """, data + (self.seller_id,))

                log(f"✅ Updated seller ID {self.seller_id}")

            else:

                cursor.execute("""
                    INSERT INTO seller(
                        unique_name, shop_name, owner_name, selling_items,
                        phone_1, phone_2, email, address, landmark, city, state, country,
                        minimum_purchase, timings, notes, is_active
                    )
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, data)

                log(f"✅ Inserted new seller: {self.unique_name.text().strip()}")

            conn.commit()

            self.accept()

        except Exception as e:

            log(f"❌ Failed to save seller: {e}")

            QMessageBox.critical(
                self,
                "Error",
                f"Database error: {e}"
            )

        finally:

            close_db_connection(conn)