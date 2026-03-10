from config.paths import BIHONGANA_XLSX
from services_data.helpers import import_from_excel, clean_name, clean_contact, clean_float, clean_date

def import_expenses():
    column_mapping = {
        "expense_date": "date",
        "expense_type": "expense_type",
        "expense_description": "expense_description",
        "payee_name": "payee_details",
        "phone_1": "phone_1",
        "phone_2": "phone_2",
        "amount": "amount"
    }

    clean_rules = {
        "expense_date": clean_date,
        "payee_name": clean_name,
        "phone_1": clean_contact,
        "phone_2": clean_contact,
        "amount": clean_float
    }

    return import_from_excel(
        str(BIHONGANA_XLSX),
        sheet_name="expense",
        table_name="expense",
        column_mapping=column_mapping,
        clean_rules=clean_rules
    )