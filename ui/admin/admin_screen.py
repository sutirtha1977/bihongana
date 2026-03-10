from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QProgressBar
)
from PySide6.QtCore import Qt

from database.create_database import create_inventory_database
from services_data.import_customers import import_customers
from services_data.import_sellers import import_sellers
from services_data.import_inventory import import_inventory
from services_data.import_expense import import_expenses
from services_data.import_owners import import_owners

from ui.widgets.styles import style_button
from ui.widgets.popups import confirm_action


class AdminScreen(QWidget):

    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(12)

        # -------- Title --------
        title = QLabel("System Setup Console")
        title.setStyleSheet("font-size:24px; font-weight:700;")
        main_layout.addWidget(title)

        # -------- Toolbar --------
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        self.btn_db = QPushButton("Create Database")
        self.btn_customers = QPushButton("Import Customers")
        self.btn_sellers = QPushButton("Import Sellers")
        self.btn_inventory = QPushButton("Import Inventory")
        self.btn_expenses = QPushButton("Import Expenses")
        self.btn_owners = QPushButton("Import Owners")

        buttons = [
            self.btn_db,
            self.btn_customers,
            self.btn_sellers,
            self.btn_inventory,
            self.btn_expenses,
            self.btn_owners
        ]

        for btn in buttons:
            style_button(btn)
            toolbar.addWidget(btn)

        toolbar.addStretch()
        main_layout.addLayout(toolbar)

        # -------- Progress --------
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        main_layout.addWidget(self.progress)

        # -------- Log Panel --------
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("""
            QTextEdit {
                background:#1e1e1e;
                color:#dcdcdc;
                font-family: Consolas;
                font-size:13px;
                border:1px solid #e4e7ea;
            }
        """)
        main_layout.addWidget(self.log)

        # -------- Status --------
        self.status = QLabel("Ready")
        self.status.setStyleSheet("color:#7f8c8d;")
        main_layout.addWidget(self.status)

        # -------- Connect actions --------
        self.btn_db.clicked.connect(self.create_database)
        self.btn_customers.clicked.connect(self.import_customers)
        self.btn_sellers.clicked.connect(self.import_sellers)
        self.btn_inventory.clicked.connect(self.import_inventory)
        self.btn_expenses.clicked.connect(self.import_expenses)
        self.btn_owners.clicked.connect(self.import_owners)

    # -------- Logging helper --------
    def write_log(self, message):
        self.log.append(message)
        self.status.setText(message)

    # -------- Actions --------

    def create_database(self):

        if not confirm_action(self, "This will recreate the database.\nContinue?", "Create Database"):
            return

        self.write_log("Creating database...")
        create_inventory_database(drop_existing=True)
        self.write_log("Database created successfully.")

    def import_customers(self):

        if not confirm_action(self, "Import customers into the database?", "Import Customers"):
            return

        self.write_log("Importing customers...")
        count = import_customers()
        self.write_log(f"{count} customers imported.")

    def import_sellers(self):

        if not confirm_action(self, "Import sellers into the database?", "Import Sellers"):
            return

        self.write_log("Importing sellers...")
        count = import_sellers()
        self.write_log(f"{count} sellers imported.")

    def import_inventory(self):

        if not confirm_action(self, "Import inventory records?", "Import Inventory"):
            return

        self.write_log("Importing inventory...")
        count = import_inventory()
        self.write_log(f"{count} inventory records imported.")

    def import_expenses(self):

        if not confirm_action(self, "Import expenses into the database?", "Import Expenses"):
            return

        self.write_log("Importing expenses...")
        count = import_expenses()
        self.write_log(f"{count} expenses imported.")

    def import_owners(self):

        if not confirm_action(self, "Import owners into the database?", "Import Owners"):
            return

        self.write_log("Importing owners...")
        count = import_owners()
        self.write_log(f"{count} owners imported.")