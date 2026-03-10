import pycountry
from PySide6.QtWidgets import (
    QLineEdit, QTextEdit, QCheckBox, QComboBox, QDateEdit, QMessageBox
)
from PySide6.QtCore import QDate

from database.connection import get_db_connection, close_db_connection
from ui.widgets.styles import LINEEDIT_STYLE
from config.logger import log
from ui.forms.base_form import BaseForm
from ui.utils.form_helpers import clean_text, clean_email, clean_contact, is_valid_email
from ui.utils.ui_helpers import apply_style


class CustomerForm(BaseForm):
    def __init__(self, customer_id=None):
        super().__init__("Customer", 450, 600)
        self.customer_id = customer_id

        # ---------------- Fields ----------------
        self.title = QComboBox()
        self.title.addItems(["", "Mr", "Mrs", "Miss", "Ms", "Dr", "Prof", "Company", "Other"])

        self.unique_name = QLineEdit()
        self.first_name = QLineEdit()
        self.last_name = QLineEdit()

        self.phone1 = QLineEdit()
        self.phone2 = QLineEdit()
        self.email = QLineEdit()

        self.address = QTextEdit()
        self.city = QLineEdit()
        self.state = QLineEdit()

        self.country = QComboBox()
        self.country.setEditable(True)
        self.country.addItem("")
        for c in pycountry.countries:
            self.country.addItem(c.name)

        self.exhibition = QLineEdit()
        self.customer_type = QLineEdit()
        self.notes = QTextEdit()
        self.active = QCheckBox()
        self.active.setChecked(True)

        # ---------------- Standard QDateEdit for dates ----------------
        default_date = QDate(1900, 1, 1)
        self.birthday = QDateEdit()
        self.birthday.setCalendarPopup(True)
        self.birthday.setDisplayFormat("yyyy-MM-dd")
        self.birthday.setDate(default_date)

        self.anniversary = QDateEdit()
        self.anniversary.setCalendarPopup(True)
        self.anniversary.setDisplayFormat("yyyy-MM-dd")
        self.anniversary.setDate(default_date)

        # ---------------- Apply Styles ----------------
        apply_style(
            [
                self.title, self.unique_name, self.first_name, self.last_name,
                self.phone1, self.phone2, self.email, self.address, self.city,
                self.state, self.country, self.exhibition, self.customer_type, self.notes
            ],
            LINEEDIT_STYLE
        )

        # ---------------- Add Fields to Form Layout ----------------
        f = self.form_layout
        f.addRow("Title", self.title)
        f.addRow("Unique Name *", self.unique_name)
        f.addRow("First Name", self.first_name)
        f.addRow("Last Name", self.last_name)
        f.addRow("Phone 1", self.phone1)
        f.addRow("Phone 2", self.phone2)
        f.addRow("Email", self.email)
        f.addRow("Address", self.address)
        f.addRow("City", self.city)
        f.addRow("State", self.state)
        f.addRow("Country", self.country)
        f.addRow("Exhibition", self.exhibition)
        f.addRow("Customer Type", self.customer_type)
        f.addRow("Birthday", self.birthday)
        f.addRow("Anniversary", self.anniversary)
        f.addRow("Notes", self.notes)
        f.addRow("Active", self.active)

        # ---------------- Button Action ----------------
        self.save_btn.clicked.connect(self.save_customer)

        # ---------------- Load Existing ----------------
        if self.customer_id:
            self.load_customer()

    # ---------------- Load customer ----------------
    def load_customer(self):
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT title, unique_name, first_name, last_name,
                       phone_1, phone_2, email,
                       address, city, state, country,
                       exhibition, customer_type, notes,
                       birthday, anniversary, is_active
                FROM customer
                WHERE customer_id = ?
            """, (self.customer_id,))
            row = cursor.fetchone()
            if not row:
                log(f"⚠️ Customer ID {self.customer_id} not found")
                return

            (
                title, unique_name, first_name, last_name,
                phone1, phone2, email,
                addr, city, state, country,
                exhibition, ctype, notes,
                birthday, anniversary, active
            ) = row

            self.title.setCurrentText(title or "")
            self.unique_name.setText(unique_name or "")
            self.first_name.setText(first_name or "")
            self.last_name.setText(last_name or "")
            self.phone1.setText(phone1 or "")
            self.phone2.setText(phone2 or "")
            self.email.setText(email or "")
            self.address.setPlainText(addr or "")
            self.city.setText(city or "")
            self.state.setText(state or "")
            self.country.setCurrentText(country or "")
            self.exhibition.setText(exhibition or "")
            self.customer_type.setText(ctype or "")
            self.notes.setPlainText(notes or "")

            # ---------------- Dates ----------------
            self.birthday.setDate(QDate.fromString(birthday, "yyyy-MM-dd") if birthday else QDate(1900,1,1))
            self.anniversary.setDate(QDate.fromString(anniversary, "yyyy-MM-dd") if anniversary else QDate(1900,1,1))

            self.active.setChecked(bool(active))
            log(f"✅ Loaded customer ID {self.customer_id}")

        except Exception as e:
            log(f"❌ Failed to load customer: {e}")
        finally:
            close_db_connection(conn)

    # ---------------- Save customer ----------------
    def save_customer(self):
        if not self.unique_name.text().strip():
            QMessageBox.warning(self, "Validation", "Unique Name is required.")
            return

        email = self.email.text().strip()
        if email and not is_valid_email(email):
            QMessageBox.warning(self, "Invalid Email", "Please enter a valid email.")
            return

        data = (
            self.title.currentText().strip(),
            clean_text(self.unique_name.text()),
            clean_text(self.first_name.text()),
            clean_text(self.last_name.text()),
            clean_contact(self.phone1.text()),
            clean_contact(self.phone2.text()),
            clean_email(self.email.text()),
            clean_text(self.address.toPlainText()),
            clean_text(self.city.text()),
            clean_text(self.state.text()),
            clean_text(self.country.currentText()),
            clean_text(self.exhibition.text()),
            clean_text(self.customer_type.text()),
            clean_text(self.notes.toPlainText()),
            self.birthday.date().toString("yyyy-MM-dd"),
            self.anniversary.date().toString("yyyy-MM-dd"),
            int(self.active.isChecked())
        )

        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            if self.customer_id:
                cursor.execute("""
                    UPDATE customer SET
                        title=?, unique_name=?, first_name=?, last_name=?,
                        phone_1=?, phone_2=?, email=?, address=?, city=?, state=?, country=?,
                        exhibition=?, customer_type=?, notes=?,
                        birthday=?, anniversary=?, is_active=?
                    WHERE customer_id=?
                """, data + (self.customer_id,))
            else:
                cursor.execute("""
                    INSERT INTO customer(
                        title, unique_name, first_name, last_name,
                        phone_1, phone_2, email, address, city, state, country,
                        exhibition, customer_type, notes,
                        birthday, anniversary, is_active
                    )
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, data)

            conn.commit()
            self.accept()
        except Exception as e:
            log(f"❌ Failed to save customer: {e}")
            QMessageBox.critical(self, "Error", f"Database error: {e}")
        finally:
            close_db_connection(conn)