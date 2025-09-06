import { NextResponse } from "next/server";
import { createServerSupabase } from "@/lib/supabase/server";

export async function GET() {
  const sb = createServerSupabase();
  const { data: { user } } = await sb.auth.getUser();
  if (!user) return NextResponse.json({ credits: 0 });
  const { data, error } = await sb.from("profiles").select("credits").eq("id", user.id).single();
  if (error) return NextResponse.json({ credits: 0 });
  return NextResponse.json({ credits: data.credits });
}