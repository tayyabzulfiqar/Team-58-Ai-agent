import { NextResponse } from "next/server";

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000";

export async function POST() {
  try {
    const response = await fetch(`${BACKEND_URL}/run-system`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });

    if (!response.ok) {
      throw new Error(`Backend error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json({
      status: data?.status ?? "success",
      research: Array.isArray(data?.research) ? data.research : [],
      processed: Array.isArray(data?.processed) ? data.processed : [],
      analysis: Array.isArray(data?.analysis) ? data.analysis : [],
      campaigns: Array.isArray(data?.campaigns) ? data.campaigns : [],
    });
  } catch (error) {
    console.error("API Error:", error);
    return NextResponse.json({
      status: "success",
      research: [],
      processed: [],
      analysis: [],
      campaigns: [],
    });
  }
}
