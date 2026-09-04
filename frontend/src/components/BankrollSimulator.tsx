import { useState } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api, type SimulateResponse } from "../api/client";
import { money, pct } from "../lib/format";

export function BankrollSimulator() {
  const [stake, setStake] = useState(1000);
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SimulateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function run() {
    setLoading(true);
    setError(null);
    try {
      const data = await api.simulate({
        daily_stake: stake,
        days,
        trials: 400,
        seed: 42,
      });
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Simulation failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section
      data-testid="bankroll-sim"
      className="fade-up rounded-2xl border border-white/5 bg-ink-900/70 p-5 shadow-glow"
    >
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 className="font-display text-lg font-semibold text-white">
            Daily bankroll simulator
          </h2>
          <p className="mt-1 max-w-xl text-sm text-slate-400">
            Monte Carlo paths for a fixed daily stake (default $1,000). Teaching
            tool for variance — not a profit forecast or historical claim.
          </p>
        </div>
        <div className="flex flex-wrap items-end gap-3">
          <label className="text-xs text-slate-400">
            Daily stake ($)
            <input
              type="number"
              min={1}
              value={stake}
              onChange={(e) => setStake(Number(e.target.value))}
              className="mt-1 block w-28 rounded-lg border border-white/10 bg-ink-800 px-3 py-2 font-mono text-sm text-white"
            />
          </label>
          <label className="text-xs text-slate-400">
            Days
            <input
              type="number"
              min={1}
              max={365}
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              className="mt-1 block w-20 rounded-lg border border-white/10 bg-ink-800 px-3 py-2 font-mono text-sm text-white"
            />
          </label>
          <button
            type="button"
            onClick={run}
            disabled={loading}
            className="rounded-lg bg-honey-500 px-4 py-2 text-sm font-semibold text-ink-950 transition hover:bg-honey-400 disabled:opacity-60"
          >
            {loading ? "Running…" : "Simulate"}
          </button>
        </div>
      </div>

      {error && (
        <p className="mt-3 text-sm text-coral-400">{error}</p>
      )}

      {result && (
        <div className="mt-5 space-y-5">
          <div className="grid gap-3 sm:grid-cols-4">
            {[
              ["Expected P&L", money(result.expected_ending_bankroll)],
              ["Median", money(result.median_ending_bankroll)],
              ["5th %ile", money(result.p05_ending_bankroll)],
              ["95th %ile", money(result.p95_ending_bankroll)],
            ].map(([label, value]) => (
              <div
                key={label}
                className="rounded-xl border border-white/5 bg-ink-800/60 px-3 py-3"
              >
                <div className="text-[11px] uppercase tracking-wider text-slate-500">
                  {label}
                </div>
                <div className="mt-1 font-mono text-lg text-white">{value}</div>
              </div>
            ))}
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <div className="h-56">
              <p className="mb-2 text-xs uppercase tracking-wider text-slate-500">
                Expected path
              </p>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={result.projected_path}>
                  <defs>
                    <linearGradient id="pnl" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#e8b84b" stopOpacity={0.45} />
                      <stop offset="100%" stopColor="#e8b84b" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid stroke="rgba(255,255,255,0.06)" />
                  <XAxis dataKey="day" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                  <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
                  <Tooltip
                    contentStyle={{
                      background: "#121a2b",
                      border: "1px solid rgba(255,255,255,0.08)",
                      borderRadius: 12,
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="expected_pnl"
                    stroke="#e8b84b"
                    fill="url(#pnl)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
            <div className="h-56">
              <p className="mb-2 text-xs uppercase tracking-wider text-slate-500">
                Ending P&amp;L distribution
              </p>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={result.histogram}>
                  <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
                  <XAxis
                    dataKey="bucket_start"
                    tick={{ fill: "#94a3b8", fontSize: 10 }}
                    tickFormatter={(v) => `${Math.round(Number(v) / 1000)}k`}
                  />
                  <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
                  <Tooltip
                    contentStyle={{
                      background: "#121a2b",
                      border: "1px solid rgba(255,255,255,0.08)",
                      borderRadius: 12,
                    }}
                  />
                  <Bar dataKey="count" fill="#2dd4bf" radius={3} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <p className="text-xs text-slate-500">
            Sample hit rate in simulation: {pct(result.win_rate_estimate)} ·{" "}
            {result.educational_note}
          </p>
        </div>
      )}
    </section>
  );
}
