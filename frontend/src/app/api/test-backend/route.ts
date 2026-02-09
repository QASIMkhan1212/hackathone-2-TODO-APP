import { NextResponse } from "next/server";

export async function GET() {
  try {
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    console.log("Testing backend connection to:", backendUrl);

    const response = await fetch(backendUrl, {
      method: "GET",
    });

    const data = await response.json();

    return NextResponse.json({
      success: true,
      backendUrl,
      backendResponse: data,
      message: "Backend is reachable from Next.js server",
    });
  } catch (error: any) {
    return NextResponse.json({
      success: false,
      error: error.message,
      message: "Backend is NOT reachable from Next.js server",
    }, { status: 500 });
  }
}
