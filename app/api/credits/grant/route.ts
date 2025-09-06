import { NextRequest, NextResponse } from "next/server";
import { createServerAdminSupabase } from "@/lib/supabase/admin";

export async function POST(req: NextRequest) {
  const { user_id, amount, reason, meta } = await req.json();
  const sb = createServerAdminSupabase();
  const { data, error } = await sb.rpc("admin_grant_credits", { target: user_id, amount, reason, meta });
  if (error) return NextResponse.json({ error: error.message }, { status: 400 });
  return NextResponse.json({ credits: data });
}