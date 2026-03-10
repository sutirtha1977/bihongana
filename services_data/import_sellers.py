from config.paths import BIHONGANA_XLSX
from services_data.helpers import import_from_excel, clean_name, clean_contact, clean_email, clean_text

def import_sellers():
    column_mapping = {
        "unique_name": "unique_name",
        "shop_name": "shop_name",
        "owner_name": "owner_name",
        "selling_items": "selling_items",
        "phone_1": "phone_1",
        "phone_2": "phone_2",
        "email": "email",
        "address": "address",
        "landmark": "landmark",
        "city": "city",
        "state": "state",
        "country": "country",
        "minimum_purchase": "minimum_purchase",
        "timings": "timings",
        "notes": "notes"
    }
    clean_rules = {
        "unique_name": clean_name,
        "shop_name": clean_name,
        "owner_name": clean_name,
        "selling_items": clean_text,
        "phone_1": clean_contact,
        "phone_2": clean_contact,
        "email": clean_email
    }
    return import_from_excel(str(BIHONGANA_XLSX), "seller", "seller", column_mapping, clean_rules)
