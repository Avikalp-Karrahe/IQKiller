"use client";
import useSWR from "swr";

export default function RequireCredits({ need = 1, children }: { need?: number; children: React.ReactNode }) {
  const { data } = useSWR("/api/credits/balance", (u) => fetch(u).then(r => r.json()));
  const ok = (data?.credits ?? 0) >= need;
  if (!ok) return <div className="text-center text-sm opacity-80">Not enough credits. <a href="/pricing" className="underline">Buy credits</a></div>;
  return <>{children}</>;
}