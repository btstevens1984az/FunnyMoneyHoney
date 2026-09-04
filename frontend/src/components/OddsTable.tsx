import type { EventOdds } from "../api/client";
import { formatKickoff, pct, riskClass } from "../lib/format";

interface Props {
  events: EventOdds[];
  selectedId?: string | null;
  onSelect: (event: EventOdds) => void;
}

export function OddsTable({ events, selectedId, onSelect }: Props) {
  return (
    <section data-testid="odds-table" className="fade-up">
      <div className="mb-3 flex items-end justify-between gap-3">
        <div>
          <h2 className="font-display text-lg font-semibold text-white">
            Today&apos;s markets
          </h2>
          <p className="text-sm text-slate-400">
            Prices refresh on an interval — demo mode jitters bundled sample
            odds so the board stays alive without an API key.
          </p>
        </div>
        <span className="font-mono text-xs text-slate-500">
          {events.length} events
        </span>
      </div>

      <div className="overflow-hidden rounded-2xl border border-white/5 bg-ink-900/70 shadow-glow">
        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-ink-800/80 text-xs uppercase tracking-wider text-slate-400">
              <tr>
                <th className="px-4 py-3 font-medium">Matchup</th>
                <th className="px-4 py-3 font-medium">Kickoff</th>
                <th className="px-4 py-3 font-medium">Best h2h</th>
                <th className="px-4 py-3 font-medium">Implied</th>
                <th className="px-4 py-3 font-medium">Fair</th>
                <th className="px-4 py-3 font-medium">Rel. value</th>
                <th className="px-4 py-3 font-medium">Signal</th>
              </tr>
            </thead>
            <tbody>
              {events.map((event) => {
                const market =
                  event.bookmakers[0]?.markets.find((m) => m.key === "h2h") ??
                  event.bookmakers[0]?.markets[0];
                const top = market?.outcomes
                  .slice()
                  .sort((a, b) => b.relative_value - a.relative_value)[0];
                const selected = selectedId === event.id;
                return (
                  <tr
                    key={event.id}
                    onClick={() => onSelect(event)}
                    className={`cursor-pointer border-t border-white/5 transition hover:bg-white/[0.03] ${
                      selected ? "bg-honey-500/5" : ""
                    }`}
                  >
                    <td className="px-4 py-3">
                      <div className="font-medium text-white">
                        {event.away_team}{" "}
                        <span className="text-slate-500">@</span>{" "}
                        {event.home_team}
                      </div>
                      <div className="text-xs text-slate-500">
                        {event.sport_title}
                      </div>
                    </td>
                    <td className="px-4 py-3 font-mono text-xs text-slate-300">
                      {formatKickoff(event.commence_time)}
                    </td>
                    <td className="px-4 py-3">
                      {top ? (
                        <>
                          <div className="text-white">{top.name}</div>
                          <div className="font-mono text-xs text-slate-400">
                            {top.price.toFixed(2)}
                            {top.point != null ? ` (${top.point})` : ""}
                          </div>
                        </>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td className="px-4 py-3 font-mono text-slate-300">
                      {top ? pct(top.implied_probability) : "—"}
                    </td>
                    <td className="px-4 py-3 font-mono text-mint-400">
                      {top ? pct(top.fair_probability) : "—"}
                    </td>
                    <td className="px-4 py-3 font-mono">
                      {top ? (
                        <span
                          className={
                            top.relative_value >= 0
                              ? "text-mint-400"
                              : "text-coral-400"
                          }
                        >
                          {top.relative_value >= 0 ? "+" : ""}
                          {pct(top.relative_value)}
                        </span>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td className={`px-4 py-3 font-mono text-xs uppercase ${riskClass(event.alert_level)}`}>
                      {event.alert_level}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
