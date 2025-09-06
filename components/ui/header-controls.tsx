'use client'

import { useTheme } from 'next-themes'
import { useEffect, useState } from 'react'
import { Sun, Moon, Star, ExternalLink, Github, MessageSquare, Coins } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { track } from '@vercel/analytics'
import { useAuth } from '@/contexts/AuthContext'
import { useCredits } from '@/hooks/useCredits'
import Link from 'next/link'

export function HeaderControls() {
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)
  const [starCount, setStarCount] = useState('4.3k')
  const { user } = useAuth()
  const { credits } = useCredits()
  // Track Discord clicks separately
  const handleDiscordClick = () => {
    track('Discord Button Clicked', {
      currentTheme: theme || 'unknown'
    })
  }

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
      setStarCount(stars > 1000 ? `${(stars / 1000).toFixed(1)}k` : stars.toString())
    } catch (error) {
      console.error('Error fetching GitHub stars:', error)
    }
  }

  const handleGitHubClick = () => {
    // Track GitHub star button click
    track('GitHub Star Button Clicked', {
      starCount: starCount,
      currentTheme: theme || 'unknown'
    })
  }

  const handleThemeToggle = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light'
    
    // Track theme toggle
    track('Theme Toggle', {
      fromTheme: theme || 'unknown',
      toTheme: newTheme
    })
    
    setTheme(newTheme)
  }

  if (!mounted) return null

  return (
    <div className="flex items-center gap-3">
      {/* Credits Link - Only show when user is authenticated */}
      {user && (
        <Link
          href="/credits"
          className="group relative overflow-hidden px-3 py-2 h-10
                     bg-gradient-to-r from-yellow-500 to-amber-600 hover:from-yellow-400 hover:to-amber-500
                     text-white rounded-full shadow-lg hover:shadow-xl
                     transition-all duration-300 ease-in-out hover:scale-105
                     border border-yellow-600/50"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent
                          transform -translate-x-full group-hover:translate-x-full transition-transform duration-700 ease-in-out"></div>

          <div className="relative flex items-center gap-1.5 z-10">
            <Coins className="w-4 h-4 text-white group-hover:text-gray-200 transition-colors duration-300" />
            <span className="text-sm font-bold tracking-wide text-white">{credits}</span>
            <span className="text-xs text-white/80">credits</span>
          </div>
        </Link>
      )}
      {/* Discord Community Button */}
      <a
        href="https://discord.gg/sEAEu6abdn"
        target="_blank"
        rel="noopener noreferrer"
        onClick={handleDiscordClick}
        className="group relative overflow-hidden px-3 py-2 h-10
                   bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500
                   text-white rounded-full shadow-lg hover:shadow-xl
                   transition-all duration-300 ease-in-out hover:scale-105
                   border border-indigo-700/50"
      >
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent
                        transform -translate-x-full group-hover:translate-x-full transition-transform duration-700 ease-in-out"></div>

        <div className="relative flex items-center gap-1.5 z-10">
          <MessageSquare className="w-4 h-4 text-white group-hover:text-gray-200 transition-colors duration-300" />
          <span className="text-sm font-bold tracking-wide text-white">Discord</span>
          <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-all duration-300 group-hover:translate-x-1" />
        </div>
      </a>
      {/* GitHub Star Badge */}
      <a
        href="https://github.com/Avikalp-Karrahe/IQKiller"
        target="_blank"
        rel="noopener noreferrer"
        onClick={handleGitHubClick}
        className="group relative overflow-hidden px-3 py-2 h-10 
                   bg-gradient-to-r from-gray-900 to-black hover:from-gray-800 hover:to-gray-900
                   dark:from-gray-800 dark:to-gray-900 dark:hover:from-gray-700 dark:hover:to-gray-800
                   text-white rounded-full shadow-lg hover:shadow-xl 
                   transition-all duration-300 ease-in-out hover:scale-105
                   border border-gray-700/50 dark:border-gray-600/50"
      >
        {/* Shimmer effect */}
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent 
                        transform -translate-x-full group-hover:translate-x-full transition-transform duration-700 ease-in-out"></div>
        
        <div className="relative flex items-center gap-1.5 z-10">
          <Github className="w-4 h-4 text-white group-hover:text-gray-200 transition-colors duration-300" />
          <Star className="w-4 h-4 fill-current text-yellow-400 group-hover:text-yellow-300 transition-colors duration-300 group-hover:rotate-12" />
          <span className="text-sm font-bold tracking-wide text-white">{starCount}</span>
          <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-all duration-300 group-hover:translate-x-1" />
        </div>
      </a>

      {/* Theme Toggle */}
      <button
        onClick={handleThemeToggle}
        className="group relative w-20 h-10 rounded-full p-1 
                   bg-gradient-to-r from-amber-400 to-orange-500 
                   dark:from-indigo-500 dark:to-purple-600
                   hover:from-amber-300 hover:to-orange-400 
                   dark:hover:from-indigo-400 dark:hover:to-purple-500
                   shadow-lg hover:shadow-xl transition-all duration-300 ease-in-out hover:scale-105
                   border-2 border-white/20 dark:border-white/10"
        aria-label="Toggle theme"
      >
        {/* Animated background glow */}
        <div className="absolute inset-0 rounded-full bg-gradient-to-r from-amber-400/50 to-orange-500/50 
                        dark:from-indigo-500/50 dark:to-purple-600/50 blur-lg opacity-0 group-hover:opacity-100 
                        transition-opacity duration-300"></div>
        
        {/* Sliding circle */}
        <div className={`relative w-8 h-8 rounded-full shadow-lg transform transition-all duration-300 ease-in-out
                        ${theme === 'light' ? 'translate-x-0' : 'translate-x-10'}
                        bg-white dark:bg-gray-800 border-2 border-white/30 dark:border-gray-600/30
                        group-hover:scale-110 group-hover:shadow-xl`}>
          
          {/* Light mode decorations */}
          <div className={`absolute inset-0 flex items-center justify-center transition-all duration-300
                          ${theme === 'light' ? 'opacity-100 rotate-0' : 'opacity-0 -rotate-180'}`}>
            <Sun className="w-4 h-4 text-amber-600 group-hover:rotate-12 transition-transform duration-300" />
            {/* Light rays */}
            <div className="absolute inset-0 rounded-full">
              <div className="absolute top-0 left-1/2 w-0.5 h-1 bg-amber-400 rounded-full transform -translate-x-1/2 -translate-y-1"></div>
              <div className="absolute bottom-0 left-1/2 w-0.5 h-1 bg-amber-400 rounded-full transform -translate-x-1/2 translate-y-1"></div>
              <div className="absolute left-0 top-1/2 w-1 h-0.5 bg-amber-400 rounded-full transform -translate-y-1/2 -translate-x-1"></div>
              <div className="absolute right-0 top-1/2 w-1 h-0.5 bg-amber-400 rounded-full transform -translate-y-1/2 translate-x-1"></div>
            </div>
          </div>
          
          {/* Dark mode decorations */}
          <div className={`absolute inset-0 flex items-center justify-center transition-all duration-300
                          ${theme === 'dark' ? 'opacity-100 rotate-0' : 'opacity-0 rotate-180'}`}>
            <Moon className="w-4 h-4 text-indigo-400 group-hover:-rotate-12 transition-transform duration-300" />
            {/* Stars */}
            <div className="absolute inset-0 rounded-full">
              <div className="absolute top-1 right-1 w-1 h-1 bg-purple-300 rounded-full"></div>
              <div className="absolute bottom-1 left-1 w-0.5 h-0.5 bg-indigo-300 rounded-full"></div>
              <div className="absolute top-2 left-2 w-0.5 h-0.5 bg-purple-400 rounded-full"></div>
            </div>
          </div>
        </div>
      </button>
    </div>
  )
}