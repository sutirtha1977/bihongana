# -------------------------
# Button styling helper
# -------------------------
def style_button(btn, color="#5c6bc0"):
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {color};
            color: white;
            border-radius: 6px;
            padding: 6px 16px;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background-color: #4f5bb5;
        }}
        QPushButton:pressed {{
            background-color: #434fa3;
        }}
    """)
# -------------------------
# Table styling
# -------------------------
TABLE_STYLE = """
QTableWidget {
    background-color: #ffffff;
    alternate-background-color: #fafbfc;
    gridline-color: #e4e7ea;
    border: 1px solid #e4e7ea;
}

QTableWidget::item {
    padding: 6px;
}

QTableWidget::item:selected {
    background-color: #e9eef6;
    color: #2c3e50;
}

QTableWidget::item:hover {
    background-color: #f4f6f8;
}

QHeaderView::section {
    background-color: #f7f9fb;
    color: #34495e;
    padding: 6px;
    font-weight: 600;
    border: none;
    border-bottom: 1px solid #e4e7ea;
}
"""
# -------------------------
# LineEdit styling
# -------------------------
LINEEDIT_STYLE = """
    QLineEdit {
        border: 1px solid #dcdcdc;
        border-radius: 6px;
        padding: 6px 10px;
        background: white;
    }
    QLineEdit:focus {
        border: 1px solid #3498db;
    }
"""