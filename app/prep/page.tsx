import { Metadata } from "next";

export const metadata: Metadata = {
  title: "AI Interview Preparation - Interview Quotient",
  description: "Transform your interview performance with AI-powered coaching and personalized insights",
};

export default function PrepPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-900 dark:via-slate-900 dark:to-gray-800">
      <div className="max-w-6xl mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h1 className="text-6xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent mb-6">
            Master Your Next Interview
          </h1>
          <p className="text-2xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto leading-relaxed">
            Unlock your potential with AI-powered interview preparation. 
            Get personalized coaching, strategic insights, and confidence-building practice.
          </p>
        </div>
        
        <div className="grid lg:grid-cols-2 gap-12 mb-16">
          <div className="group relative">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-600 rounded-3xl blur opacity-20 group-hover:opacity-30 transition-opacity"></div>
            <div className="relative bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-3xl p-8 border border-white/20 hover:border-blue-300/50 transition-all duration-300 hover:transform hover:scale-105">
              <div className="text-5xl mb-6">🧠</div>
              <h2 className="text-3xl font-bold mb-4 text-gray-900 dark:text-white">
                AI Resume Intelligence
              </h2>
              <p className="text-gray-600 dark:text-gray-300 mb-8 text-lg leading-relaxed">
                Upload your resume and receive deep AI analysis with actionable insights. 
                Optimize your profile for maximum impact and ATS compatibility.
              </p>
              <div className="space-y-3 mb-8">
                <div className="flex items-center gap-3 text-gray-700 dark:text-gray-300">
                  <span className="text-green-500">✓</span>
                  <span>ATS optimization scoring</span>
                </div>
                <div className="flex items-center gap-3 text-gray-700 dark:text-gray-300">
                  <span className="text-green-500">✓</span>
                  <span>Skills gap analysis</span>
                </div>
                <div className="flex items-center gap-3 text-gray-700 dark:text-gray-300">
                  <span className="text-green-500">✓</span>
                  <span>Industry-specific recommendations</span>
                </div>
              </div>
              <a 
                href="/" 
                className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white px-8 py-4 rounded-2xl font-semibold hover:shadow-xl transition-all duration-300 group"
              >
                <span>Analyze Resume</span>
                <span className="group-hover:translate-x-1 transition-transform">→</span>
              </a>
            </div>
          </div>
          
          <div className="group relative">
            <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-600 rounded-3xl blur opacity-20 group-hover:opacity-30 transition-opacity"></div>
            <div className="relative bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-3xl p-8 border border-white/20 hover:border-purple-300/50 transition-all duration-300 hover:transform hover:scale-105">
              <div className="text-5xl mb-6">🎯</div>
              <h2 className="text-3xl font-bold mb-4 text-gray-900 dark:text-white">
                Smart Job Matching
              </h2>
              <p className="text-gray-600 dark:text-gray-300 mb-8 text-lg leading-relaxed">
                Paste any job description and get personalized interview questions, 
                company insights, and strategic talking points tailored to the role.
              </p>
              <div className="space-y-3 mb-8">
                <div className="flex items-center gap-3 text-gray-700 dark:text-gray-300">
                  <span className="text-green-500">✓</span>
                  <span>Role-specific questions</span>
                </div>
                <div className="flex items-center gap-3 text-gray-700 dark:text-gray-300">
                  <span className="text-green-500">✓</span>
                  <span>Company culture insights</span>
                </div>
                <div className="flex items-center gap-3 text-gray-700 dark:text-gray-300">
                  <span className="text-green-500">✓</span>
                  <span>Strategic positioning advice</span>
                </div>
              </div>
              <a 
                href="/" 
                className="inline-flex items-center gap-2 bg-gradient-to-r from-purple-500 to-pink-600 text-white px-8 py-4 rounded-2xl font-semibold hover:shadow-xl transition-all duration-300 group"
              >
                <span>Match Job</span>
                <span className="group-hover:translate-x-1 transition-transform">→</span>
              </a>
            </div>
          </div>
        </div>
        
        <div className="text-center">
          <div className="bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-3xl p-12 border border-white/20">
            <h3 className="text-3xl font-bold mb-8 text-gray-900 dark:text-white">
              Your Success Journey
            </h3>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center group">
                <div className="text-6xl mb-4 group-hover:scale-110 transition-transform">📋</div>
                <h4 className="text-xl font-bold text-gray-900 dark:text-white mb-3">Analyze & Optimize</h4>
                <p className="text-gray-600 dark:text-gray-300">Upload your materials and let AI identify strengths and improvement areas</p>
              </div>
              <div className="text-center group">
                <div className="text-6xl mb-4 group-hover:scale-110 transition-transform">🎪</div>
                <h4 className="text-xl font-bold text-gray-900 dark:text-white mb-3">Practice & Prepare</h4>
                <p className="text-gray-600 dark:text-gray-300">Get personalized questions and strategic insights for your target role</p>
              </div>
              <div className="text-center group">
                <div className="text-6xl mb-4 group-hover:scale-110 transition-transform">🏆</div>
                <h4 className="text-xl font-bold text-gray-900 dark:text-white mb-3">Ace & Succeed</h4>
                <p className="text-gray-600 dark:text-gray-300">Walk into your interview with confidence and strategic positioning</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}