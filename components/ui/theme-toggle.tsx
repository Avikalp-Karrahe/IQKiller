'use client'

import { useTheme } from 'next-themes'
import { useEffect, useState } from 'react'
import { Sun, Moon } from 'lucide-react'
import { Button } from '@/components/ui/button'

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return (
      <div className="w-12 h-6 bg-gray-200 dark:bg-gray-700 rounded-full animate-pulse" />
    )
  }

  const isDark = theme === 'dark'

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={() => setTheme(isDark ? 'light' : 'dark')}
      className="relative w-12 h-6 p-0 rounded-full border-2 border-gray-300 dark:border-gray-600 bg-gradient-to-r from-blue-400 to-blue-600 dark:from-purple-600 dark:to-indigo-700 transition-all duration-500 hover:scale-105 hover:shadow-lg overflow-hidden"
      aria-label="Toggle theme"
    >
      {/* Background gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-r from-yellow-300 via-orange-400 to-pink-400 dark:from-indigo-900 dark:via-purple-800 dark:to-blue-900 transition-opacity duration-500" />
      
      {/* Sliding circle */}
      <div
        className={`absolute top-0.5 w-5 h-5 bg-white dark:bg-gray-800 rounded-full shadow-lg transform transition-all duration-500 ease-in-out flex items-center justify-center ${
          isDark ? 'translate-x-6' : 'translate-x-0.5'
        }`}
      >
        {/* Icons with fade transition */}
        <div className="relative w-3 h-3">
          <Sun
            className={`absolute inset-0 w-3 h-3 text-yellow-500 transition-all duration-300 ${
              isDark ? 'opacity-0 rotate-180 scale-0' : 'opacity-100 rotate-0 scale-100'
            }`}
          />
          <Moon
            className={`absolute inset-0 w-3 h-3 text-blue-600 transition-all duration-300 ${
              isDark ? 'opacity-100 rotate-0 scale-100' : 'opacity-0 -rotate-180 scale-0'
            }`}
          />
        </div>
      </div>
      
      {/* Glowing effect */}
      <div
        className={`absolute inset-0 rounded-full transition-all duration-500 ${
          isDark
            ? 'shadow-[inset_0_0_12px_rgba(99,102,241,0.4)] bg-gradient-to-r from-indigo-500/20 to-purple-600/20'
            : 'shadow-[inset_0_0_12px_rgba(251,191,36,0.4)] bg-gradient-to-r from-yellow-400/20 to-orange-500/20'
        }`}
      />
    </Button>
  )
} 