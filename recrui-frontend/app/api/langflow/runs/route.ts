import { NextResponse } from "next/server";

export async function GET() {
  // TODO: Query Redis for last 50 runs
  // For now, return mock data
  return NextResponse.json({
    runs: [
      {
        id: "run_email_1234",
        status: "completed",
        flowName: "Email Agent",
        duration: 2000, // duration in ms
        createdAt: new Date().toISOString()
      }
      // Add more mock runs as needed
    ]
  });
}
