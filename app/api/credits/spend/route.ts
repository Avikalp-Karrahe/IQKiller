import { NextRequest, NextResponse } from "next/server";
import { createServerSupabase } from "@/lib/supabase/server";

export async function POST(req: NextRequest) {
  const { amount, reason, meta } = await req.json();
  const sb = createServerSupabase();
  const { data: { user } } = await sb.auth.getUser();
  if (!user) return NextResponse.json({ error: "auth" }, { status: 401 });
  const { data, error } = await sb.rpc("spend_credits", { amount, reason, meta });
  if (error) return NextResponse.json({ error: error.message }, { status: 400 });
  return NextResponse.json({ credits: data });
}