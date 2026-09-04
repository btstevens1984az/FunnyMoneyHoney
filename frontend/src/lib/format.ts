export function pct(n: number, digits = 1): string {
  return `${(n * 100).toFixed(digits)}%`;
}

export function money(n: number): string {
  const sign = n < 0 ? "-" : "";
  return `${sign}$${Math.abs(n).toLocaleString(undefined, {
    maximumFractionDigits: 0,
  })}`;
}

export function formatKickoff(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString(undefined, {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export function riskClass(flag: string): string {
  if (flag === "pull") return "text-coral-400";
  if (flag === "caution") return "text-honey-400";
  return "text-mint-400";
}
