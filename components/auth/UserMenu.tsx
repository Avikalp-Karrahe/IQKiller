"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { createClientComponentClient } from "@/lib/supabase-client";

export default function UserMenu() {
  const [user, setUser] = useState<any>(null);
  
  useEffect(() => {
    createClientComponentClient().auth.getUser().then(({ data }) => setUser(data.user));
  }, []);
  
  if (!user) {
    return (
      <Link href="/auth/signin" className="text-sm opacity-80 hover:opacity-100">
        Sign in
      </Link>
    );
  }
  
  const logout = async () => {
    await createClientComponentClient().auth.signOut();
    location.href = "/";
  };
  
  return (
    <div className="flex items-center gap-3">
      <span className="text-sm opacity-80">{user.email}</span>
      <button onClick={logout} className="text-sm opacity-80 hover:opacity-100">
        Sign out
      </button>
      <Link href="/dashboard/credits" className="text-sm underline/40 hover:underline">
        Credits
      </Link>
    </div>
  );
}