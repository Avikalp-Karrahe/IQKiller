import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export async function middleware(req: NextRequest) {
  const url = new URL(req.url);
  if (url.pathname.startsWith("/prep") || url.pathname.startsWith("/dashboard")) {
    // simple check: rely on Supabase cookie (sb-access-token)
    const hasToken = !!req.cookies.get("sb-access-token");
    if (!hasToken) {
      url.pathname = "/";
      url.searchParams.set("next", "/prep");
      return NextResponse.redirect(url);
    }
  }
  return NextResponse.next();
}

export const config = { matcher: ["/prep/:path*", "/dashboard/:path*"] };