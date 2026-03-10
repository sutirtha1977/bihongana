from PySide6.QtWidgets import QLabel, QHBoxLayout


def create_form_row(label_text, widget):

    layout = QHBoxLayout()

    label = QLabel(label_text)
    label.setMinimumWidth(150)

    layout.addWidget(label)
    layout.addWidget(widget)

    return layout