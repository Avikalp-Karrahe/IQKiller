"use client";
import { createClientComponentClient } from "@/lib/supabase-client";

export default function SignInButton() {
  const login = async () => {
    const sb = createClientComponentClient();
    const origin = window.location.origin;
    await sb.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${origin}/auth/callback?next=/prep`
      }
    });
  };
  
  return (
    <button 
      onClick={login} 
      className="px-4 py-2 rounded-xl border border-white/15 hover:border-white/30"
    >
      Sign in with Google
    </button>
  );
}