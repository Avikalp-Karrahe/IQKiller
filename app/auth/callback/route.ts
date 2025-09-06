import { createRouteHandlerClient } from '@/lib/supabase-server'
import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url)
  const code = requestUrl.searchParams.get('code')

  if (code) {
    const supabase = createRouteHandlerClient(request)
    const { error } = await supabase.auth.exchangeCodeForSession(code)
    
    if (error) {
      console.error('Error exchanging code for session:', error)
      return NextResponse.redirect(`${requestUrl.origin}/auth/error`)
    }
  }

  // Check if there's a 'next' parameter for custom redirect
  const next = requestUrl.searchParams.get('next')
  const redirectTo = next || '/prep'
  
  // Redirect to prep page after successful authentication
  return NextResponse.redirect(`${requestUrl.origin}${redirectTo}`)
}