import { createServerSupabase } from "@/lib/supabase/server";

export default async function CreditsPage() {
  const sb = createServerSupabase();
  const { data: { user } } = await sb.auth.getUser();
  if (!user) return null;
  
  const [{ data: profile }, { data: ledger }] = await Promise.all([
    sb.from("profiles").select("credits").eq("id", user.id).single(),
    sb.from("credit_ledger").select("*").eq("user_id", user.id).order("created_at", { ascending: false }).limit(50)
  ]);
  
  const currentCredits = profile?.credits ?? 0;
  
  return (
    <main className="max-w-[1000px] mx-auto px-6 py-20">
      <div className="mb-12">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent mb-4">
          Credit Dashboard
        </h1>
        <p className="text-gray-600 dark:text-gray-300 text-lg">
          Track your AI analysis usage and manage your credit balance
        </p>
      </div>
      
      {/* Balance Card */}
      <div className="mb-12">
        <div className="bg-gradient-to-br from-blue-500/10 to-purple-500/10 rounded-3xl border border-blue-500/20 p-8">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">
                Available Credits
              </h2>
              <div className="flex items-baseline gap-2">
                <span className="text-5xl font-black bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-text text-transparent">
                  {currentCredits}
                </span>
                <span className="text-gray-600 dark:text-gray-400">credits remaining</span>
              </div>
            </div>
            <div className="text-right">
              <div className="text-6xl opacity-20">💎</div>
            </div>
          </div>
          
          {currentCredits < 5 && (
            <div className="mt-6 p-4 bg-amber-500/10 border border-amber-500/20 rounded-2xl">
              <p className="text-amber-600 dark:text-amber-400 font-medium">
                ⚠️ Running low on credits. Consider purchasing more to continue your analysis.
              </p>
            </div>
          )}
        </div>
      </div>
      
      {/* Transaction History */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white">
            Transaction History
          </h2>
          <a 
            href="/pricing" 
            className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-6 py-3 rounded-2xl font-semibold hover:shadow-lg transition-all"
          >
            Purchase Credits
          </a>
        </div>
        
        <div className="rounded-3xl border border-white/10 bg-white/[0.02] overflow-hidden">
          {ledger && ledger.length > 0 ? (
            <table className="w-full">
              <thead className="bg-white/[0.05] border-b border-white/10">
                <tr>
                  <th className="text-left p-4 font-semibold text-gray-900 dark:text-white">Date & Time</th>
                  <th className="text-left p-4 font-semibold text-gray-900 dark:text-white">Activity</th>
                  <th className="text-right p-4 font-semibold text-gray-900 dark:text-white">Credits</th>
                </tr>
              </thead>
              <tbody>
                {ledger.map((r: any, index: number) => (
                  <tr key={r.id} className={`${index !== ledger.length - 1 ? 'border-b border-white/5' : ''} hover:bg-white/[0.02] transition-colors`}>
                    <td className="p-4 text-gray-600 dark:text-gray-400">
                      {new Date(r.created_at).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">
                          {r.reason === 'purchase' ? '💳' : 
                           r.reason === 'analysis' ? '🧠' : 
                           r.reason === 'refund' ? '↩️' : '⚡'}
                        </span>
                        <div>
                          <div className="font-medium text-gray-900 dark:text-white capitalize">
                            {r.reason === 'analysis' ? 'AI Analysis' : 
                             r.reason === 'purchase' ? 'Credit Purchase' :
                             r.reason === 'refund' ? 'Refund' : r.reason}
                          </div>
                          {r.meta && Object.keys(r.meta).length > 0 && (
                            <div className="text-sm text-gray-500 dark:text-gray-500">
                              {r.meta.source || r.meta.checkout || 'System'}
                            </div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className={`p-4 text-right font-bold ${
                      r.delta > 0 ? "text-emerald-500" : "text-rose-500"
                    }`}>
                      {r.delta > 0 ? `+${r.delta}` : r.delta}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="p-12 text-center">
              <div className="text-6xl opacity-20 mb-4">📊</div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                No transactions yet
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                Start using AI analysis to see your credit history here
              </p>
              <a 
                href="/prep" 
                className="inline-block bg-blue-500 text-white px-6 py-3 rounded-2xl font-semibold hover:bg-blue-600 transition-colors"
              >
                Start Analyzing
              </a>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}