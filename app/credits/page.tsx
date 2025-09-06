import React from 'react'
import CreditsDashboard from '@/components/CreditsDashboard'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Credits - IQ Killer',
  description: 'Manage your IQ Killer credits and view usage history',
}

export default function CreditsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Page Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-4">
              Your Credits
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              Manage your IQ Killer credits, view usage history, and request additional credits when needed.
            </p>
          </div>

          {/* Credits Dashboard */}
          <CreditsDashboard />
        </div>
      </div>
    </div>
  )
}