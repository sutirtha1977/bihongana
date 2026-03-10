import sys
from PySide6.QtWidgets import QApplication

from main_window import MainWindow
from config.logger import log


def main():
    log("Application started")

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()