from config.logger import log
from database.connection import get_db_connection, close_db_connection


def create_inventory_database(drop_existing=False):
    """Create tables for the inventory management system, including expenses."""

    conn = get_db_connection()
    c = conn.cursor()

    # Drop order (child → parent)
    drop_order = [
        "sales",
        "inventory",
        "expense",
        "customer",
        "seller",
        "owner"
    ]

    try:
        c.execute("PRAGMA foreign_keys = ON")

        # -------------------
        # Drop existing tables
        # -------------------
        if drop_existing:
            log("⚠️ Dropping existing inventory tables...")

            c.execute("PRAGMA foreign_keys = OFF")

            for table in drop_order:
                log(f"Dropping table: {table}")
                c.execute(f"DROP TABLE IF EXISTS {table}")

            conn.commit()
            c.execute("PRAGMA foreign_keys = ON")
            log("✅ Existing tables dropped")

        # -------------------
        # Customer table
        # -------------------
        c.execute("""
        CREATE TABLE IF NOT EXISTS customer (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            unique_name TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            phone_1 TEXT,
            phone_2 TEXT,
            email TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            country TEXT,
            exhibition TEXT,
            customer_type TEXT,
            notes TEXT,
            birthday DATE,
            anniversary DATE,
            is_active BOOLEAN DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # -------------------
        # Owner table
        # -------------------
        c.execute("""
        CREATE TABLE IF NOT EXISTS owner (
            owner_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            first_name TEXT,
            last_name TEXT,
            phone_1 TEXT,
            phone_2 TEXT,
            email TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            country TEXT,
            paid_capital REAL,
            birthday DATE,
            anniversary DATE,
            is_active BOOLEAN DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # -------------------
        # Seller table
        # -------------------
        c.execute("""
        CREATE TABLE IF NOT EXISTS seller (
            seller_id INTEGER PRIMARY KEY AUTOINCREMENT,
            unique_name TEXT NOT NULL,
            shop_name TEXT,
            owner_name TEXT,
            selling_items TEXT,
            phone_1 TEXT,
            phone_2 TEXT,
            email TEXT,
            address TEXT,
            landmark TEXT,
            city TEXT,
            state TEXT,
            country TEXT,
            minimum_purchase TEXT,
            timings TEXT,
            notes TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # -------------------
        # Inventory table
        # -------------------
        c.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER NOT NULL,
            type TEXT,
            item_description TEXT,
            material TEXT,
            size TEXT,
            bill_no TEXT,
            purchase_price REAL,
            purchase_date TEXT DEFAULT CURRENT_TIMESTAMP,
            payment_mode TEXT,
            price_tag REAL,
            sold BOOLEAN DEFAULT 0,
            notes TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (seller_id) REFERENCES seller(seller_id)
        )
        """)

        # -------------------
        # Sales table
        # -------------------
        c.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            inventory_id INTEGER NOT NULL,
            customer_id INTEGER NOT NULL,
            sale_price REAL,
            sale_date TEXT DEFAULT CURRENT_TIMESTAMP,
            payment_mode TEXT,
            notes TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (inventory_id) REFERENCES inventory(inventory_id),
            FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
        )
        """)

        # -------------------
        # Expense table
        # -------------------
        c.execute("""
        CREATE TABLE IF NOT EXISTS expense (
            expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_date DATE,
            expense_type TEXT,
            expense_description TEXT,
            payee_name TEXT,
            phone_1 TEXT,
            phone_2 TEXT,
            amount REAL,
            payment_mode TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # -------------------
        # Indexes (performance)
        # -------------------
        c.execute("CREATE INDEX IF NOT EXISTS idx_inventory_seller ON inventory(seller_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_sales_inventory ON sales(inventory_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales(customer_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_expense_date ON expense(expense_date)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_expense_payee ON expense(payee_name)")

        conn.commit()
        log("🎉 Inventory database (including expense table) created successfully")

    except Exception as e:
        conn.rollback()
        log(f"❌ Database creation failed: {e}")
        raise

    finally:
        close_db_connection(conn)