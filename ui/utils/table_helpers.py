from PySide6.QtWidgets import QTableWidgetItem


def populate_table(table, headers, rows):
    """
    Populate QTableWidget
    """

    table.clear()

    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setRowCount(len(rows))

    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            item = QTableWidgetItem("" if value is None else str(value))
            table.setItem(r, c, item)

    table.resizeColumnsToContents()