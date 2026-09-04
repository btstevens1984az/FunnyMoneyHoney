export type RiskFlag = "ok" | "caution" | "pull";

export interface Outcome {
  name: string;
  price: number;
  point?: number | null;
  implied_probability: number;
  fair_probability: number;
  overround_share: number;
  relative_value: number;
  safety_rank: number;
  risk_flag: RiskFlag;
  risk_reason?: string | null;
}

export interface Market {
  key: string;
  last_update?: string | null;
  outcomes: Outcome[];
  overround: number;
}

export interface Bookmaker {
  key: string;
  title: string;
  markets: Market[];
}

export interface EventOdds {
  id: string;
  sport_key: string;
  sport_title: string;
  commence_time: string;
  home_team: string;
  away_team: string;
  bookmakers: Bookmaker[];
  best_value_outcome?: string | null;
  analysis_summary?: string | null;
  alert_level: RiskFlag;
}

export interface OddsFeed {
  mode: "demo" | "live";
  generated_at: string;
  refresh_seconds: number;
  event_count: number;
  events: EventOdds[];
  disclaimer: string;
}

export interface RankedOutcome {
  event_id: string;
  sport_title: string;
  matchup: string;
  commence_time: string;
  bookmaker: string;
  market: string;
  outcome: string;
  price: number;
  implied_probability: number;
  fair_probability: number;
  relative_value: number;
  safety_rank: number;
  risk_flag: RiskFlag;
  risk_reason?: string | null;
  analysis: string;
}

export interface RankingResponse {
  mode: "demo" | "live";
  generated_at: string;
  rankings: RankedOutcome[];
  disclaimer: string;
}

export interface AlertItem {
  severity: "info" | "caution" | "pull";
  title: string;
  detail: string;
  event_id?: string | null;
  matchup?: string | null;
}

export interface AlertsResponse {
  generated_at: string;
  alerts: AlertItem[];
  disclaimer: string;
}

export interface SimulateResponse {
  daily_stake: number;
  days: number;
  trials: number;
  expected_ending_bankroll: number;
  median_ending_bankroll: number;
  p05_ending_bankroll: number;
  p95_ending_bankroll: number;
  win_rate_estimate: number;
  projected_path: { day: number; expected_pnl: number }[];
  histogram: { bucket_start: number; count: number }[];
  educational_note: string;
  disclaimer: string;
}

export interface AnalysisResponse {
  thinking: string[];
  educational_score: number;
  recommendation: "study" | "caution" | "avoid";
  summary: string;
  disclaimer: string;
}

const base = "";

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${base}${path}`);
  if (!res.ok) throw new Error(`${path} failed: ${res.status}`);
  return res.json() as Promise<T>;
}

export const api = {
  odds: () => getJson<OddsFeed>("/api/odds"),
  rankings: () => getJson<RankingResponse>("/api/rankings"),
  alerts: () => getJson<AlertsResponse>("/api/alerts"),
  simulate: (body: {
    daily_stake: number;
    days: number;
    trials?: number;
    seed?: number;
  }) =>
    fetch(`${base}/api/simulate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then(async (res) => {
      if (!res.ok) throw new Error(`simulate failed: ${res.status}`);
      return res.json() as Promise<SimulateResponse>;
    }),
  analyze: (body: { event_id?: string; outcome_name?: string }) =>
    fetch(`${base}/api/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then(async (res) => {
      if (!res.ok) throw new Error(`analyze failed: ${res.status}`);
      return res.json() as Promise<AnalysisResponse>;
    }),
};
