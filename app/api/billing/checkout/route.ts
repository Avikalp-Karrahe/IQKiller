import { NextRequest, NextResponse } from "next/server";
import { stripe } from "@/lib/stripe";
import { createServerSupabase } from "@/lib/supabase/server";

const PACKS: Record<string, { qty: number; price: number }> = {
  pack_20: { qty: 20, price: 500 },
  pack_100: { qty: 100, price: 1900 },
  pack_300: { qty: 300, price: 4900 }
};

export async function POST(req: NextRequest) {
  const form = await req.formData();
  const packId = String(form.get("pack") || "");
  const pack = PACKS[packId];
  if (!pack) return NextResponse.redirect("/pricing", 303);
  
  const sb = createServerSupabase();
  const { data: { user } } = await sb.auth.getUser();
  if (!user) return NextResponse.redirect("/auth/signin", 303);
  
  const session = await stripe.checkout.sessions.create({
    mode: "payment",
    success_url: `${process.env.NEXT_PUBLIC_BASE_URL}/dashboard/credits?ok=1`,
    cancel_url: `${process.env.NEXT_PUBLIC_BASE_URL}/pricing`,
    line_items: [{
      price_data: {
        currency: "usd",
        product_data: { name: `${pack.qty} credits` },
        unit_amount: pack.price
      },
      quantity: 1
    }],
    metadata: { user_id: user.id, credits: String(pack.qty) }
  });
  
  return NextResponse.redirect(session.url!, 303);
}