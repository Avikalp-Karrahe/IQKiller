'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'

export interface CreditTransaction {
  id: string
  user_id: string
  amount: number
  type: 'debit' | 'credit'
  description: string
  created_at: string
}

export interface CreditsData {
  credits: number
  transactions: CreditTransaction[]
  user: {
    id: string
    email: string
    full_name: string | null
    avatar_url: string | null
  }
}

export const useCredits = () => {
  const { user } = useAuth()
  const [credits, setCredits] = useState<number>(0)
  const [transactions, setTransactions] = useState<CreditTransaction[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchCredits = async () => {
    if (!user) return

    setLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/credits')
      
      if (!response.ok) {
        throw new Error('Failed to fetch credits')
      }

      const data: CreditsData = await response.json()
      setCredits(data.credits)
      setTransactions(data.transactions)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const deductCredits = async (amount: number, description: string) => {
    if (!user) {
      throw new Error('User not authenticated')
    }

    const response = await fetch('/api/credits', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ amount, description }),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Failed to deduct credits')
    }

    const data = await response.json()
    setCredits(data.credits)
    
    // Refresh transactions to show the new deduction
    await fetchCredits()
    
    return data
  }

  const hasEnoughCredits = (amount: number) => {
    return credits >= amount
  }

  useEffect(() => {
    if (user) {
      fetchCredits()
    } else {
      setCredits(0)
      setTransactions([])
    }
  }, [user])

  return {
    credits,
    transactions,
    loading,
    error,
    fetchCredits,
    deductCredits,
    hasEnoughCredits,
  }
}