import { createRouteHandlerClient } from '@/lib/supabase-server'
import { NextRequest, NextResponse } from 'next/server'

// GET /api/credits - Get user credits and transaction history
export async function GET(request: NextRequest) {
  try {
    const supabase = createRouteHandlerClient(request)
    
    // Get the current user
    const { data: { user }, error: authError } = await supabase.auth.getUser()
    
    if (authError || !user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

    // Get user profile with credits
    const { data: userProfile, error: profileError } = await supabase
      .from('users')
      .select('*')
      .eq('id', user.id)
      .single()

    if (profileError) {
      console.error('Error fetching user profile:', profileError)
      return NextResponse.json(
        { error: 'Failed to fetch user profile' },
        { status: 500 }
      )
    }

    // Get transaction history (last 50 transactions)
    const { data: transactions, error: transactionsError } = await supabase
      .from('credit_transactions')
      .select('*')
      .eq('user_id', user.id)
      .order('created_at', { ascending: false })
      .limit(50)

    if (transactionsError) {
      console.error('Error fetching transactions:', transactionsError)
      return NextResponse.json(
        { error: 'Failed to fetch transaction history' },
        { status: 500 }
      )
    }

    return NextResponse.json({
      credits: userProfile.credits,
      transactions: transactions || [],
      user: {
        id: userProfile.id,
        email: userProfile.email,
        full_name: userProfile.full_name,
        avatar_url: userProfile.avatar_url,
      }
    })

  } catch (error) {
    console.error('Credits API error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

// POST /api/credits - Deduct credits (for internal use)
export async function POST(request: NextRequest) {
  try {
    const supabase = createRouteHandlerClient(request)
    const body = await request.json()
    const { amount, description } = body

    if (!amount || !description) {
      return NextResponse.json(
        { error: 'Amount and description are required' },
        { status: 400 }
      )
    }

    if (amount <= 0) {
      return NextResponse.json(
        { error: 'Amount must be positive' },
        { status: 400 }
      )
    }

    // Get the current user
    const { data: { user }, error: authError } = await supabase.auth.getUser()
    
    if (authError || !user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

    // Call the deduct_credits function
    const { data, error } = await supabase.rpc('deduct_credits', {
      p_user_id: user.id,
      p_amount: amount,
      p_description: description
    })

    if (error) {
      console.error('Error deducting credits:', error)
      return NextResponse.json(
        { error: 'Failed to deduct credits' },
        { status: 500 }
      )
    }

    if (!data) {
      return NextResponse.json(
        { error: 'Insufficient credits' },
        { status: 402 } // Payment Required
      )
    }

    // Get updated user credits
    const { data: updatedUser, error: fetchError } = await supabase
      .from('users')
      .select('credits')
      .eq('id', user.id)
      .single()

    if (fetchError) {
      console.error('Error fetching updated credits:', fetchError)
    }

    return NextResponse.json({
      success: true,
      credits: updatedUser?.credits || 0,
      message: `${amount} credits deducted successfully`
    })

  } catch (error) {
    console.error('Credits deduction API error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}