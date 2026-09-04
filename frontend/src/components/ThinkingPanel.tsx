import { useEffect, useState } from "react";
import { api, type AnalysisResponse, type EventOdds } from "../api/client";

interface Props {
  event: EventOdds | null;
}

export function ThinkingPanel({ event }: Props) {
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!event) {
      setResult(null);
      return;
    }
    let cancelled = false;
    setLoading(true);
    const outcome = event.bookmakers[0]?.markets[0]?.outcomes[0];
    void api
      .analyze({
        event_id: event.id,
        outcome_name: outcome?.name,
      })
      .then((data) => {
        if (!cancelled) setResult(data);
      })
      .catch(() => {
        if (!cancelled) setResult(null);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [event]);

  async function run() {
    if (!event) return;
    setLoading(true);
    try {
      const outcome = event.bookmakers[0]?.markets[0]?.outcomes[0];
      const data = await api.analyze({
        event_id: event.id,
        outcome_name: outcome?.name,
      });
      setResult(data);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section
      data-testid="thinking-panel"
      className="fade-up rounded-2xl border border-white/5 bg-ink-900/70 p-5"
    >
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="font-display text-lg font-semibold text-white">
            Educational thinking
          </h2>
          <p className="mt-1 text-sm text-slate-400">
            Transparent step-by-step odds math — not a claimed win rate.
          </p>
        </div>
        <button
          type="button"
          disabled={!event || loading}
          onClick={run}
          className="rounded-lg border border-mint-500/40 bg-mint-500/10 px-3 py-2 text-sm font-medium text-mint-400 hover:bg-mint-500/20 disabled:opacity-50"
        >
          {loading ? "Thinking…" : "Analyze"}
        </button>
      </div>

      {loading && !result && (
        <p className="mt-4 text-sm text-slate-500">Running educational analysis…</p>
      )}

      {result && (
        <div className="mt-4 space-y-3">
          <div className="flex flex-wrap items-center gap-3">
            <div className="rounded-xl border border-white/5 bg-ink-800 px-4 py-3">
              <div className="text-[10px] uppercase tracking-wider text-slate-500">
                Educational score
              </div>
              <div className="font-mono text-2xl text-honey-300">
                {result.educational_score.toFixed(0)}
                <span className="text-sm text-slate-500">/100</span>
              </div>
            </div>
            <div className="rounded-xl border border-white/5 bg-ink-800 px-4 py-3">
              <div className="text-[10px] uppercase tracking-wider text-slate-500">
                Recommendation
              </div>
              <div className="font-mono text-lg uppercase text-slate-200">
                {result.recommendation}
              </div>
            </div>
          </div>
          <ol className="max-h-40 space-y-1.5 overflow-y-auto text-xs text-slate-400">
            {result.thinking.map((step, i) => (
              <li key={i} className="flex gap-2">
                <span className="font-mono text-slate-600">{i + 1}.</span>
                <span>{step}</span>
              </li>
            ))}
          </ol>
          <p className="text-sm text-slate-300">{result.summary}</p>
        </div>
      )}
    </section>
  );
}
