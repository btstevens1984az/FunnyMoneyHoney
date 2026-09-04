import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { EventOdds } from "../api/client";
import { pct } from "../lib/format";

interface Props {
  event: EventOdds | null;
}

export function ProbabilityView({ event }: Props) {
  if (!event) {
    return (
      <section
        data-testid="probability-view"
        className="rounded-2xl border border-dashed border-white/10 bg-ink-900/40 p-6 text-sm text-slate-400"
      >
        Select a game to inspect implied vs fair probabilities.
      </section>
    );
  }

  const market =
    event.bookmakers[0]?.markets.find((m) => m.key === "h2h") ??
    event.bookmakers[0]?.markets[0];
  const data =
    market?.outcomes.map((o) => ({
      name: o.name.length > 16 ? `${o.name.slice(0, 14)}…` : o.name,
      implied: Number((o.implied_probability * 100).toFixed(1)),
      fair: Number((o.fair_probability * 100).toFixed(1)),
    })) ?? [];

  return (
    <section
      data-testid="probability-view"
      className="fade-up rounded-2xl border border-white/5 bg-ink-900/70 p-5 shadow-glow"
    >
      <h2 className="font-display text-lg font-semibold text-white">
        Probability lens
      </h2>
      <p className="mt-1 text-sm text-slate-400">
        {event.away_team} @ {event.home_team} · overround{" "}
        <span className="font-mono text-honey-300">
          {market ? pct(market.overround) : "—"}
        </span>
      </p>
      <div className="mt-4 h-56">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} barGap={4}>
            <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
            <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 11 }} />
            <YAxis
              tick={{ fill: "#94a3b8", fontSize: 11 }}
              unit="%"
              domain={[0, "auto"]}
            />
            <Tooltip
              contentStyle={{
                background: "#121a2b",
                border: "1px solid rgba(255,255,255,0.08)",
                borderRadius: 12,
              }}
            />
            <Bar dataKey="implied" name="Implied %" fill="#64748b" radius={4} />
            <Bar dataKey="fair" name="Fair %" fill="#2dd4bf" radius={4} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <p className="mt-3 text-xs text-slate-500">
        Fair % removes bookmaker overround so outcomes sum to 100%. Educational
        metric only.
      </p>
    </section>
  );
}
