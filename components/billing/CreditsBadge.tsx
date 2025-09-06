"use client";
import useSWR from "swr";

const fetcher = (u: string) => fetch(u).then(r => r.json());

export default function CreditsBadge() {
  const { data } = useSWR("/api/credits/balance", fetcher, { refreshInterval: 15000 });
  const n = data?.credits ?? 0;
  
  return (
    <div className="flex items-center gap-2 bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20 rounded-full px-3 py-1.5">
      <div className="w-2 h-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full animate-pulse"></div>
      <span className="text-sm font-semibold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
        {n} credits
      </span>
    </div>
  );
}