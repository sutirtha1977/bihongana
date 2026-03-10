from PySide6.QtWidgets import (
    QMainWindow, QTreeWidget, QTreeWidgetItem, QStackedWidget, QSplitter,
    QWidget, QLabel, QVBoxLayout, QApplication
)
from PySide6.QtCore import Qt

from config.logger import log, clear_log
from config.paths import DB_FILE

from services_data.export_db import export_database
from ui.widgets.popups import show_info, show_error, confirm_action
from ui.master_data.customer_screen import CustomersScreen
from ui.master_data.seller_screen import SellersScreen
from ui.master_data.inventory_screen import InventoryScreen
from ui.master_data.owner_screen import OwnersScreen
from ui.master_data.expense_screen import ExpensesScreen
from ui.admin.admin_screen import AdminScreen
from ui.report_screen import ReportingScreen
from ui.dashboard_screen import DashboardScreen

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("BIHONGANA APP")
        self.setMinimumSize(1200, 700)

        clear_log()
        self.screens = {}

        self._init_ui()

    # ---------------- UI Setup ----------------
    def _init_ui(self):
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Sidebar
        self.sidebar = QTreeWidget()
        self.sidebar.setHeaderHidden(True)
        self.sidebar.setMinimumWidth(220)
        self.sidebar.setIndentation(15)
        self.sidebar.setAnimated(True)
        self.sidebar.setExpandsOnDoubleClick(False)
        self.sidebar.setStyleSheet("""
        QTreeWidget {
            background-color: #f8f9fa;
            border: none;
            font-size: 14px;
            padding: 6px;
        }
        QTreeWidget::item {
            height: 32px;
            padding-left: 12px;
            margin: 2px 0;
            border-radius: 4px;
            color: #2c3e50;
            font-weight: 500;
            background: transparent;
        }
        QTreeWidget::item:hover {
            background-color: #dfe6ed;
        }
        QTreeWidget::item:selected {
            background-color: #3498db;
            color: #fff;
            font-weight: 600;
        }
        QTreeWidget::item:has-children {
            font-weight: 600;
            color: #34495e;
        }
        """)
        self._create_sidebar()
        self.sidebar.itemClicked.connect(self._menu_clicked)

        # Workspace
        self.workspace = QStackedWidget()
        self._create_home_screen()

        # Splitter
        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.workspace)
        self.splitter.setSizes([220, 980])
        self.setCentralWidget(self.splitter)

    # ---------------- Sidebar ----------------
    def _create_sidebar(self):
        home = QTreeWidgetItem(["Home"])
        admin = QTreeWidgetItem(["Admin"])

        masters = QTreeWidgetItem(["Master Data"])
        masters.addChildren([
            QTreeWidgetItem(["Customers"]),
            QTreeWidgetItem(["Sellers"]),
            QTreeWidgetItem(["Inventory"]),
            QTreeWidgetItem(["Expenses"]),
            QTreeWidgetItem(["Owners"])
        ])

        reports = QTreeWidgetItem(["Reports"])
        reports.addChildren([
            QTreeWidgetItem(["Dashboard"]),
            QTreeWidgetItem(["Reporting"])
        ])
        export_db = QTreeWidgetItem(["Export Database"])
        
        exit_app = QTreeWidgetItem(["Exit"])

        self.sidebar.addTopLevelItems([home, admin, masters, reports, export_db, exit_app])

        # Collapse by default
        for item in [masters, reports]:
            self.sidebar.collapseItem(item)

    # ---------------- Home Screen ----------------
    def _create_home_screen(self):
        home_widget = QWidget()
        layout = QVBoxLayout(home_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(10)

        title = QLabel("BIHONGANA")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size:40px; font-weight:800; color:#2c3e50;")

        subtitle = QLabel("Where Style Meets Passion")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size:20px; font-weight:500; color:#34495e;")

        footer = QLabel("© 2026 Bihongana. All rights reserved.")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("font-size:12px; color:#7f8c8d;")

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()
        layout.addWidget(footer)

        self.screens["home"] = home_widget
        self.workspace.addWidget(home_widget)
        self.workspace.setCurrentWidget(home_widget)

    # ---------------- Screen Loader ----------------
    def _load_screen(self, name, widget):
        if name not in self.screens:
            self.screens[name] = widget
            self.workspace.addWidget(widget)
        self.workspace.setCurrentWidget(self.screens[name])

    # ---------------- Menu Handler ----------------
    def _menu_clicked(self, item):
        if item.childCount() > 0:
            item.setExpanded(not item.isExpanded())
            return

        action = item.text(0)
        log(f"Menu clicked: {action}")

        try:
            if action == "Home":
                self.workspace.setCurrentWidget(self.screens["home"])
            elif action == "Admin":
                self._load_screen("admin", AdminScreen())
            elif action == "Customers":
                self._load_screen("customers", CustomersScreen())
            elif action == "Sellers":
                self._load_screen("sellers", SellersScreen())
            elif action == "Inventory":
                self._load_screen("inventory", InventoryScreen())
            elif action == "Owners":
                self._load_screen("owners", OwnersScreen())
            elif action == "Expenses":
                self._load_screen("expenses", ExpensesScreen())
            elif action == "Reporting":
                self._load_screen("reporting", ReportingScreen())
            elif action == "Dashboard":
                self._load_screen("dashboard", DashboardScreen())
            elif action == "Export Database":
                export_database(self)
            elif action == "Exit":
                if confirm_action(self, "EXIT APPLICATION!!!", "EXIT APPLICATION"):
                    QApplication.quit()
            else:
                show_info(self, f"{action} NOT IMPLEMENTED YET.")
        except Exception as e:
            log(f"ERROR {action}: {e}")
            show_error(self, "OPERATION FAILED. CHECK LOG.")

    # ---------------- Helper ----------------
    def _check_database(self):
        if not DB_FILE.exists():
            show_error(self, "DATABASE NOT FOUND. PLEASE CREATE THE DATABASE FIRST.")
            raise Exception("DATABASE MISSING")