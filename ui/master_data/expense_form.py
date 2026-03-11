from PySide6.QtWidgets import (
    QLineEdit, QTextEdit, QCheckBox,
    QDateEdit, QDoubleSpinBox, QMessageBox
)

from PySide6.QtCore import QDate

from ui.forms.base_form import BaseForm
from ui.widgets.styles import LINEEDIT_STYLE
from database.connection import get_db_connection, close_db_connection
from config.logger import log
from ui.widgets.popups import show_warning
from ui.utils.form_helpers import clean_text, clean_contact
from ui.utils.ui_helpers import apply_style

# NEW IMPORT
from ui.widgets.payment_mode import PaymentModeCombo


class ExpenseForm(BaseForm):

    def __init__(self, expense_id=None):

        super().__init__("Expense", 500, 620)

        self.expense_id = expense_id

        # ---------------- Fields ----------------

        self.expense_date = QDateEdit()
        self.expense_date.setCalendarPopup(True)
        self.expense_date.setDisplayFormat("yyyy-MM-dd")
        self.expense_date.setDate(QDate.currentDate())

        self.expense_type = QLineEdit()

        self.expense_description = QTextEdit()

        self.payee_name = QLineEdit()

        self.phone_1 = QLineEdit()
        self.phone_2 = QLineEdit()

        self.amount = QDoubleSpinBox()
        self.amount.setPrefix("₹ ")
        self.amount.setMaximum(1_000_000_000)
        self.amount.setDecimals(2)

        # Payment Mode (Reusable Widget)
        self.payment_mode = PaymentModeCombo()

        self.active = QCheckBox()
        self.active.setChecked(True)

        # ---------------- Apply Styles ----------------

        apply_style(
            [
                self.expense_type,
                self.expense_description,
                self.payee_name,
                self.phone_1,
                self.phone_2,
                self.amount,
                self.payment_mode
            ],
            LINEEDIT_STYLE
        )

        # ---------------- Form Layout ----------------

        f = self.form_layout

        f.addRow("Date *", self.expense_date)
        f.addRow("Type *", self.expense_type)
        f.addRow("Description", self.expense_description)

        f.addRow("Payee Name *", self.payee_name)

        f.addRow("Phone 1", self.phone_1)
        f.addRow("Phone 2", self.phone_2)

        f.addRow("Amount *", self.amount)
        f.addRow("Payment Mode", self.payment_mode)

        f.addRow("Active", self.active)

        # ---------------- Button Action ----------------

        self.save_btn.clicked.connect(self.save_expense)

        # ---------------- Load existing ----------------

        if self.expense_id:
            self.load_expense()

    # -------------------------------------------------
    # Load Expense
    # -------------------------------------------------

    def load_expense(self):

        conn = None

        try:

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT expense_date,
                       expense_type,
                       expense_description,
                       payee_name,
                       phone_1,
                       phone_2,
                       amount,
                       payment_mode,
                       is_active
                FROM expense
                WHERE expense_id = ?
            """, (self.expense_id,))

            row = cursor.fetchone()

            if not row:
                return

            if row[0]:
                self.expense_date.setDate(QDate.fromString(row[0], "yyyy-MM-dd"))

            self.expense_type.setText(row[1] or "")
            self.expense_description.setPlainText(row[2] or "")
            self.payee_name.setText(row[3] or "")

            self.phone_1.setText(row[4] or "")
            self.phone_2.setText(row[5] or "")

            self.amount.setValue(float(row[6] or 0))

            # Payment Mode
            self.payment_mode.set_value(row[7])

            self.active.setChecked(bool(row[8]))

            log(f"✅ Loaded expense ID {self.expense_id}")

        except Exception as e:

            log(f"❌ Failed to load expense: {e}")

            show_warning(self, f"Failed to load expense: {e}")

        finally:

            close_db_connection(conn)

    # -------------------------------------------------
    # Save Expense
    # -------------------------------------------------

    def save_expense(self):

        date = self.expense_date.date().toString("yyyy-MM-dd")

        exp_type = clean_text(self.expense_type.text())

        description = clean_text(self.expense_description.toPlainText())

        payee = clean_text(self.payee_name.text())

        phone1 = clean_contact(self.phone_1.text())
        phone2 = clean_contact(self.phone_2.text())

        amount = self.amount.value()

        # Payment Mode
        payment_mode = self.payment_mode.get_value()

        if not exp_type or not payee or amount <= 0:

            QMessageBox.warning(
                self,
                "Validation",
                "Type, Payee Name, and Amount are required."
            )
            return

        conn = None

        try:

            conn = get_db_connection()
            cursor = conn.cursor()

            if self.expense_id:

                cursor.execute("""
                    UPDATE expense SET
                        expense_date=?,
                        expense_type=?,
                        expense_description=?,
                        payee_name=?,
                        phone_1=?,
                        phone_2=?,
                        amount=?,
                        payment_mode=?,
                        is_active=?
                    WHERE expense_id=?
                """, (
                    date,
                    exp_type,
                    description,
                    payee,
                    phone1,
                    phone2,
                    amount,
                    payment_mode,
                    int(self.active.isChecked()),
                    self.expense_id
                ))

                log(f"✅ Updated expense ID {self.expense_id}")

            else:

                cursor.execute("""
                    INSERT INTO expense(
                        expense_date,
                        expense_type,
                        expense_description,
                        payee_name,
                        phone_1,
                        phone_2,
                        amount,
                        payment_mode,
                        is_active
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    date,
                    exp_type,
                    description,
                    payee,
                    phone1,
                    phone2,
                    amount,
                    payment_mode,
                    int(self.active.isChecked())
                ))

                log(f"✅ Inserted new expense: {payee} - ₹{amount:.2f}")

            conn.commit()

            self.accept()

        except Exception as e:

            log(f"❌ Failed to save expense: {e}")

            QMessageBox.critical(
                self,
                "Error",
                f"Database error: {e}"
            )

        finally:

            close_db_connection(conn)