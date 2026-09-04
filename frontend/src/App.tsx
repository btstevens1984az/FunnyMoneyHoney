import { useEffect, useState } from "react";
import {
  api,
  type AlertItem,
  type EventOdds,
  type OddsFeed,
  type RankedOutcome,
} from "./api/client";
import { AlertsPanel } from "./components/AlertsPanel";
import { BankrollSimulator } from "./components/BankrollSimulator";
import { DisclaimerBanner } from "./components/DisclaimerBanner";
import { Header } from "./components/Header";
import { OddsTable } from "./components/OddsTable";
import { ProbabilityView } from "./components/ProbabilityView";
import { ThinkingPanel } from "./components/ThinkingPanel";
import { ValueRanking } from "./components/ValueRanking";

export default function App() {
  const [feed, setFeed] = useState<OddsFeed | null>(null);
  const [rankings, setRankings] = useState<RankedOutcome[]>([]);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [selected, setSelected] = useState<EventOdds | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    setRefreshing(true);
    try {
      const [odds, ranks, alertData] = await Promise.all([
        api.odds(),
        api.rankings(),
        api.alerts(),
      ]);
      setFeed(odds);
      setRankings(ranks.rankings);
      setAlerts(alertData.alerts);
      setSelected((prev) => {
        if (!prev) return odds.events[0] ?? null;
        return odds.events.find((e) => e.id === prev.id) ?? odds.events[0] ?? null;
      });
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load feed");
    } finally {
      setRefreshing(false);
    }
  }

  useEffect(() => {
    void refresh();
    const id = window.setInterval(() => void refresh(), 15000);
    return () => window.clearInterval(id);
  }, []);

  return (
    <div className="min-h-screen bg-ink-950 bg-mesh text-slate-100">
      <DisclaimerBanner />
      <Header
        mode={feed?.mode ?? "demo"}
        generatedAt={feed?.generated_at}
        refreshing={refreshing}
      />

      <main className="mx-auto max-w-7xl space-y-8 px-4 py-8 sm:px-6">
        {error && (
          <div className="rounded-xl border border-coral-500/30 bg-coral-500/10 px-4 py-3 text-sm text-coral-400">
            {error}
          </div>
        )}

        <OddsTable
          events={feed?.events ?? []}
          selectedId={selected?.id}
          onSelect={setSelected}
        />

        <div className="grid gap-6 lg:grid-cols-2">
          <ProbabilityView event={selected} />
          <ValueRanking rankings={rankings} />
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <AlertsPanel alerts={alerts} />
          <ThinkingPanel event={selected} />
        </div>

        <BankrollSimulator />

        <footer className="border-t border-white/5 pt-6 pb-10 text-center text-xs text-slate-500">
          FunnyMoneyHoney · MIT · Self-hosted educational odds dashboard ·{" "}
          {feed?.disclaimer ??
            "Not financial or gambling advice. Gambling involves risk of loss."}
        </footer>
      </main>
    </div>
  );
}
