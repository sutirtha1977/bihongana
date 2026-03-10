import re


# =====================================================
# TEXT CLEANING
# =====================================================
def clean_text(val):
    if not val:
        return ""
    return str(val).strip().title()


def clean_email(val):
    if not val:
        return ""
    return str(val).strip().lower()


def clean_contact(val):
    """
    Cleans phone numbers and converts to international format
    """
    if not val:
        return ""

    val = str(val).strip()

    # remove everything except digits and +
    val = re.sub(r"[^\d+]", "", val)

    if val.startswith("+"):
        return val

    if val.startswith("91") and len(val) == 12:
        return f"+{val}"

    if len(val) == 10:
        return f"+91{val}"

    return val


# =====================================================
# VALIDATION
# =====================================================
def is_valid_email(email):
    if not email:
        return False

    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None


def is_valid_contact(contact):
    if not contact:
        return False

    digits = re.sub(r"\D", "", contact)

    return len(digits) >= 10