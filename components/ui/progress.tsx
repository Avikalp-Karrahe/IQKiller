import React from 'react'

interface ProgressProps {
  value: number
  className?: string
}

export function Progress({ value, className = '' }: ProgressProps) {
  return (
    <div className={`w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 ${className}`}>
      <div 
        className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 h-2.5 rounded-full transition-all duration-300 ease-out shadow-sm" 
        style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
      />
    </div>
  )
}
