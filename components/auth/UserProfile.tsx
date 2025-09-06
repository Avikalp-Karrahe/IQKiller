'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { useAuth } from '@/contexts/AuthContext'
import { LogOut, User, CreditCard, Linkedin } from 'lucide-react'
import { toast } from 'sonner'

export function UserProfile() {
  const { user, userProfile, signOut } = useAuth()
  const [isSigningOut, setIsSigningOut] = useState(false)

  if (!user || !userProfile) return null

  const handleSignOut = async () => {
    try {
      setIsSigningOut(true)
      await signOut()
      toast.success('Signed out successfully')
    } catch (error) {
      console.error('Sign out error:', error)
      toast.error('Failed to sign out')
    } finally {
      setIsSigningOut(false)
    }
  }

  const handleRequestCredits = () => {
    const linkedinUrl = 'https://www.linkedin.com/in/avikalp-karrahe/'
    const message = encodeURIComponent(
      `Hi Avikalp! I'm using IQKiller and would like to request more credits. My email: ${user.email}`
    )
    window.open(`${linkedinUrl}?message=${message}`, '_blank')
  }

  const getInitials = (name: string | null) => {
    if (!name) return user.email?.charAt(0).toUpperCase() || 'U'
    return name
      .split(' ')
      .map(n => n.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="relative h-10 w-10 rounded-full">
          <Avatar className="h-10 w-10">
            <AvatarImage src={userProfile.avatar_url || ''} alt={userProfile.full_name || ''} />
            <AvatarFallback>{getInitials(userProfile.full_name)}</AvatarFallback>
          </Avatar>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-80" align="end" forceMount>
        <DropdownMenuLabel className="font-normal">
          <div className="flex flex-col space-y-2">
            <div className="flex items-center space-x-2">
              <Avatar className="h-8 w-8">
                <AvatarImage src={userProfile.avatar_url || ''} alt={userProfile.full_name || ''} />
                <AvatarFallback className="text-xs">{getInitials(userProfile.full_name)}</AvatarFallback>
              </Avatar>
              <div className="flex flex-col">
                <p className="text-sm font-medium leading-none">
                  {userProfile.full_name || 'User'}
                </p>
                <p className="text-xs leading-none text-muted-foreground">
                  {user.email}
                </p>
              </div>
            </div>
            <div className="flex items-center justify-between pt-2">
              <div className="flex items-center space-x-2">
                <CreditCard className="h-4 w-4 text-blue-600" />
                <span className="text-sm font-medium">Credits:</span>
              </div>
              <Badge variant={userProfile.credits > 5 ? 'default' : userProfile.credits > 0 ? 'secondary' : 'destructive'}>
                {userProfile.credits}
              </Badge>
            </div>
            {userProfile.credits <= 5 && (
              <div className="pt-2">
                <Button
                  onClick={handleRequestCredits}
                  size="sm"
                  variant="outline"
                  className="w-full text-xs"
                >
                  <Linkedin className="mr-2 h-3 w-3" />
                  Request More Credits
                </Button>
              </div>
            )}
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={handleRequestCredits}>
          <Linkedin className="mr-2 h-4 w-4" />
          <span>Contact for Credits</span>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={handleSignOut} disabled={isSigningOut}>
          <LogOut className="mr-2 h-4 w-4" />
          <span>{isSigningOut ? 'Signing out...' : 'Sign out'}</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}