import pandas as pd
import re
from config.logger import log
from database.connection import get_db_connection, close_db_connection

DATE_DEFAULT = "1900-01-01"

# -------------------------------------------------
# Helper functions
# -------------------------------------------------
def clean_text(val):
    return str(val).strip()

def clean_name(val):
    val = str(val).strip()
    return val.title() if val else ""

def clean_email(val):
    return str(val).strip().lower()

def clean_contact(val):
    if not val:
        return ""
    val = str(val).strip()
    val = re.sub(r"[^\d+]", "", val)
    if val.startswith("+"):
        return val
    if val.startswith("91") and len(val) == 12:
        return f"+{val}"
    if len(val) == 10:
        return f"+91{val}"
    return val

def clean_date(val):
    if not val:
        return DATE_DEFAULT
    try:
        return pd.to_datetime(val).strftime("%Y-%m-%d")
    except Exception:
        return DATE_DEFAULT

def clean_float(val):
    try:
        return float(val)
    except:
        return 0.0

def clean_int(val):
    try:
        return int(val)
    except:
        return 0

# -------------------------------------------------
# Generic Excel Import Engine
# -------------------------------------------------
def import_from_excel(file_path, sheet_name, table_name, column_mapping, clean_rules):
    log(f"📥 Import started → {sheet_name}")

    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, dtype=str).fillna("")
        log(f"✅ Excel loaded | rows={len(df)}")
    except Exception as e:
        log(f"❌ Excel read failed: {e}")
        return 0

    rows = []
    for idx, row in df.iterrows():
        row_data = []
        for db_col, excel_col in column_mapping.items():
            val = row.get(excel_col, "")
            clean_func = clean_rules.get(db_col, clean_text)
            row_data.append(clean_func(val))
        rows.append(tuple(row_data))

    if not rows:
        log(f"⚠ No rows to import for {table_name}")
        return 0

    conn = get_db_connection()
    cursor = conn.cursor()
    placeholders = ", ".join(["?"] * len(column_mapping))
    columns = ", ".join(column_mapping.keys())
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    try:
        cursor.executemany(sql, rows)
        conn.commit()
        log(f"🎉 {len(rows)} rows imported into {table_name}")
        return len(rows)
    except Exception as e:
        conn.rollback()
        log(f"❌ {table_name} import failed: {e}")
        return 0
    finally:
        close_db_connection(conn)