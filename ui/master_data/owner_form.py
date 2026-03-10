import pycountry

from PySide6.QtWidgets import (
    QLineEdit, QTextEdit, QCheckBox,
    QComboBox, QMessageBox, QDateEdit, QDoubleSpinBox
)

from PySide6.QtCore import QDate

from ui.forms.base_form import BaseForm

from database.connection import get_db_connection, close_db_connection
from ui.widgets.styles import LINEEDIT_STYLE
from config.logger import log

from ui.utils.form_helpers import (
    clean_text,
    clean_email,
    clean_contact,
    is_valid_email
)

from ui.utils.ui_helpers import apply_style


class OwnerForm(BaseForm):

    def __init__(self, owner_id=None):

        super().__init__("Owner", 600, 700)

        self.owner_id = owner_id

        # ---------------- Title ----------------
        self.title = QComboBox()
        self.title.addItems(
            ["", "Mr", "Mrs", "Miss", "Ms", "Dr", "Prof", "Company", "Other"]
        )

        # ---------------- Name ----------------
        self.first_name = QLineEdit()
        self.last_name = QLineEdit()

        # ---------------- Contact ----------------
        self.phone1 = QLineEdit()
        self.phone2 = QLineEdit()
        self.email = QLineEdit()

        # ---------------- Address ----------------
        self.address = QTextEdit()

        self.city = QLineEdit()
        self.state = QLineEdit()

        self.country = QComboBox()
        self.country.setEditable(True)
        self.country.addItem("")

        for c in pycountry.countries:
            self.country.addItem(c.name)

        # ---------------- Paid Capital ----------------
        self.paid_capital = QDoubleSpinBox()
        self.paid_capital.setPrefix("₹ ")
        self.paid_capital.setMaximum(1_000_000_000)
        self.paid_capital.setDecimals(2)

        # ---------------- Dates ----------------
        default_date = QDate(1900, 1, 1)

        self.birthday = QDateEdit()
        self.birthday.setCalendarPopup(True)
        self.birthday.setDisplayFormat("yyyy-MM-dd")
        self.birthday.setDate(default_date)

        self.anniversary = QDateEdit()
        self.anniversary.setCalendarPopup(True)
        self.anniversary.setDisplayFormat("yyyy-MM-dd")
        self.anniversary.setDate(default_date)

        # ---------------- Active ----------------
        self.active = QCheckBox()
        self.active.setChecked(True)

        # ---------------- Apply Styles ----------------
        apply_style(
            [
                self.title,
                self.first_name,
                self.last_name,
                self.phone1,
                self.phone2,
                self.email,
                self.address,
                self.city,
                self.state,
                self.country,
                self.paid_capital
            ],
            LINEEDIT_STYLE
        )

        # ---------------- Add fields ----------------
        f = self.form_layout

        f.addRow("Title", self.title)
        f.addRow("First Name *", self.first_name)
        f.addRow("Last Name", self.last_name)

        f.addRow("Phone 1", self.phone1)
        f.addRow("Phone 2", self.phone2)
        f.addRow("Email", self.email)

        f.addRow("Address", self.address)
        f.addRow("City", self.city)
        f.addRow("State", self.state)
        f.addRow("Country", self.country)

        f.addRow("Paid Capital", self.paid_capital)

        f.addRow("Birthday", self.birthday)
        f.addRow("Anniversary", self.anniversary)

        f.addRow("Active", self.active)

        # ---------------- Button Action ----------------
        self.save_btn.clicked.connect(self.save_owner)

        # ---------------- Load existing owner ----------------
        if self.owner_id:
            self.load_owner()

    # ---------------- Load Owner ----------------
    def load_owner(self):

        conn = None

        try:

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT title, first_name, last_name,
                       phone_1, phone_2, email,
                       address, city, state, country,
                       paid_capital, birthday, anniversary, is_active
                FROM owner
                WHERE owner_id = ?
            """, (self.owner_id,))

            row = cursor.fetchone()

            if not row:
                log(f"⚠️ Owner ID {self.owner_id} not found")
                return

            (
                title, first_name, last_name,
                phone1, phone2, email,
                addr, city, state, country,
                paid_capital, birthday, anniversary, active
            ) = row

            self.title.setCurrentText(title or "")

            self.first_name.setText(first_name or "")
            self.last_name.setText(last_name or "")

            self.phone1.setText(phone1 or "")
            self.phone2.setText(phone2 or "")

            self.email.setText(email or "")

            self.address.setPlainText(addr or "")

            self.city.setText(city or "")
            self.state.setText(state or "")

            self.country.setCurrentText(country or "")

            self.paid_capital.setValue(float(paid_capital or 0))

            if birthday:
                self.birthday.setDate(QDate.fromString(birthday, "yyyy-MM-dd"))

            if anniversary:
                self.anniversary.setDate(QDate.fromString(anniversary, "yyyy-MM-dd"))

            self.active.setChecked(bool(active))

            log(f"✅ Loaded owner ID {self.owner_id}")

        except Exception as e:

            log(f"❌ Failed to load owner: {e}")

            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load owner:\n{e}"
            )

        finally:

            close_db_connection(conn)

    # ---------------- Save Owner ----------------
    def save_owner(self):

        first_name = self.first_name.text().strip()

        if not first_name:

            QMessageBox.warning(
                self,
                "Validation",
                "First Name is required."
            )
            return

        email = self.email.text().strip()

        if email and not is_valid_email(email):

            QMessageBox.warning(
                self,
                "Invalid Email",
                "Please enter a valid email."
            )
            return

        data = (
            self.title.currentText().strip(),
            clean_text(first_name),
            clean_text(self.last_name.text()),
            clean_contact(self.phone1.text()),
            clean_contact(self.phone2.text()),
            clean_email(self.email.text()),
            clean_text(self.address.toPlainText()),
            clean_text(self.city.text()),
            clean_text(self.state.text()),
            clean_text(self.country.currentText()),
            self.paid_capital.value(),
            self.birthday.date().toString("yyyy-MM-dd"),
            self.anniversary.date().toString("yyyy-MM-dd"),
            int(self.active.isChecked())
        )

        conn = None

        try:

            conn = get_db_connection()
            cursor = conn.cursor()

            if self.owner_id:

                cursor.execute("""
                    UPDATE owner SET
                        title=?, first_name=?, last_name=?,
                        phone_1=?, phone_2=?, email=?,
                        address=?, city=?, state=?, country=?,
                        paid_capital=?, birthday=?, anniversary=?, is_active=?
                    WHERE owner_id=?
                """, data + (self.owner_id,))

                log(f"✅ Updated owner ID {self.owner_id}")

            else:

                cursor.execute("""
                    INSERT INTO owner(
                        title, first_name, last_name,
                        phone_1, phone_2, email,
                        address, city, state, country,
                        paid_capital, birthday, anniversary, is_active
                    )
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, data)

                log("✅ Inserted new owner")

            conn.commit()

            self.accept()

        except Exception as e:

            log(f"❌ Failed to save owner: {e}")

            QMessageBox.critical(
                self,
                "Error",
                f"Database error: {e}"
            )

        finally:

            close_db_connection(conn)