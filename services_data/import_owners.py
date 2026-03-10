from config.paths import BIHONGANA_XLSX
from services_data.helpers import import_from_excel, clean_name, clean_contact, clean_email, clean_date, clean_float

def import_owners():
    column_mapping = {
        "title": "title",
        "first_name": "first_name",
        "last_name": "last_name",
        "phone_1": "phone_1",
        "phone_2": "phone_2",
        "email": "email",
        "address": "address",
        "city": "city",
        "state": "state",
        "country": "country",
        "paid_capital": "paid_capital",
        "birthday": "birthday",
        "anniversary": "anniversary"
    }

    clean_rules = {
        "first_name": clean_name,
        "last_name": clean_name,
        "phone_1": clean_contact,
        "phone_2": clean_contact,
        "email": clean_email,
        "paid_capital": clean_float,
        "birthday": clean_date,
        "anniversary": clean_date
    }

    return import_from_excel(
        str(BIHONGANA_XLSX),
        sheet_name="owner",
        table_name="owner",
        column_mapping=column_mapping,
        clean_rules=clean_rules
    )