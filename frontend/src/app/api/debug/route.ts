import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";

export async function GET(request: NextRequest) {
  try {
    // Try to get session
    const session = await auth.api.getSession({
      headers: request.headers,
    });

    return NextResponse.json({
      success: true,
      hasSession: !!session,
      session: session ? {
        userId: session.user?.id,
        userEmail: session.user?.email,
        sessionId: session.session?.id,
      } : null,
      cookies: request.cookies.getAll().map(c => ({ name: c.name, hasValue: !!c.value })),
    });
  } catch (error: any) {
    return NextResponse.json({
      success: false,
      error: error.message,
      stack: error.stack,
    }, { status: 500 });
  }
}
