import type { RankedOutcome } from "../api/client";
import { pct, riskClass } from "../lib/format";

interface Props {
  rankings: RankedOutcome[];
}

export function ValueRanking({ rankings }: Props) {
  return (
    <section
      data-testid="value-ranking"
      className="fade-up rounded-2xl border border-white/5 bg-ink-900/70 p-5"
    >
      <h2 className="font-display text-lg font-semibold text-white">
        Relative safety / value
      </h2>
      <p className="mt-1 text-sm text-slate-400">
        Ranked by educational relative value after vig removal — not tips.
      </p>
      <ol className="mt-4 max-h-80 space-y-2 overflow-y-auto pr-1">
        {rankings.slice(0, 12).map((row) => (
          <li
            key={`${row.event_id}-${row.bookmaker}-${row.market}-${row.outcome}`}
            className="flex items-start justify-between gap-3 rounded-xl border border-white/5 bg-ink-800/50 px-3 py-2"
          >
            <div>
              <div className="text-sm font-medium text-white">
                <span className="mr-2 font-mono text-xs text-slate-500">
                  #{row.safety_rank}
                </span>
                {row.outcome}
              </div>
              <div className="text-xs text-slate-400">
                {row.matchup} · {row.bookmaker} · {row.market}
              </div>
            </div>
            <div className="text-right">
              <div
                className={`font-mono text-sm ${
                  row.relative_value >= 0 ? "text-mint-400" : "text-coral-400"
                }`}
              >
                {row.relative_value >= 0 ? "+" : ""}
                {pct(row.relative_value)}
              </div>
              <div
                className={`font-mono text-[10px] uppercase ${riskClass(row.risk_flag)}`}
              >
                {row.risk_flag}
              </div>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}
