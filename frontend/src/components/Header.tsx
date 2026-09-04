interface Props {
  mode: "demo" | "live";
  generatedAt?: string;
  refreshing?: boolean;
}

export function Header({ mode, generatedAt, refreshing }: Props) {
  return (
    <header className="border-b border-white/5 bg-ink-950/80 backdrop-blur-md sticky top-0 z-40">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-honey-400 to-honey-500 text-ink-950 shadow-glow font-display font-bold text-lg">
            $
          </div>
          <div>
            <h1 className="font-display text-xl font-semibold tracking-tight text-white sm:text-2xl">
              FunnyMoneyHoney
            </h1>
            <p className="text-xs text-slate-400 sm:text-sm">
              Clean odds · implied probability · educational value ranking
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3 text-xs sm:text-sm">
          <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-ink-800 px-3 py-1.5">
            <span className="live-dot h-2 w-2 rounded-full bg-mint-400" />
            <span className="font-mono uppercase tracking-wider text-slate-300">
              {mode} · {refreshing ? "updating…" : "live feed"}
            </span>
          </span>
          {generatedAt && (
            <span className="hidden font-mono text-slate-500 md:inline">
              {new Date(generatedAt).toLocaleTimeString()}
            </span>
          )}
        </div>
      </div>
    </header>
  );
}
