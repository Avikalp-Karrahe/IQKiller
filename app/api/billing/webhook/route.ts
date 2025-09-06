import { NextRequest, NextResponse } from "next/server";
import { stripe } from "@/lib/stripe";
import { createServerAdminSupabase } from "@/lib/supabase/admin";

export const config = { api: { bodyParser: false } } as any;

export async function POST(req: NextRequest) {
  const payload = await req.text();
  const sig = req.headers.get("stripe-signature")!;
  let event;
  
  try {
    event = stripe.webhooks.constructEvent(payload, sig, process.env.STRIPE_WEBHOOK_SECRET!);
  } catch (err: any) {
    return new NextResponse(`Webhook Error: ${err.message}`, { status: 400 });
  }

  if (event.type === "checkout.session.completed") {
    const s = event.data.object as any;
    const userId = s.metadata?.user_id;
    const credits = parseInt(s.metadata?.credits || "0", 10);
    
    if (userId && credits > 0) {
      const sb = createServerAdminSupabase();
      await sb.rpc("admin_grant_credits", {
        target: userId,
        amount: credits,
        reason: "purchase",
        meta: { checkout: s.id }
      });
    }
  }
  
  return NextResponse.json({ received: true });
}