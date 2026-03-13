import { useEffect, useState } from "react";
import useSWR from "swr";
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from "recharts";

const API = "http://localhost:5001";

const fetcher = (url) => fetch(url).then((r) => r.json());

// ── Formatting helpers ──────────────────────────────────────────────────────

const fmt = {
  currency: (n) =>
    n >= 1_000_000
      ? `$${(n / 1_000_000).toFixed(1)}M`
      : n >= 1_000
      ? `$${(n / 1_000).toFixed(0)}K`
      : `$${n?.toFixed(0) ?? 0}`,
  number: (n) => Number(n).toLocaleString(),
  pct: (n) => `${n}%`,
};

const GOLD        = "#C9A84C";
const GOLD_LIGHT  = "#E8D5A3";
const MAISON_COLORS = {
  "Maison Eclat":   "#C9A84C",
  "Maison Vellore": "#8B9E7A",
  "Maison Aurore":  "#9E7A8B",
};
const TIER_COLORS = { VIC: "#C9A84C", Premium: "#8B9E7A", Standard: "#555555" };
const CHANNEL_COLORS = ["#C9A84C", "#8B9E7A", "#9E7A8B", "#6A7A8B"];

// ── Tooltip ─────────────────────────────────────────────────────────────────

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-obsidian-3 border border-obsidian-5 px-4 py-3 text-xs font-mono">
      {label && <p className="text-stone-light mb-2">{label}</p>}
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color || GOLD }}>
          {p.name}: {typeof p.value === "number" && p.value > 100
            ? fmt.currency(p.value)
            : p.value}
        </p>
      ))}
    </div>
  );
};

// ── KPI Card ────────────────────────────────────────────────────────────────

const KpiCard = ({ label, value, sub }) => (
  <div className="border border-obsidian-5 bg-obsidian-2 px-6 py-5 relative overflow-hidden group hover:border-gold transition-colors duration-500">
    <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-gold to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
    <p className="text-stone text-xs font-mono tracking-[0.15em] uppercase mb-2">{label}</p>
    <p className="text-gold font-display text-3xl font-light">{value}</p>
    {sub && <p className="text-stone text-xs mt-1 font-mono">{sub}</p>}
  </div>
);

// ── Section Header ──────────────────────────────────────────────────────────

const SectionHeader = ({ title, subtitle }) => (
  <div className="mb-6">
    <div className="flex items-center gap-3 mb-1">
      <div className="w-4 h-px bg-gold" />
      <h2 className="text-gold-light font-display text-xl font-light tracking-wide">{title}</h2>
    </div>
    {subtitle && <p className="text-stone text-xs font-mono ml-7">{subtitle}</p>}
  </div>
);

// ── Panel ───────────────────────────────────────────────────────────────────

const Panel = ({ children, className = "" }) => (
  <div className={`border border-obsidian-5 bg-obsidian-2 p-6 ${className}`}>
    {children}
  </div>
);

// ── Main Dashboard ───────────────────────────────────────────────────────────

export default function Dashboard() {
  const { data: kpis }        = useSWR(`${API}/api/kpis`, fetcher);
  const { data: byMaison }    = useSWR(`${API}/api/revenue-by-maison`, fetcher);
  const { data: byMonth }     = useSWR(`${API}/api/revenue-by-month`, fetcher);
  const { data: tiers }       = useSWR(`${API}/api/tier-summary`, fetcher);
  const { data: products }    = useSWR(`${API}/api/top-products?limit=8`, fetcher);
  const { data: boutiques }   = useSWR(`${API}/api/boutique-performance`, fetcher);
  const { data: channels }    = useSWR(`${API}/api/channel-mix`, fetcher);

  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  if (!mounted) return null;

  // Format monthly data — abbreviate month label
  const monthlyData = (byMonth || []).map((d) => ({
    ...d,
    label: d.month?.slice(0, 7),
  }));

  return (
    <div className="min-h-screen bg-obsidian font-body">

      {/* ── Header ── */}
      <header className="border-b border-obsidian-5 bg-obsidian-2 sticky top-0 z-50">
        <div className="max-w-screen-xl mx-auto px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <div>
              <p className="text-gold font-display text-lg tracking-[0.2em] uppercase">Maison Analytics</p>
              <p className="text-stone text-xs font-mono tracking-widest">Intelligence Platform — 2022–2025</p>
            </div>
          </div>
          <div className="flex items-center gap-8 text-xs font-mono text-stone">
            <span>3 Maisons</span>
            <span className="text-obsidian-5">|</span>
            <span>15 Boutiques</span>
            <span className="text-obsidian-5">|</span>
            <span>35 SKUs</span>
            <span className="text-obsidian-5">|</span>
            <span className="text-gold">{fmt.number(kpis?.total_transactions)} Transactions</span>
          </div>
        </div>
      </header>

      <main className="max-w-screen-xl mx-auto px-8 py-10 space-y-14">

        {/* ── KPI Row ── */}
        <section>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-px bg-obsidian-5">
            <KpiCard
              label="Total Revenue"
              value={fmt.currency(kpis?.total_revenue)}
              sub="Net, all maisons"
            />
            <KpiCard
              label="Avg Order Value"
              value={fmt.currency(kpis?.avg_order_value)}
              sub="Per transaction"
            />
            <KpiCard
              label="Active Clients"
              value={fmt.number(kpis?.active_customers)}
              sub="With purchases"
            />
            <KpiCard
              label="VIC Avg LTV"
              value={fmt.currency(kpis?.vic_avg_ltv)}
              sub="Lifetime value"
            />
            <KpiCard
              label="VIC Rev Share"
              value={fmt.pct(kpis?.vic_revenue_share)}
              sub="Pareto principle"
            />
            <KpiCard
              label="Transactions"
              value={fmt.number(kpis?.total_transactions)}
              sub="All channels"
            />
          </div>
        </section>

        {/* ── Revenue Trend ── */}
        <section>
          <SectionHeader
            title="Revenue Trend"
            subtitle="Monthly net revenue across all maisons · seasonal peaks visible in Nov–Dec, Feb, May"
          />
          <Panel>
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={monthlyData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
                <defs>
                  <linearGradient id="goldGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor={GOLD} stopOpacity={0.3} />
                    <stop offset="95%" stopColor={GOLD} stopOpacity={0.02} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="label" tick={{ fontSize: 10 }} interval={3} />
                <YAxis tickFormatter={(v) => fmt.currency(v)} tick={{ fontSize: 10 }} width={60} />
                <Tooltip content={<CustomTooltip />} />
                <Area
                  type="monotone"
                  dataKey="revenue"
                  name="Revenue"
                  stroke={GOLD}
                  strokeWidth={1.5}
                  fill="url(#goldGrad)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </Panel>
        </section>

        {/* ── Maison + Tier row ── */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-8">

          {/* Revenue by Maison */}
          <div>
            <SectionHeader title="Revenue by Maison" subtitle="Net revenue and margin contribution" />
            <Panel>
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={byMaison || []} layout="vertical" margin={{ left: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                  <XAxis type="number" tickFormatter={fmt.currency} tick={{ fontSize: 10 }} />
                  <YAxis type="category" dataKey="maison" tick={{ fontSize: 10 }} width={110} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="revenue" name="Revenue" radius={[0, 2, 2, 0]}>
                    {(byMaison || []).map((entry) => (
                      <Cell key={entry.maison} fill={MAISON_COLORS[entry.maison] || GOLD} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </Panel>
          </div>

          {/* Client Tier Breakdown */}
          <div>
            <SectionHeader title="Client Tier Breakdown" subtitle="Revenue share · Pareto: top 8% VIC clients drive majority" />
            <Panel className="flex items-center gap-6">
              <ResponsiveContainer width="45%" height={220}>
                <PieChart>
                  <Pie
                    data={tiers || []}
                    dataKey="total_revenue"
                    nameKey="client_tier"
                    cx="50%" cy="50%"
                    innerRadius={55} outerRadius={85}
                    strokeWidth={0}
                  >
                    {(tiers || []).map((entry) => (
                      <Cell key={entry.client_tier} fill={TIER_COLORS[entry.client_tier] || "#555"} />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex-1 space-y-4">
                {(tiers || []).map((t) => (
                  <div key={t.client_tier}>
                    <div className="flex justify-between text-xs font-mono mb-1">
                      <span style={{ color: TIER_COLORS[t.client_tier] }}>{t.client_tier}</span>
                      <span className="text-stone">{fmt.currency(t.avg_ltv)} avg LTV</span>
                    </div>
                    <div className="h-px bg-obsidian-5 relative">
                      <div
                        className="h-px absolute top-0 left-0 transition-all duration-1000"
                        style={{
                          width: `${Math.min(100, (t.avg_ltv / 93600) * 100)}%`,
                          background: TIER_COLORS[t.client_tier],
                        }}
                      />
                    </div>
                    <p className="text-stone text-xs mt-1">{fmt.number(t.customers)} clients · {fmt.currency(t.total_revenue)} total</p>
                  </div>
                ))}
              </div>
            </Panel>
          </div>
        </section>

        {/* ── Channel Mix + Top Boutiques ── */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-8">

          {/* Channel Mix */}
          <div>
            <SectionHeader title="Channel Mix" subtitle="Revenue by purchase channel" />
            <Panel>
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={channels || []} margin={{ top: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="channel" tick={{ fontSize: 9 }} />
                  <YAxis tickFormatter={fmt.currency} tick={{ fontSize: 10 }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="revenue" name="Revenue" radius={[2, 2, 0, 0]}>
                    {(channels || []).map((_, i) => (
                      <Cell key={i} fill={CHANNEL_COLORS[i % CHANNEL_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </Panel>
          </div>

          {/* Top Boutiques */}
          <div>
            <SectionHeader title="Boutique Performance" subtitle="Top locations by net revenue" />
            <Panel>
              <div className="space-y-3">
                {(boutiques || []).slice(0, 6).map((b, i) => (
                  <div key={b.boutique_id} className="flex items-center gap-4">
                    <span className="text-obsidian-5 font-mono text-xs w-4">{String(i + 1).padStart(2, "0")}</span>
                    <div className="flex-1 min-w-0">
                      <div className="flex justify-between items-baseline">
                        <span className="text-stone-light text-xs font-mono truncate">{b.city} — {b.maison.replace("Maison ", "")}</span>
                        <span className="text-gold text-xs font-mono ml-2 shrink-0">{fmt.currency(b.revenue)}</span>
                      </div>
                      <div className="mt-1 h-px bg-obsidian-5 relative">
                        <div
                          className="h-px absolute top-0 left-0"
                          style={{
                            width: `${(b.revenue / (boutiques?.[0]?.revenue || 1)) * 100}%`,
                            background: MAISON_COLORS[b.maison] || GOLD,
                            opacity: 0.7,
                          }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Panel>
          </div>
        </section>

        {/* ── Top Products ── */}
        <section>
          <SectionHeader title="Top Products by Revenue" subtitle="SKU-level performance · price × volume" />
          <Panel>
            <div className="overflow-x-auto">
              <table className="w-full text-xs font-mono">
                <thead>
                  <tr className="border-b border-obsidian-5">
                    {["SKU", "Product", "Maison", "Category", "Base Price", "Revenue", "Units Sold", "Margin %"].map((h) => (
                      <th key={h} className="text-left text-stone pb-3 pr-6 font-normal tracking-widest uppercase text-[10px]">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {(products || []).map((p, i) => (
                    <tr key={p.sku} className="border-b border-obsidian-4 hover:bg-obsidian-3 transition-colors">
                      <td className="py-3 pr-6 text-obsidian-5">{p.sku}</td>
                      <td className="py-3 pr-6 text-stone-light">{p.name}</td>
                      <td className="py-3 pr-6" style={{ color: MAISON_COLORS[p.maison] || GOLD }}>{p.maison.replace("Maison ", "")}</td>
                      <td className="py-3 pr-6 text-stone">{p.category}</td>
                      <td className="py-3 pr-6 text-stone">{fmt.currency(p.base_price_usd)}</td>
                      <td className="py-3 pr-6 text-gold">{fmt.currency(p.revenue)}</td>
                      <td className="py-3 pr-6 text-stone">{fmt.number(p.units_sold)}</td>
                      <td className="py-3 pr-6 text-stone">{p.margin_pct}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Panel>
        </section>

        {/* ── Footer ── */}
        <footer className="border-t border-obsidian-5 pt-8 pb-4 flex justify-between items-center text-stone text-xs font-mono">
          <span>Maison Analytics — Synthetic luxury retail intelligence platform</span>
          <span>Built with Flask · Next.js · SQLite · Railway</span>
        </footer>

      </main>
    </div>
  );
}
