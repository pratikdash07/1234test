import { NextResponse } from "next/server";

export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  const runId = params.id;
  // TODO: Query Redis for full run details
  // For now, return mock data
  return NextResponse.json({
    id: runId,
    status: "completed",
    flowName: "Email Agent",
    output: "Mock output for run " + runId,
    logs: [],
    createdAt: new Date().toISOString(),
    duration: 2000
  });
}
