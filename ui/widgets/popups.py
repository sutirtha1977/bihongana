from PySide6.QtWidgets import QMessageBox, QPushButton

# ----------------------------------------
# Base Message
# ----------------------------------------
def _create_message(parent, title, text, icon, button_color="#3498db"):
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setIcon(icon)

    msg.setText(f"""
        <div style="
            font-size:14px;
            color:#2c3e50;
            line-height:1.5;
        ">
            {text}
        </div>
    """)

    # Simple, professional button styling
    msg.setStyleSheet(f"""
        QMessageBox {{
            background-color: #ffffff;
        }}
        QPushButton {{
            min-width: 90px;
            padding: 6px 14px;
            font-weight: 600;
            font-size: 13px;
            color: #ffffff;
            background-color: {button_color};
            border-radius: 4px;
        }}
        QPushButton:pressed {{
            background-color: #2c80b4;
        }}
    """)

    return msg


# ----------------------------------------
# Information
# ----------------------------------------
def show_info(parent, text: str, title="Information"):
    msg = _create_message(parent, title, text, QMessageBox.Information, button_color="#3498db")
    msg.exec()


# ----------------------------------------
# Success
# ----------------------------------------
def show_success(parent, text: str, title="Success"):
    msg = _create_message(parent, title, text, QMessageBox.Information, button_color="#27ae60")
    msg.exec()


# ----------------------------------------
# Warning
# ----------------------------------------
def show_warning(parent, text: str, title="Warning"):
    msg = _create_message(parent, title, text, QMessageBox.Warning, button_color="#e67e22")
    msg.exec()


# ----------------------------------------
# Error
# ----------------------------------------
def show_error(parent, text: str, title="Error"):
    msg = _create_message(parent, title, text, QMessageBox.Critical, button_color="#c0392b")
    msg.exec()


# ----------------------------------------
# Confirmation
# ----------------------------------------
def confirm_action(parent, text: str, title="Confirm Action") -> bool:
    msg = _create_message(parent, title, text, QMessageBox.Question)

    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg.setDefaultButton(QMessageBox.No)

    # Only change button colors
    yes_button = msg.button(QMessageBox.Yes)
    no_button = msg.button(QMessageBox.No)

    yes_button.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
    no_button.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold;")

    return msg.exec() == QMessageBox.Yes