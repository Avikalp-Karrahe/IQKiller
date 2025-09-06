'use client'

import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { useCredits } from '@/hooks/useCredits'
import { useAuth } from '@/contexts/AuthContext'
import { Coins, History, Plus, ExternalLink, Loader2, AlertCircle, CheckCircle, Minus } from 'lucide-react'
import { toast } from 'sonner'

interface CreditsDashboardProps {
  className?: string
}

export default function CreditsDashboard({ className }: CreditsDashboardProps) {
  const { user } = useAuth()
  const { credits, transactions, loading, error, fetchCredits } = useCredits()

  const handleRequestCredits = () => {
    const linkedInUrl = 'https://www.linkedin.com/in/avikalp-karrahe/'
    const message = `Hi Avikalp! I'm using IQ Killer and would like to request additional credits. My email: ${user?.email}`
    const encodedMessage = encodeURIComponent(message)
    const fullUrl = `${linkedInUrl}?message=${encodedMessage}`
    
    window.open(fullUrl, '_blank')
    toast.success('LinkedIn opened! Send me a message to request more credits.')
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getTransactionIcon = (type: 'debit' | 'credit') => {
    return type === 'credit' ? (
      <Plus className="w-4 h-4 text-green-600" />
    ) : (
      <Minus className="w-4 h-4 text-red-600" />
    )
  }

  const getTransactionColor = (type: 'debit' | 'credit') => {
    return type === 'credit' ? 'text-green-600' : 'text-red-600'
  }

  const getCreditsBadgeVariant = (credits: number) => {
    if (credits >= 10) return 'default'
    if (credits >= 5) return 'secondary'
    return 'destructive'
  }

  if (!user) {
    return (
      <Card className={className}>
        <CardContent className="flex items-center justify-center p-8">
          <div className="text-center">
            <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-400">Please sign in to view your credits</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (loading) {
    return (
      <Card className={className}>
        <CardContent className="flex items-center justify-center p-8">
          <div className="text-center">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-400">Loading your credits...</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className={className}>
        <CardContent className="flex items-center justify-center p-8">
          <div className="text-center">
            <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
            <Button onClick={fetchCredits} variant="outline" size="sm">
              Try Again
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Credits Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Coins className="w-5 h-5 text-yellow-600" />
            Your Credits
          </CardTitle>
          <CardDescription>
            Use credits to run interview analyses and get personalized preparation
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="text-3xl font-bold text-gray-900 dark:text-gray-100">
                {credits}
              </div>
              <Badge variant={getCreditsBadgeVariant(credits)} className="text-sm">
                {credits >= 10 ? 'Plenty' : credits >= 5 ? 'Good' : 'Low'}
              </Badge>
            </div>
            <Button 
              onClick={handleRequestCredits}
              variant="outline"
              size="sm"
              className="flex items-center gap-2"
            >
              <ExternalLink className="w-4 h-4" />
              Request More
            </Button>
          </div>
          
          {/* Credit Usage Progress */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
              <span>Credits Used This Session</span>
              <span>{Math.max(0, 10 - credits)}/10</span>
            </div>
            <Progress 
              value={Math.max(0, (10 - credits) / 10 * 100)} 
              className="h-2"
            />
          </div>
          
          {credits <= 2 && (
            <div className="mt-4 p-3 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg">
              <div className="flex items-center gap-2 text-orange-800 dark:text-orange-200">
                <AlertCircle className="w-4 h-4" />
                <span className="text-sm font-medium">Low Credits Warning</span>
              </div>
              <p className="text-sm text-orange-700 dark:text-orange-300 mt-1">
                You're running low on credits. Each analysis costs 1 credit.
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Transaction History */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="w-5 h-5 text-blue-600" />
            Usage History
          </CardTitle>
          <CardDescription>
            Your recent credit transactions and analysis history
          </CardDescription>
        </CardHeader>
        <CardContent>
          {transactions.length === 0 ? (
            <div className="text-center py-8">
              <History className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 dark:text-gray-400">No transactions yet</p>
              <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">
                Your credit usage will appear here
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {transactions.slice(0, 10).map((transaction) => (
                <div 
                  key={transaction.id} 
                  className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    {getTransactionIcon(transaction.type)}
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        {transaction.description}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {formatDate(transaction.created_at)}
                      </p>
                    </div>
                  </div>
                  <div className={`text-sm font-medium ${getTransactionColor(transaction.type)}`}>
                    {transaction.type === 'credit' ? '+' : '-'}{transaction.amount}
                  </div>
                </div>
              ))}
              
              {transactions.length > 10 && (
                <div className="text-center pt-2">
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Showing 10 most recent transactions
                  </p>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* How Credits Work */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">How Credits Work</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 text-sm text-gray-600 dark:text-gray-400">
            <div className="flex items-start gap-2">
              <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
              <span>Each complete interview analysis costs <strong>1 credit</strong></span>
            </div>
            <div className="flex items-start gap-2">
              <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
              <span>New users start with <strong>10 free credits</strong></span>
            </div>
            <div className="flex items-start gap-2">
              <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
              <span>Request more credits by contacting me on LinkedIn</span>
            </div>
            <div className="flex items-start gap-2">
              <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
              <span>Credits never expire and roll over between sessions</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}