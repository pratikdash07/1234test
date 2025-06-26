import { NextResponse } from "next/server";

export async function GET(
  request: Request,
  { params }: { params: { workflowId: string } }
) {
  return NextResponse.json({
    url: `${process.env.NEXT_PUBLIC_BASE_URL || "http://localhost:3000"}/api/hooks/${params.workflowId}`,
    webhookId: crypto.randomUUID()
  });
}

export async function POST(
  request: Request,
  { params }: { params: { workflowId: string } }
) {
  const payload = await request.json();

  // Forward to your backend
  const backendUrl = process.env.LANGFLOW_BASE_URL || "http://localhost:8000";
  const response = await fetch(`${backendUrl}/api/langflow/trigger`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      workflowId: params.workflowId,
      triggerType: "webhook",
      inputPayload: payload
    })
  });

  if (!response.ok) {
    return NextResponse.json({ error: "Failed to trigger workflow" }, { status: 500 });
  }

  return NextResponse.json({ success: true });
}
