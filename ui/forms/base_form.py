from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QScrollArea, QWidget,
    QFormLayout, QPushButton, QHBoxLayout
)

from PySide6.QtCore import Qt

from ui.widgets.styles import style_button


class BaseForm(QDialog):

    def __init__(self, title, width=650, height=720):
        super().__init__()

        self.setWindowTitle(title)
        self.resize(width, height)
        self.setMinimumSize(600, 500)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # -------- Scroll Area --------
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        content = QWidget()

        self.form_layout = QFormLayout(content)
        self.form_layout.setSpacing(12)
        self.form_layout.setLabelAlignment(Qt.AlignRight)
        self.form_layout.setFormAlignment(Qt.AlignTop)

        # make labels aligned nicely
        self.form_layout.setHorizontalSpacing(20)
        self.form_layout.setVerticalSpacing(10)

        scroll.setWidget(content)

        self.main_layout.addWidget(scroll)

        # -------- Buttons --------
        buttons = QHBoxLayout()
        buttons.setSpacing(10)

        buttons.addStretch()

        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")

        self.save_btn.setMinimumWidth(120)
        self.cancel_btn.setMinimumWidth(120)

        style_button(self.save_btn, "#27ae60")
        style_button(self.cancel_btn, "#c0392b")

        self.cancel_btn.clicked.connect(self.close)

        buttons.addWidget(self.save_btn)
        buttons.addWidget(self.cancel_btn)

        self.main_layout.addLayout(buttons)