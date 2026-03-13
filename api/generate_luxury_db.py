"""
Luxury Retail Intelligence Database Generator
=============================================
Generates a realistic synthetic SQLite database for luxury retail analytics.
Maisons: Maison Aurore (fragrance/beauty), Maison Vellore (leather/RTW), Maison Eclat (jewelry/watches)

Requires: pip install faker

Usage:
    python generate_luxury_db.py              # clean database
    python generate_luxury_db.py --dirty      # injects realistic data quality issues

Output:
    luxury_retail.db  — SQLite database with 5 tables, ~6K+ transactions
    (with --dirty: also exports data/raw_clients.csv and data/raw_transactions.csv)
"""

import sqlite3
import random
import csv
import sys
import os
from datetime import datetime, timedelta
from faker import Faker

# ─────────────────────────────────────────────
# SEED FOR REPRODUCIBILITY
# ─────────────────────────────────────────────
random.seed(42)
fake = Faker()
Faker.seed(42)

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
NUM_CUSTOMERS    = 3_000
NUM_TRANSACTIONS = 50_000
START_DATE       = datetime(2022, 1, 1)
END_DATE         = datetime(2025, 12, 31)
DB_PATH          = "luxury_retail.db"
DIRTY_MODE       = "--dirty" in sys.argv

# ─────────────────────────────────────────────
# REFERENCE DATA
# ─────────────────────────────────────────────

MAISONS = {
    "Maison Aurore":  {"focus": "Fragrance & Beauty",   "code": "AUR"},
    "Maison Vellore": {"focus": "Leather Goods & RTW",  "code": "VEL"},
    "Maison Eclat":   {"focus": "Jewelry & Timepieces", "code": "ECL"},
}

# (boutique_id, name, city, country, maison, tier)
BOUTIQUES = [
    ("AUR-NYC", "Maison Aurore Fifth Avenue",        "New York",     "USA",          "Maison Aurore",  "Flagship"),
    ("AUR-PAR", "Maison Aurore Champs-Elysees",      "Paris",        "France",       "Maison Aurore",  "Flagship"),
    ("AUR-DXB", "Maison Aurore Dubai Mall",          "Dubai",        "UAE",          "Maison Aurore",  "Premium"),
    ("AUR-TKY", "Maison Aurore Ginza",               "Tokyo",        "Japan",        "Maison Aurore",  "Premium"),
    ("AUR-MIA", "Maison Aurore Bal Harbour",         "Miami",        "USA",          "Maison Aurore",  "Standard"),
    ("VEL-NYC", "Maison Vellore Madison Avenue",     "New York",     "USA",          "Maison Vellore", "Flagship"),
    ("VEL-PAR", "Maison Vellore Rue Saint-Honore",   "Paris",        "France",       "Maison Vellore", "Flagship"),
    ("VEL-HKG", "Maison Vellore Landmark",           "Hong Kong",    "China",        "Maison Vellore", "Flagship"),
    ("VEL-LAX", "Maison Vellore Rodeo Drive",        "Los Angeles",  "USA",          "Maison Vellore", "Premium"),
    ("VEL-SGP", "Maison Vellore Marina Bay",         "Singapore",    "Singapore",    "Maison Vellore", "Premium"),
    ("ECL-NYC", "Maison Eclat Plaza Athenee",        "New York",     "USA",          "Maison Eclat",   "Flagship"),
    ("ECL-PAR", "Maison Eclat Place Vendome",        "Paris",        "France",       "Maison Eclat",   "Flagship"),
    ("ECL-GVA", "Maison Eclat Rue du Rhone",         "Geneva",       "Switzerland",  "Maison Eclat",   "Flagship"),
    ("ECL-DXB", "Maison Eclat The Dubai Mall",       "Dubai",        "UAE",          "Maison Eclat",   "Premium"),
    ("ECL-TKY", "Maison Eclat Omotesando",           "Tokyo",        "Japan",        "Maison Eclat",   "Premium"),
]

# (sku, name, maison, category, subcategory, base_price_usd, margin_pct)
PRODUCTS = [
    # ── Maison Aurore ─────────────────────────────────────────────────
    ("AUR-FRG-001", "Nuit Doree Eau de Parfum 100ml",     "Maison Aurore", "Fragrance",    "Signature",    320,    0.78),
    ("AUR-FRG-002", "Lumiere Blanche Eau de Parfum 50ml", "Maison Aurore", "Fragrance",    "Signature",    245,    0.76),
    ("AUR-FRG-003", "Absolu de Roses 200ml",              "Maison Aurore", "Fragrance",    "Collection",   580,    0.80),
    ("AUR-FRG-004", "Eclat Vert Travel Set",              "Maison Aurore", "Fragrance",    "Travel",       195,    0.72),
    ("AUR-SKN-001", "Serum Precieux 30ml",                "Maison Aurore", "Skincare",     "Serum",        420,    0.82),
    ("AUR-SKN-002", "Creme Royale 50ml",                  "Maison Aurore", "Skincare",     "Moisturizer",  310,    0.80),
    ("AUR-SKN-003", "Huile Lumiere Face Oil 30ml",        "Maison Aurore", "Skincare",     "Oil",          285,    0.79),
    ("AUR-MKP-001", "Rouge Absolue Lipstick",             "Maison Aurore", "Makeup",       "Lip",           68,    0.70),
    ("AUR-MKP-002", "Fond de Teint Satin Foundation",     "Maison Aurore", "Makeup",       "Face",          95,    0.71),
    ("AUR-MKP-003", "Palette Lumiere Eyeshadow",          "Maison Aurore", "Makeup",       "Eye",          145,    0.73),
    ("AUR-GFT-001", "Aurore Discovery Set",               "Maison Aurore", "Gift Set",     "Fragrance",    480,    0.75),
    ("AUR-GFT-002", "La Beaute Gift Box",                 "Maison Aurore", "Gift Set",     "Skincare",     650,    0.77),
    # ── Maison Vellore ────────────────────────────────────────────────
    ("VEL-LTH-001", "Tote Venitien in Grain Leather",     "Maison Vellore","Leather Goods","Tote",        2800,    0.68),
    ("VEL-LTH-002", "Pochette Classique",                 "Maison Vellore","Leather Goods","Clutch",       950,    0.65),
    ("VEL-LTH-003", "Sac a Dos Souple",                   "Maison Vellore","Leather Goods","Backpack",    3400,    0.70),
    ("VEL-LTH-004", "Portefeuille Long",                  "Maison Vellore","Leather Goods","Wallet",       480,    0.63),
    ("VEL-LTH-005", "Card Holder Emboss",                 "Maison Vellore","Leather Goods","Accessory",    220,    0.60),
    ("VEL-RTW-001", "Manteau Cachemire Double Face",       "Maison Vellore","RTW",          "Outerwear",   5200,    0.65),
    ("VEL-RTW-002", "Robe Soir en Soie",                  "Maison Vellore","RTW",          "Dress",       2100,    0.63),
    ("VEL-RTW-003", "Blazer Structure Laine Vierge",      "Maison Vellore","RTW",          "Tailoring",   1850,    0.62),
    ("VEL-SHO-001", "Escarpins Eternels 85mm",            "Maison Vellore","Shoes",        "Heels",        890,    0.60),
    ("VEL-SHO-002", "Derby Couture Cuir Veau",            "Maison Vellore","Shoes",        "Flats",        750,    0.59),
    ("VEL-ACC-001", "Foulard Carre en Soie 90cm",         "Maison Vellore","Accessories",  "Scarf",        480,    0.72),
    ("VEL-ACC-002", "Ceinture Signature Reversible",      "Maison Vellore","Accessories",  "Belt",         620,    0.68),
    # ── Maison Eclat ──────────────────────────────────────────────────
    ("ECL-JWL-001", "Bague Etoile en Or 18k Diamants",    "Maison Eclat",  "Jewelry",      "Ring",        4800,    0.55),
    ("ECL-JWL-002", "Collier Cascade Perles et Or",       "Maison Eclat",  "Jewelry",      "Necklace",    7200,    0.57),
    ("ECL-JWL-003", "Bracelet Jonc Or Jaune 18k",         "Maison Eclat",  "Jewelry",      "Bracelet",    3100,    0.54),
    ("ECL-JWL-004", "Boucles d Oreilles Solitaire",       "Maison Eclat",  "Jewelry",      "Earrings",    2650,    0.53),
    ("ECL-JWL-005", "Parure Royale Rubis et Diamants",    "Maison Eclat",  "Jewelry",      "Set",        28000,    0.50),
    ("ECL-WTC-001", "Chronographe Automatique 40mm",      "Maison Eclat",  "Timepieces",   "Sport",      12500,    0.52),
    ("ECL-WTC-002", "Montre Dress Or Rose Dame",          "Maison Eclat",  "Timepieces",   "Dress",       8900,    0.51),
    ("ECL-WTC-003", "Tourbillon Grande Complication",     "Maison Eclat",  "Timepieces",   "Haute",      95000,    0.48),
    ("ECL-WTC-004", "Montre Acier Bracelet Milanais",     "Maison Eclat",  "Timepieces",   "Sport",       4200,    0.53),
    ("ECL-ACC-001", "Stylo Plume Or Massif",              "Maison Eclat",  "Accessories",  "Writing",     1800,    0.60),
    ("ECL-ACC-002", "Agenda Cuir Maroquinerie",           "Maison Eclat",  "Accessories",  "Stationery",   680,    0.62),
]

CLIENT_TIERS = ["Standard", "Premium", "VIC"]
CHANNELS     = ["In-Store", "E-Commerce", "Private Appointment", "Pop-Up Event"]
CURRENCIES   = {
    "USA": "USD", "France": "EUR", "UAE": "AED",
    "Japan": "JPY", "China": "HKD", "Singapore": "SGD", "Switzerland": "CHF"
}

# Locales that match our boutique countries — gives realistic international names
FAKER_LOCALES = ["en_US", "fr_FR", "ja_JP", "zh_CN", "ar_AA", "de_DE", "en_GB"]


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def rand_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def seasonal_weight(dt: datetime) -> float:
    """Realistic luxury spend patterns: holiday spike, Valentine's, Mother's Day, summer dip."""
    m = dt.month
    if m in (11, 12): return 2.2
    if m == 2:        return 1.5
    if m == 5:        return 1.3
    if m in (6, 7):   return 0.8
    return 1.0


def get_faker_for_country(country: str) -> Faker:
    """Return a locale-appropriate Faker instance for realistic names per country."""
    locale_map = {
        "USA":         "en_US",
        "France":      "fr_FR",
        "Japan":       "ja_JP",
        "China":       "zh_CN",
        "UAE":         "ar_AA",
        "Switzerland": "de_DE",
        "Singapore":   "en_GB",
    }
    locale = locale_map.get(country, "en_US")
    try:
        return Faker(locale)
    except Exception:
        return Faker("en_US")


def generate_customer_identity(country: str, seen_emails: set) -> tuple:
    """Generate a unique (first_name, last_name, email) using faker."""
    local_fake = get_faker_for_country(country)
    first = local_fake.first_name()
    last  = local_fake.last_name()

    # Build email from name — more realistic than faker's random emails
    domains = ["gmail.com", "icloud.com", "outlook.com", "pm.me", "proton.me", "me.com"]
    def clean(s):
        import unicodedata
        # Normalize accented characters to ASCII equivalents
        s = unicodedata.normalize("NFKD", s)
        s = s.encode("ascii", "ignore").decode("ascii")
        return s.lower().replace(" ", "").replace("-", "").replace("'", "")

    sep    = random.choice([".", "_", ""])
    suffix = random.choice(["", str(random.randint(1, 99))])
    email  = f"{clean(first)}{sep}{clean(last)}{suffix}@{random.choice(domains)}"

    # Guarantee uniqueness
    attempts = 0
    while email in seen_emails:
        suffix = str(random.randint(100, 9999))
        email  = f"{clean(first)}{sep}{clean(last)}{suffix}@{random.choice(domains)}"
        attempts += 1
        if attempts > 20:
            email = fake.unique.email()  # fallback to faker's unique generator
            break

    seen_emails.add(email)
    return first, last, email


# ─────────────────────────────────────────────
# SCHEMA
# ─────────────────────────────────────────────

def create_schema(conn: sqlite3.Connection):
    conn.executescript("""
    PRAGMA journal_mode=WAL;

    CREATE TABLE IF NOT EXISTS boutiques (
        boutique_id     TEXT PRIMARY KEY,
        name            TEXT NOT NULL,
        city            TEXT NOT NULL,
        country         TEXT NOT NULL,
        maison          TEXT NOT NULL,
        tier            TEXT NOT NULL,
        currency        TEXT NOT NULL,
        opened_year     INTEGER
    );

    CREATE TABLE IF NOT EXISTS products (
        sku             TEXT PRIMARY KEY,
        name            TEXT NOT NULL,
        maison          TEXT NOT NULL,
        category        TEXT NOT NULL,
        subcategory     TEXT NOT NULL,
        base_price_usd  REAL NOT NULL,
        margin_pct      REAL NOT NULL,
        is_active       INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS customers (
        customer_id      TEXT PRIMARY KEY,
        first_name       TEXT NOT NULL,
        last_name        TEXT NOT NULL,
        email            TEXT UNIQUE,
        country          TEXT,
        client_tier      TEXT NOT NULL,
        acquisition_date TEXT NOT NULL,
        preferred_maison TEXT,
        lifetime_value   REAL DEFAULT 0,
        total_orders     INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id   TEXT PRIMARY KEY,
        customer_id      TEXT NOT NULL,
        boutique_id      TEXT NOT NULL,
        sku              TEXT NOT NULL,
        transaction_date TEXT NOT NULL,
        quantity         INTEGER NOT NULL,
        unit_price_usd   REAL NOT NULL,
        discount_pct     REAL DEFAULT 0,
        channel          TEXT NOT NULL,
        gross_revenue    REAL NOT NULL,
        net_revenue      REAL NOT NULL,
        margin_usd       REAL NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (boutique_id) REFERENCES boutiques(boutique_id),
        FOREIGN KEY (sku)         REFERENCES products(sku)
    );

    CREATE TABLE IF NOT EXISTS inventory (
        inventory_id    TEXT PRIMARY KEY,
        boutique_id     TEXT NOT NULL,
        sku             TEXT NOT NULL,
        stock_date      TEXT NOT NULL,
        units_received  INTEGER DEFAULT 0,
        units_sold      INTEGER DEFAULT 0,
        units_on_hand   INTEGER DEFAULT 0,
        reorder_point   INTEGER DEFAULT 5,
        FOREIGN KEY (boutique_id) REFERENCES boutiques(boutique_id),
        FOREIGN KEY (sku)         REFERENCES products(sku)
    );

    CREATE INDEX IF NOT EXISTS idx_txn_date     ON transactions(transaction_date);
    CREATE INDEX IF NOT EXISTS idx_txn_customer ON transactions(customer_id);
    CREATE INDEX IF NOT EXISTS idx_txn_boutique ON transactions(boutique_id);
    CREATE INDEX IF NOT EXISTS idx_txn_sku      ON transactions(sku);
    """)
    conn.commit()
    print("✓ Schema created")


# ─────────────────────────────────────────────
# SEEDERS
# ─────────────────────────────────────────────

def seed_boutiques(conn: sqlite3.Connection):
    rows = []
    for bid, name, city, country, maison, tier in BOUTIQUES:
        currency    = CURRENCIES.get(country, "USD")
        opened_year = random.randint(1998, 2018)
        rows.append((bid, name, city, country, maison, tier, currency, opened_year))
    conn.executemany("INSERT OR IGNORE INTO boutiques VALUES (?,?,?,?,?,?,?,?)", rows)
    conn.commit()
    print(f"✓ Seeded {len(rows)} boutiques")


def seed_products(conn: sqlite3.Connection):
    rows = [(sku, name, maison, cat, subcat, price, margin, 1)
            for sku, name, maison, cat, subcat, price, margin in PRODUCTS]
    conn.executemany("INSERT OR IGNORE INTO products VALUES (?,?,?,?,?,?,?,?)", rows)
    conn.commit()
    print(f"✓ Seeded {len(rows)} products")


def seed_customers(conn: sqlite3.Connection) -> list:
    boutique_countries = [b[3] for b in BOUTIQUES]
    maison_list        = list(MAISONS.keys())

    # Realistic tier distribution: 70% Standard, 22% Premium, 8% VIC
    tier_pool = ["Standard"] * 70 + ["Premium"] * 22 + ["VIC"] * 8

    rows         = []
    customer_ids = []
    seen_emails  = set()

    print(f"  Generating {NUM_CUSTOMERS:,} customers with faker...", end="", flush=True)

    for i in range(NUM_CUSTOMERS):
        cid         = f"CUST-{i+1:05d}"
        country     = random.choice(boutique_countries)
        tier        = random.choice(tier_pool)
        acq_date    = rand_date(START_DATE, END_DATE - timedelta(days=180))
        pref_maison = random.choice(maison_list)

        first, last, email = generate_customer_identity(country, seen_emails)

        rows.append((cid, first, last, email, country, tier,
                     acq_date.strftime("%Y-%m-%d"), pref_maison, 0.0, 0))
        customer_ids.append((cid, tier, pref_maison, acq_date))

        if (i + 1) % 500 == 0:
            print(f" {i+1}", end="", flush=True)

    print()
    conn.executemany("INSERT OR IGNORE INTO customers VALUES (?,?,?,?,?,?,?,?,?,?)", rows)
    conn.commit()
    print(f"✓ Seeded {len(rows):,} customers")
    return customer_ids


def seed_transactions(conn: sqlite3.Connection, customer_ids: list):
    boutique_map = {}
    for bid, _, _, _, maison, _ in BOUTIQUES:
        boutique_map.setdefault(maison, []).append(bid)

    product_map = {}
    for sku, _, maison, _, _, price, margin in PRODUCTS:
        product_map.setdefault(maison, []).append((sku, price, margin))

    channel_weights = {
        "Standard": [0.55, 0.35, 0.05, 0.05],
        "Premium":  [0.50, 0.30, 0.15, 0.05],
        "VIC":      [0.35, 0.10, 0.50, 0.05],
    }
    # VIC clients transact 12x more than Standard — realistic luxury CRM behavior
    purchase_freq = {"Standard": 1, "Premium": 3, "VIC": 12}

    txn_rows     = []
    cust_updates = {}
    txn_count    = 0
    txn_index    = 0

    for cid, tier, pref_maison, acq_date in customer_ids:
        base_orders = purchase_freq[tier]
        n_orders    = max(1, int(random.gauss(base_orders, base_orders * 0.5)))
        cust_ltv    = 0.0
        cust_orders = 0

        for _ in range(n_orders):
            if txn_count >= NUM_TRANSACTIONS:
                break

            maison      = pref_maison if random.random() < 0.6 else random.choice(list(MAISONS.keys()))
            boutique_id = random.choice(boutique_map[maison])
            sku, base_price, margin = random.choice(product_map[maison])

            txn_date   = rand_date(acq_date, END_DATE)
            season_w   = seasonal_weight(txn_date)
            unit_price = base_price * random.uniform(0.97, 1.03)
            qty        = random.choices([1, 2, 3], weights=[0.80, 0.15, 0.05])[0]

            # Discounts are rare in luxury — VICs occasionally get private client pricing
            discount = 0.0
            if tier == "VIC" and random.random() < 0.08:
                discount = random.choice([0.05, 0.10])
            elif tier == "Standard" and random.random() < 0.03:
                discount = 0.05

            channel = random.choices(CHANNELS, weights=channel_weights[tier])[0]

            # Seasonal volume boost
            if random.random() < (season_w - 1) * 0.5:
                qty = min(qty + 1, 4)

            gross_rev  = round(unit_price * qty, 2)
            net_rev    = round(gross_rev * (1 - discount), 2)
            margin_usd = round(net_rev * margin, 2)

            txn_rows.append((
                f"TXN-{txn_index+1:07d}", cid, boutique_id, sku,
                txn_date.strftime("%Y-%m-%d %H:%M:%S"),
                qty, round(unit_price, 2), round(discount, 2), channel,
                gross_rev, net_rev, margin_usd
            ))

            cust_ltv    += net_rev
            cust_orders += 1
            txn_count   += 1
            txn_index   += 1

        cust_updates[cid] = (round(cust_ltv, 2), cust_orders)
        if txn_count >= NUM_TRANSACTIONS:
            break

    conn.executemany(
        "INSERT OR IGNORE INTO transactions VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", txn_rows
    )
    conn.executemany(
        "UPDATE customers SET lifetime_value=?, total_orders=? WHERE customer_id=?",
        [(v[0], v[1], k) for k, v in cust_updates.items()]
    )
    conn.commit()
    print(f"✓ Seeded {len(txn_rows):,} transactions")


def seed_inventory(conn: sqlite3.Connection):
    sold_map = {}
    for row in conn.execute(
        "SELECT boutique_id, sku, SUM(quantity) FROM transactions GROUP BY boutique_id, sku"
    ):
        sold_map[(row[0], row[1])] = row[2]

    rows   = []
    inv_id = 1
    for bid, _, _, _, maison, tier in BOUTIQUES:
        for sku, _, pmaison, _, _, _, _ in PRODUCTS:
            if pmaison != maison:
                continue
            total_sold = sold_map.get((bid, sku), 0)
            received   = total_sold + random.randint(5, 30)
            on_hand    = received - total_sold
            reorder_pt = 5 if tier == "Standard" else 3
            rows.append((f"INV-{inv_id:06d}", bid, sku,
                         END_DATE.strftime("%Y-%m-%d"),
                         received, total_sold, on_hand, reorder_pt))
            inv_id += 1

    conn.executemany("INSERT OR IGNORE INTO inventory VALUES (?,?,?,?,?,?,?,?)", rows)
    conn.commit()
    print(f"✓ Seeded {len(rows)} inventory records")


# ─────────────────────────────────────────────
# DIRTY DATA INJECTION
# ─────────────────────────────────────────────

def inject_dirty_data(conn: sqlite3.Connection):
    """
    Injects realistic data quality issues and exports dirty CSVs for ETL demos.
    Issues: duplicate rows, null emails, malformed dates,
            negative prices, null SKUs, inconsistent boutique ID casing.
    """
    print("\n  Injecting dirty data for ETL demo...")

    customers = conn.execute("SELECT * FROM customers").fetchall()
    cust_cols = [d[0] for d in conn.execute("SELECT * FROM customers LIMIT 0").description]
    dirty_customers = [list(r) for r in customers]

    dup_count = max(1, int(len(dirty_customers) * 0.03))
    dirty_customers.extend(random.sample(dirty_customers, dup_count))
    print(f"    + {dup_count} duplicate customer rows")

    null_email_count = max(1, int(len(dirty_customers) * 0.04))
    email_idx = cust_cols.index("email")
    for idx in random.sample(range(len(dirty_customers)), null_email_count):
        dirty_customers[idx][email_idx] = ""
    print(f"    + {null_email_count} null emails")

    bad_date_count = max(1, int(len(dirty_customers) * 0.05))
    acq_idx = cust_cols.index("acquisition_date")
    for idx in random.sample(range(len(dirty_customers)), bad_date_count):
        try:
            d = datetime.strptime(dirty_customers[idx][acq_idx], "%Y-%m-%d")
            dirty_customers[idx][acq_idx] = d.strftime("%m/%d/%Y")
        except Exception:
            pass
    print(f"    + {bad_date_count} malformed acquisition dates")

    transactions = conn.execute("SELECT * FROM transactions").fetchall()
    txn_cols     = [d[0] for d in conn.execute("SELECT * FROM transactions LIMIT 0").description]
    dirty_txns   = [list(r) for r in transactions]

    neg_count = max(1, int(len(dirty_txns) * 0.01))
    price_idx = txn_cols.index("unit_price_usd")
    gross_idx = txn_cols.index("gross_revenue")
    net_idx   = txn_cols.index("net_revenue")
    for idx in random.sample(range(len(dirty_txns)), neg_count):
        dirty_txns[idx][price_idx] *= -1
        dirty_txns[idx][gross_idx] *= -1
        dirty_txns[idx][net_idx]   *= -1
    print(f"    + {neg_count} negative transaction amounts")

    null_sku_count = max(1, int(len(dirty_txns) * 0.02))
    sku_idx = txn_cols.index("sku")
    for idx in random.sample(range(len(dirty_txns)), null_sku_count):
        dirty_txns[idx][sku_idx] = ""
    print(f"    + {null_sku_count} null SKUs")

    case_count = max(1, int(len(dirty_txns) * 0.03))
    bout_idx   = txn_cols.index("boutique_id")
    for idx in random.sample(range(len(dirty_txns)), case_count):
        dirty_txns[idx][bout_idx] = dirty_txns[idx][bout_idx].lower()
    print(f"    + {case_count} inconsistent boutique ID casings")

    os.makedirs("data", exist_ok=True)
    with open("data/raw_clients.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows([cust_cols] + dirty_customers)
    with open("data/raw_transactions.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows([txn_cols] + dirty_txns)

    print(f"\n  Dirty CSVs exported:")
    print(f"    data/raw_clients.csv      ({len(dirty_customers):,} rows)")
    print(f"    data/raw_transactions.csv ({len(dirty_txns):,} rows)")


# ─────────────────────────────────────────────
# VALIDATION REPORT
# ─────────────────────────────────────────────

def validate(conn: sqlite3.Connection):
    print("\n─── Database Summary ───────────────────────────")
    for label, q in [
        ("boutiques",     "SELECT COUNT(*) FROM boutiques"),
        ("products",      "SELECT COUNT(*) FROM products"),
        ("customers",     "SELECT COUNT(*) FROM customers"),
        ("transactions",  "SELECT COUNT(*) FROM transactions"),
        ("inventory",     "SELECT COUNT(*) FROM inventory"),
        ("total_revenue", "SELECT ROUND(SUM(net_revenue),2) FROM transactions"),
        ("avg_order_val", "SELECT ROUND(AVG(net_revenue),2) FROM transactions"),
    ]:
        r = conn.execute(q).fetchone()[0]
        print(f"  {label:<20} {r:>15,}" if isinstance(r, int) else f"  {label:<20} ${r:>14,.2f}")

    print("\n─── Revenue by Maison ──────────────────────────")
    for row in conn.execute("""
        SELECT p.maison, ROUND(SUM(t.net_revenue),2) as rev
        FROM transactions t JOIN products p ON t.sku=p.sku
        GROUP BY p.maison ORDER BY rev DESC
    """):
        print(f"  {row[0]:<25} ${row[1]:>14,.2f}")

    print("\n─── Client Tier Summary ────────────────────────")
    for row in conn.execute("""
        SELECT client_tier, COUNT(*) as n, ROUND(AVG(lifetime_value),2) as avg_ltv
        FROM customers GROUP BY client_tier ORDER BY avg_ltv DESC
    """):
        print(f"  {row[0]:<12} {row[1]:>6} customers   Avg LTV: ${row[2]:>10,.2f}")

    print("\n─── Top 5 Products by Revenue ──────────────────")
    for row in conn.execute("""
        SELECT p.name, ROUND(SUM(t.net_revenue),2) as rev
        FROM transactions t JOIN products p ON t.sku=p.sku
        GROUP BY p.sku ORDER BY rev DESC LIMIT 5
    """):
        print(f"  {row[0]:<42} ${row[1]:>12,.2f}")

    print("\n─── Revenue by Channel ─────────────────────────")
    for row in conn.execute("""
        SELECT channel, ROUND(SUM(net_revenue),2) as rev, COUNT(*) as txns
        FROM transactions GROUP BY channel ORDER BY rev DESC
    """):
        print(f"  {row[0]:<25} ${row[1]:>12,.2f}  ({row[2]:,} txns)")
    print("────────────────────────────────────────────────\n")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    label = " [DIRTY MODE]" if DIRTY_MODE else ""
    print(f"\n🏛  Luxury Retail Intelligence Database Generator{label}")
    print(f"    Output: {DB_PATH}\n")

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    try:
        create_schema(conn)
        seed_boutiques(conn)
        seed_products(conn)
        customer_ids = seed_customers(conn)
        seed_transactions(conn, customer_ids)
        seed_inventory(conn)
        if DIRTY_MODE:
            inject_dirty_data(conn)
        validate(conn)
        print(f"✅  Database ready: {DB_PATH}")
        if DIRTY_MODE:
            print(f"📂  Dirty CSVs: data/raw_clients.csv  data/raw_transactions.csv")
    finally:
        conn.close()


if __name__ == "__main__":
    main()