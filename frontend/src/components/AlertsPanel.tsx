import type { AlertItem } from "../api/client";

interface Props {
  alerts: AlertItem[];
}

export function AlertsPanel({ alerts }: Props) {
  return (
    <section
      data-testid="alerts-panel"
      className="fade-up rounded-2xl border border-white/5 bg-ink-900/70 p-5"
    >
      <h2 className="font-display text-lg font-semibold text-white">
        Pull / caution alerts
      </h2>
      <p className="mt-1 text-sm text-slate-400">
        Educational signals when relative value is weak or overround is high —
        study or skip, never chase.
      </p>
      <ul className="mt-4 max-h-72 space-y-2 overflow-y-auto">
        {alerts.map((a, i) => (
          <li
            key={`${a.title}-${i}`}
            className={`rounded-xl border px-3 py-2 text-sm ${
              a.severity === "pull"
                ? "border-coral-500/30 bg-coral-500/10"
                : a.severity === "caution"
                  ? "border-honey-500/30 bg-honey-500/10"
                  : "border-white/5 bg-ink-800/40"
            }`}
          >
            <div className="flex items-center gap-2">
              <span className="font-mono text-[10px] uppercase tracking-wider text-slate-300">
                {a.severity}
              </span>
              <span className="font-medium text-white">{a.title}</span>
            </div>
            <p className="mt-1 text-xs leading-relaxed text-slate-400">
              {a.detail}
            </p>
            {a.matchup && (
              <p className="mt-1 font-mono text-[10px] text-slate-500">
                {a.matchup}
              </p>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}
