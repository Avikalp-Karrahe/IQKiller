'use client'

import { useTheme } from 'next-themes'
import { useEffect, useState } from 'react'
import { Sun, Moon, Star, ExternalLink } from 'lucide-react'
import { Button } from '@/components/ui/button'

export function HeaderControls() {
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)
  const [starCount, setStarCount] = useState('4.3k')

  useEffect(() => {
    setMounted(true)
    // Fetch real GitHub star count
    fetchGitHubStars()
  }, [])

  const fetchGitHubStars = async () => {
    try {
      const response = await fetch('https://api.github.com/repos/Avikalp-Karrahe/IQKiller')
      const data = await response.json()
      const stars = data.stargazers_count
      setStarCount(stars >= 1000 ? `${(stars / 1000).toFixed(1)}k` : stars.toString())
    } catch (error) {
      console.log('Failed to fetch GitHub stars:', error)
      // Keep default value
    }
  }

  if (!mounted) {
    return (
      <div className="flex items-center gap-3">
        <div className="w-20 h-8 bg-gray-200 dark:bg-gray-700 rounded-full animate-pulse" />
        <div className="w-12 h-6 bg-gray-200 dark:bg-gray-700 rounded-full animate-pulse" />
      </div>
    )
  }

  const isDark = theme === 'dark'

  return (
    <div className="flex items-center gap-3">
      {/* GitHub Star Badge */}
      <Button
        variant="outline"
        size="sm"
        onClick={() => window.open('https://github.com/Avikalp-Karrahe/IQKiller', '_blank')}
        className="flex items-center gap-2 px-3 py-1.5 h-8 bg-black text-white border-gray-600 hover:bg-gray-800 dark:bg-gray-900 dark:border-gray-700 dark:hover:bg-gray-800 transition-all duration-200 hover:scale-105 hover:shadow-lg group"
      >
        <Star className="w-3.5 h-3.5 fill-current" />
        <span className="text-xs font-medium">{starCount}</span>
        <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
      </Button>

      {/* Enhanced Theme Toggle */}
      <Button
        variant="ghost"
        size="sm"
        onClick={() => setTheme(isDark ? 'light' : 'dark')}
        className="relative w-14 h-7 p-0 rounded-full border-2 border-gray-300 dark:border-gray-600 bg-gradient-to-r from-blue-400 to-blue-600 dark:from-purple-600 dark:to-indigo-700 transition-all duration-500 hover:scale-105 hover:shadow-xl overflow-hidden group"
        aria-label="Toggle theme"
      >
        {/* Background gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-r from-yellow-300 via-orange-400 to-pink-400 dark:from-indigo-900 dark:via-purple-800 dark:to-blue-900 transition-opacity duration-500" />
        
        {/* Sliding circle */}
        <div
          className={`absolute top-0.5 w-6 h-6 bg-white dark:bg-gray-800 rounded-full shadow-xl transform transition-all duration-500 ease-in-out flex items-center justify-center border border-gray-200 dark:border-gray-600 ${
            isDark ? 'translate-x-7' : 'translate-x-0.5'
          }`}
        >
          {/* Icons with fade transition */}
          <div className="relative w-3.5 h-3.5">
            <Sun
              className={`absolute inset-0 w-3.5 h-3.5 text-yellow-500 transition-all duration-300 ${
                isDark ? 'opacity-0 rotate-180 scale-0' : 'opacity-100 rotate-0 scale-100'
              }`}
            />
            <Moon
              className={`absolute inset-0 w-3.5 h-3.5 text-blue-600 transition-all duration-300 ${
                isDark ? 'opacity-100 rotate-0 scale-100' : 'opacity-0 -rotate-180 scale-0'
              }`}
            />
          </div>
        </div>
        
        {/* Enhanced glowing effect */}
        <div
          className={`absolute inset-0 rounded-full transition-all duration-500 ${
            isDark
              ? 'shadow-[inset_0_0_15px_rgba(99,102,241,0.5),0_0_20px_rgba(99,102,241,0.3)] bg-gradient-to-r from-indigo-500/20 to-purple-600/20'
              : 'shadow-[inset_0_0_15px_rgba(251,191,36,0.5),0_0_20px_rgba(251,191,36,0.3)] bg-gradient-to-r from-yellow-400/20 to-orange-500/20'
          }`}
        />

        {/* Shine effect on hover */}
        <div className="absolute inset-0 rounded-full bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
      </Button>
    </div>
  )
} 