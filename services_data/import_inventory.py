import pandas as pd
from config.logger import log
from config.paths import BIHONGANA_XLSX
from database.connection import get_db_connection, close_db_connection
from services_data.helpers import clean_text,clean_float,clean_int,clean_date, clean_name

def import_inventory():
    log("📥 Import started → inventory")

    try:
        df = pd.read_excel(BIHONGANA_XLSX, sheet_name="inventory", dtype=str).fillna("")
        log(f"✅ Excel loaded | rows={len(df)}")
    except Exception as e:
        log(f"❌ Excel read failed: {e}")
        return 0

    conn = get_db_connection()
    cursor = conn.cursor()
    rows = []
    warnings = 0

    for idx, row in df.iterrows():
        shop_name_excel = str(row.get("shop_name", "")).strip()
        cursor.execute("SELECT seller_id FROM seller WHERE UPPER(unique_name) = ?", (shop_name_excel.upper(),))
        seller_row = cursor.fetchone()
        seller_id = seller_row[0] if seller_row else 0
        if seller_id == 0:
            warnings += 1
            log(f"⚠ Seller not found: '{shop_name_excel}' → seller_id=0")

        try:
            row_data = (
                seller_id,
                clean_name(row.get("type", "")),
                clean_text(row.get("item_description", "")),
                clean_name(row.get("material", "")),
                clean_text(row.get("size", "")),
                clean_text(row.get("bill_no", "")),
                clean_float(row.get("purchase_price", 0)),
                clean_date(row.get("purchase_date", "")),
                clean_text(row.get("payment_mode", "")),
                clean_float(row.get("price_tag", 0)),
                clean_int(row.get("sold", 0)),
                clean_text(row.get("notes", "")),
                1  # default is_active
            )
        except Exception as e:
            log(f"❌ Error parsing row {idx}: {e}")
            continue

        rows.append(row_data)

    if not rows:
        log("⚠ No inventory rows to import")
        return 0

    columns = (
        "seller_id, type, item_description, material, size, bill_no, "
        "purchase_price, purchase_date, payment_mode, price_tag, sold, notes, is_active"
    )
    placeholders = ", ".join(["?"] * 13)
    sql = f"INSERT INTO inventory ({columns}) VALUES ({placeholders})"

    try:
        cursor.executemany(sql, rows)
        conn.commit()
        log(f"🎉 {len(rows)} inventory rows imported (warnings: {warnings})")
        return len(rows)
    except Exception as e:
        conn.rollback()
        log(f"❌ Inventory import failed: {e}")
        return 0
    finally:
        close_db_connection(conn)