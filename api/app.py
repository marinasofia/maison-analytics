"""
Maison Analytics — Flask API
Serves analytics endpoints from luxury_retail.db
"""

import sqlite3
import os
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["https://hearty-eagerness-production-4f43.up.railway.app", "http://localhost:3000"])

DB_PATH = os.environ.get("DB_PATH", "luxury_retail.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # rows behave like dicts: row["column_name"]
    return conn


# ─────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────

@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


# ─────────────────────────────────────────────
# KPI SUMMARY — top-line numbers for the header cards
# ─────────────────────────────────────────────

@app.route("/api/kpis")
def kpis():
    conn = get_db()
    row = conn.execute("""
        SELECT
            ROUND(SUM(net_revenue), 2)        AS total_revenue,
            COUNT(*)                           AS total_transactions,
            ROUND(AVG(net_revenue), 2)         AS avg_order_value,
            COUNT(DISTINCT customer_id)        AS active_customers
        FROM transactions
    """).fetchone()

    vic_ltv = conn.execute("""
        SELECT ROUND(AVG(lifetime_value), 2)
        FROM customers WHERE client_tier = 'VIC'
    """).fetchone()[0]

    # Pareto check: VIC revenue share
    vic_rev = conn.execute("""
        SELECT ROUND(SUM(t.net_revenue), 2)
        FROM transactions t
        JOIN customers c ON t.customer_id = c.customer_id
        WHERE c.client_tier = 'VIC'
    """).fetchone()[0]

    conn.close()
    return jsonify({
        "total_revenue":      row["total_revenue"],
        "total_transactions": row["total_transactions"],
        "avg_order_value":    row["avg_order_value"],
        "active_customers":   row["active_customers"],
        "vic_avg_ltv":        vic_ltv,
        "vic_revenue_share":  round(vic_rev / row["total_revenue"] * 100, 1),
    })


# ─────────────────────────────────────────────
# REVENUE BY MAISON
# ─────────────────────────────────────────────

@app.route("/api/revenue-by-maison")
def revenue_by_maison():
    conn = get_db()
    rows = conn.execute("""
        SELECT
            p.maison,
            ROUND(SUM(t.net_revenue), 2)  AS revenue,
            ROUND(SUM(t.margin_usd), 2)   AS margin,
            COUNT(*)                       AS transactions,
            ROUND(AVG(t.net_revenue), 2)  AS aov
        FROM transactions t
        JOIN products p ON t.sku = p.sku
        GROUP BY p.maison
        ORDER BY revenue DESC
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


# ─────────────────────────────────────────────
# REVENUE BY MONTH (seasonal trend)
# ─────────────────────────────────────────────

@app.route("/api/revenue-by-month")
def revenue_by_month():
    conn = get_db()
    rows = conn.execute("""
        SELECT
            STRFTIME('%Y-%m', transaction_date) AS month,
            ROUND(SUM(net_revenue), 2)          AS revenue,
            COUNT(*)                             AS transactions
        FROM transactions
        GROUP BY month
        ORDER BY month ASC
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


# ─────────────────────────────────────────────
# CLIENT TIER SUMMARY
# ─────────────────────────────────────────────

@app.route("/api/tier-summary")
def tier_summary():
    conn = get_db()
    rows = conn.execute("""
        SELECT
            c.client_tier,
            COUNT(DISTINCT c.customer_id)         AS customers,
            ROUND(AVG(c.lifetime_value), 2)        AS avg_ltv,
            ROUND(SUM(t.net_revenue), 2)           AS total_revenue,
            COUNT(t.transaction_id)                AS transactions,
            ROUND(AVG(t.net_revenue), 2)           AS avg_order_value
        FROM customers c
        LEFT JOIN transactions t ON c.customer_id = t.customer_id
        GROUP BY c.client_tier
        ORDER BY avg_ltv DESC
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


# ─────────────────────────────────────────────
# TOP PRODUCTS BY REVENUE
# ─────────────────────────────────────────────

@app.route("/api/top-products")
def top_products():
    limit = request.args.get("limit", 10, type=int)
    conn = get_db()
    rows = conn.execute(f"""
        SELECT
            p.sku,
            p.name,
            p.maison,
            p.category,
            p.base_price_usd,
            ROUND(SUM(t.net_revenue), 2)  AS revenue,
            SUM(t.quantity)                AS units_sold,
            ROUND(AVG(t.margin_usd / NULLIF(t.net_revenue, 0)) * 100, 1) AS margin_pct
        FROM transactions t
        JOIN products p ON t.sku = p.sku
        GROUP BY p.sku
        ORDER BY revenue DESC
        LIMIT {limit}
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


# ─────────────────────────────────────────────
# BOUTIQUE PERFORMANCE
# ─────────────────────────────────────────────

@app.route("/api/boutique-performance")
def boutique_performance():
    conn = get_db()
    rows = conn.execute("""
        SELECT
            b.boutique_id,
            b.name,
            b.city,
            b.country,
            b.maison,
            b.tier,
            ROUND(SUM(t.net_revenue), 2)  AS revenue,
            COUNT(t.transaction_id)        AS transactions,
            ROUND(AVG(t.net_revenue), 2)  AS aov,
            ROUND(SUM(t.margin_usd), 2)   AS total_margin
        FROM boutiques b
        LEFT JOIN transactions t ON b.boutique_id = t.boutique_id
        GROUP BY b.boutique_id
        ORDER BY revenue DESC
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


# ─────────────────────────────────────────────
# CHANNEL MIX
# ─────────────────────────────────────────────

@app.route("/api/channel-mix")
def channel_mix():
    conn = get_db()
    rows = conn.execute("""
        SELECT
            channel,
            ROUND(SUM(net_revenue), 2)  AS revenue,
            COUNT(*)                     AS transactions,
            ROUND(AVG(net_revenue), 2)  AS aov
        FROM transactions
        GROUP BY channel
        ORDER BY revenue DESC
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


# ─────────────────────────────────────────────
# INVENTORY — sell-through rate
# ─────────────────────────────────────────────

@app.route("/api/inventory")
def inventory():
    conn = get_db()
    rows = conn.execute("""
        SELECT
            i.boutique_id,
            b.city,
            p.name  AS product,
            p.category,
            i.units_received,
            i.units_sold,
            i.units_on_hand,
            ROUND(CAST(i.units_sold AS REAL) / NULLIF(i.units_received, 0) * 100, 1) AS sellthrough_pct
        FROM inventory i
        JOIN boutiques b ON i.boutique_id = b.boutique_id
        JOIN products  p ON i.sku         = p.sku
        ORDER BY sellthrough_pct DESC
        LIMIT 50
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
