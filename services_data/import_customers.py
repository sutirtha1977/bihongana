from config.paths import BIHONGANA_XLSX
from services_data.helpers import import_from_excel, clean_name, clean_contact, clean_email, clean_date

def import_customers():
    column_mapping = {
        "title": "title",
        "unique_name": "unique_name",
        "first_name": "first_name",
        "last_name": "last_name",
        "phone_1": "phone_1",
        "phone_2": "phone_2",
        "email": "email",
        "address": "address",
        "city": "city",
        "state": "state",
        "country": "country",
        "exhibition": "exhibition",
        "customer_type": "customer_type",
        "notes": "notes",
        "birthday": "birthday",
        "anniversary": "anniversary"
    }
    clean_rules = {
        "unique_name": clean_name,
        "first_name": clean_name,
        "last_name": clean_name,
        "phone_1": clean_contact,
        "phone_2": clean_contact,
        "email": clean_email,
        "birthday": clean_date,
        "anniversary": clean_date
    }
    return import_from_excel(str(BIHONGANA_XLSX), "customer", "customer", column_mapping, clean_rules)