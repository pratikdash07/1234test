"use client"

import { useState, useEffect } from "react"
import { ExternalLink } from "lucide-react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"

interface CreateWorkflowModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  folders: { id: string; name: string; workflowCount: number; isDefault: boolean }[]
  workflowId?: string
}

interface Engine {
  id: string
  name: string
  description: string
  url: string
  color: string
}

export function CreateWorkflowModal({ open, onOpenChange, folders, workflowId }: CreateWorkflowModalProps) {
  const [selectedEngine, setSelectedEngine] = useState<string>("")
  const [selectedFolder, setSelectedFolder] = useState<string>("unassigned")
  const [webhookUrl, setWebhookUrl] = useState("")
  const [cronExpression, setCronExpression] = useState("")
  const [manualPayload, setManualPayload] = useState("{}")
  const [runs, setRuns] = useState<any[]>([])
  const [workflowId, setWorkflowId] = useState<string>("");
  const engines = [
    {
      id: "n8n",
      name: "n8n",
      description: "Low-code automation platform with visual workflow builder",
      url: "http://localhost:5678/workflow",
      color: "bg-blue-100 text-blue-800",
    },
    {
      id: "langflow",
      name: "Langflow",
      description: "Visual framework for building multi-agent and RAG applications",
      url: "http://localhost:7860/flow-builder",
      color: "bg-green-100 text-green-800",
    },
    {
      id: "langsmith",
      name: "LangSmith",
      description: "Platform for building production-grade LLM applications",
      url: "https://smith.langchain.com/",
      color: "bg-purple-100 text-purple-800",
    }
  ]

  const fetchRuns = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/langflow/runs`)
      const data = await response.json()
      setRuns(data)
    } catch (error) {
      console.error("Failed to fetch runs:", error)
    }
  }

  useEffect(() => {
    if (open && selectedEngine === "langflow") {
      fetchRuns()
    }
  }, [open, selectedEngine])

  useEffect(() => {
    if (selectedEngine === "langflow" && workflowId) {
      setWebhookUrl(`${process.env.NEXT_PUBLIC_API_URL}/api/langflow/webhook/${workflowId}`);
    }
  }, [selectedEngine, workflowId]);


  const handleCreateWorkflow = async () => {
    const engine = engines.find(e => e.id === selectedEngine);
    if (!engine) return;

    // Validate required fields
    if (!workflowId) {
      alert("Please select a workflow first");
      return;
    }

    try {
      const payload = JSON.parse(manualPayload || "{}");  // Safer JSON parsing

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/langflow/trigger`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          workflowId: workflowId,  // No fallback value
          engine: "langflow",
          triggerType: "manual",
          inputPayload: payload
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Trigger failed");
      }

      const data = await response.json();
      console.log("Workflow triggered:", data);
      await fetchRuns();
    } catch (error) {
      console.error("Error:", error);
      alert(error instanceof Error ? error.message : "Failed to trigger workflow");
    }

    onOpenChange(false);
  };



  const renderLangflowTriggers = () => (
    <Tabs defaultValue="manual" className="mt-4">
      <TabsList>
        <TabsTrigger value="manual">Manual</TabsTrigger>
        <TabsTrigger value="webhook">Webhook</TabsTrigger>
        <TabsTrigger value="schedule">Schedule</TabsTrigger>
      </TabsList>

      <TabsContent value="manual">
        <Textarea
          value={manualPayload}
          onChange={(e) => setManualPayload(e.target.value)}
          placeholder="Enter JSON payload"
          className="mb-4"
        />
      </TabsContent>

      <TabsContent value="webhook">
        <Input
          value={webhookUrl}
          readOnly
          className="mb-2"
        />
        <Button onClick={() => navigator.clipboard.writeText(webhookUrl)}>
          Copy Webhook URL
        </Button>
      </TabsContent>

      <TabsContent value="schedule">
        <Input
          value={cronExpression}
          onChange={(e) => setCronExpression(e.target.value)}
          placeholder="* * * * *"
          className="mb-2"
        />
        <Button onClick={() => {
          fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/cron-jobs`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              id: `cron-${Date.now()}`,
              workflowId: workflowId || "workflow-id",
              schedule: { minute: cronExpression }
            })
          })
        }}>
          Schedule Job
        </Button>
      </TabsContent>
    </Tabs>
  )

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Create New Workflow</DialogTitle>
          <DialogDescription>
            Choose a platform and trigger type for your new automation workflow
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <Select value={selectedEngine} onValueChange={setSelectedEngine}>
            <SelectTrigger>
              <SelectValue placeholder="Select an automation engine" />
            </SelectTrigger>
            <SelectContent>
              {engines.map((engine) => (
                <SelectItem key={engine.id} value={engine.id}>
                  {engine.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={selectedFolder} onValueChange={setSelectedFolder}>
            <SelectTrigger>
              <SelectValue placeholder="Select a folder" />
            </SelectTrigger>
            <SelectContent>
              {folders.map((folder) => (
                <SelectItem key={folder.id} value={folder.id}>
                  {folder.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={workflowId} onValueChange={setWorkflowId}>
            <SelectTrigger>
              <SelectValue placeholder="Select a workflow" />
            </SelectTrigger>
            <SelectContent>
              {workflows.map((workflow) => (
                <SelectItem key={workflow.id} value={workflow.id}>
                  {workflow.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {selectedEngine === "langflow" && renderLangflowTriggers()}

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {engines.find(e => e.id === selectedEngine)?.name}
                <span className={`px-2 py-1 rounded text-xs ${engines.find(e => e.id === selectedEngine)?.color}`}>
                  {selectedEngine}
                </span>
              </CardTitle>
              <CardDescription>
                {engines.find(e => e.id === selectedEngine)?.description}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-600">
                  {selectedEngine === "langflow" ?
                    "Configure workflow triggers" :
                    `Opens in: ${engines.find(e => e.id === selectedEngine)?.url}`
                  }
                </div>
                <Button
                  onClick={handleCreateWorkflow}
                  className="bg-[#7575e4] hover:bg-[#6565d4] text-white"
                  disabled={!selectedFolder}
                >
                  <ExternalLink className="w-4 h-4 mr-2" />
                  {selectedEngine === "langflow" ? "Create Trigger" : "Create Workflow"}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </DialogContent>
    </Dialog>
  )
}
