# Maison Analytics

A synthetic luxury retail intelligence platform built to demonstrate data analytics skills for luxury sector internship applications.

**Stack:** Python · Flask · SQLite · Next.js · Tailwind CSS · Recharts · Railway

---

## What it is

A fully functional analytics dashboard powered by a synthetically generated luxury retail database. Models three fictional maisons across 15 global boutiques with realistic business logic — VIC client tiers, seasonal spend patterns, channel mix, margin calculations, and Pareto revenue distribution.

---

## Database Schema
```
boutiques       15 rows  — global locations, tiers, currencies
products        35 rows  — SKUs with price and margin per maison
customers    3,000 rows  — faker-generated, locale-matched, tiered
transactions 6,400 rows  — purchase records with full financials
inventory      175 rows  — stock levels and sell-through
```

---

## API Endpoints

| Endpoint | Description |
|---|---|
| `GET /api/kpis` | Top-line KPIs (revenue, AOV, VIC share) |
| `GET /api/revenue-by-maison` | Revenue + margin per maison |
| `GET /api/revenue-by-month` | Monthly revenue trend |
| `GET /api/tier-summary` | Client tier breakdown with LTV |
| `GET /api/top-products` | Top SKUs by revenue |
| `GET /api/boutique-performance` | Revenue per boutique |
| `GET /api/channel-mix` | Channel mix by revenue |
| `GET /api/inventory` | Sell-through rate by boutique/SKU |
