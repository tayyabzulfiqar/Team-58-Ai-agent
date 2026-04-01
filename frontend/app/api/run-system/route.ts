import { NextResponse } from "next/server";

const BACKEND_URL = "https://team-58-ai-agent-production.up.railway.app";

export async function POST() {
  try {
    const response = await fetch(`${BACKEND_URL}/run-system`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`Backend error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("API Error:", error);
    return NextResponse.json(
      {
        opportunities: [],
        scores: [],
        decisions: [],
        campaigns: [],
        status: "error",
        message: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}
