export default function Pricing() {
  const packs = [
    { id: "pack_20", qty: 20, price: 500, label: "Starter", desc: "Perfect for exploring" },
    { id: "pack_100", qty: 100, price: 1900, label: "Professional", desc: "Most popular choice", popular: true },
    { id: "pack_300", qty: 300, price: 4900, label: "Enterprise", desc: "Maximum value" }
  ];
  
  return (
    <main className="max-w-[1000px] mx-auto px-6 py-20">
      <div className="text-center mb-16">
        <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent mb-4">
          Fuel Your Success
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
          Transparent, usage-based pricing. No subscriptions, no commitments. 
          Pay only for the AI-powered insights you need.
        </p>
      </div>
      
      <div className="grid md:grid-cols-3 gap-8">
        {packs.map(p => (
          <form key={p.id} action="/api/billing/checkout" method="POST" 
                className={`relative rounded-3xl border p-8 transition-all hover:scale-105 ${
                  p.popular 
                    ? 'border-blue-500/50 bg-gradient-to-b from-blue-500/10 to-purple-500/10 shadow-xl shadow-blue-500/20' 
                    : 'border-white/10 bg-white/[0.02] hover:bg-white/[0.05]'
                }`}>
            {p.popular && (
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <span className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-1 rounded-full text-sm font-medium">
                  Most Popular
                </span>
              </div>
            )}
            
            <input type="hidden" name="pack" value={p.id} />
            
            <div className="text-center">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">{p.label}</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">{p.desc}</p>
              
              <div className="mb-6">
                <div className="text-5xl font-black text-gray-900 dark:text-white">{p.qty}</div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">AI Analysis Credits</div>
              </div>
              
              <div className="mb-8">
                <span className="text-3xl font-bold text-gray-900 dark:text-white">
                  ${(p.price / 100).toFixed(0)}
                </span>
                <span className="text-gray-600 dark:text-gray-400 ml-1">
                  (${((p.price / 100) / p.qty).toFixed(2)} per credit)
                </span>
              </div>
              
              <button className={`w-full rounded-2xl px-6 py-4 font-semibold transition-all ${
                p.popular
                  ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg hover:shadow-xl'
                  : 'bg-white/10 text-gray-900 dark:text-white border border-white/20 hover:bg-white/20'
              }`}>
                Get Started
              </button>
            </div>
          </form>
        ))}
      </div>
      
      <div className="mt-16 text-center">
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          ✨ Instant activation • 🔒 Secure payments • 💫 No expiration
        </p>
        <p className="text-sm text-gray-500 dark:text-gray-500">
          Credits never expire. Use them at your own pace.
        </p>
      </div>
    </main>
  );
}