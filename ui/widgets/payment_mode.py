from PySide6.QtWidgets import QComboBox


class PaymentModeCombo(QComboBox):

    def __init__(self):
        super().__init__()

        self.addItems([
            "Cash",
            "UPI",
            "Bank Transfer",
            "Card",
            "Cheque",
            "Other"
        ])

    def set_value(self, value):

        if not value:
            return

        index = self.findText(value)

        if index >= 0:
            self.setCurrentIndex(index)

    def get_value(self):

        return self.currentText()