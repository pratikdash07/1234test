"use client"

import { useState, useEffect } from "react"
import { ChevronDown, ChevronRight, Folder, FolderOpen, Settings, Workflow } from "lucide-react"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
} from "@/components/ui/sidebar"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"

interface AppSidebarProps {
  selectedFolder: string | null
  onFolderSelect: (folderId: string | null) => void
  onManageFolders: () => void
  folders: { id: string; name: string; workflowCount: number; isDefault: boolean }[]
}

interface Workflow {
  id: string
  name: string
  engine: string
}

export function AppSidebar({ selectedFolder, onFolderSelect, onManageFolders, folders }: AppSidebarProps) {
  const [expandedFolders, setExpandedFolders] = useState<string[]>(["unassigned"])
  const [workflows, setWorkflows] = useState<Record<string, Workflow[]>>({})
  const [loading, setLoading] = useState(true)

  // Mock workflows for Marketing Automation and Data Processing
  const mockWorkflows = {
    marketing: [
      { id: "wf-3", name: "Lead Scoring", engine: "n8n" },
      { id: "wf-4", name: "Campaign Tracker", engine: "langsmith" },
    ],
    "data-processing": [
      { id: "wf-5", name: "ETL Pipeline", engine: "langflow" },
      { id: "wf-6", name: "Report Generator", engine: "n8n" },
    ],
  }

  // Fetch workflows from backend
  useEffect(() => {
    const fetchWorkflows = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/langflow/flows`)
        if (!response.ok) throw new Error("Failed to fetch workflows")
        
        const data = await response.json()
        const backendFlows = data.map((flow: any) => ({
          id: flow.id,
          name: flow.name,
          engine: "langflow"
        }))

        // Map workflows to folders
        const updatedWorkflows: Record<string, Workflow[]> = {}
        folders.forEach(folder => {
          if (folder.id === "unassigned") {
            updatedWorkflows[folder.id] = backendFlows
          } else {
            // Use mock workflows for other folders
            updatedWorkflows[folder.id] = mockWorkflows[folder.id as keyof typeof mockWorkflows] || []
          }
        })
        
        setWorkflows(updatedWorkflows)
      } catch (error) {
        console.error("Error fetching workflows:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchWorkflows()
  }, [folders])

  const getWorkflowsForFolder = (folderId: string) => {
    return workflows[folderId] || []
  }

  const toggleFolder = (folderId: string) => {
    setExpandedFolders((prev) => 
      prev.includes(folderId) 
        ? prev.filter((id) => id !== folderId) 
        : [...prev, folderId]
    )
  }

  const getEngineColor = (engine: string) => {
    switch (engine) {
      case "n8n": return "bg-blue-100 text-blue-800"
      case "langflow": return "bg-green-100 text-green-800"
      case "langsmith": return "bg-purple-100 text-purple-800"
      default: return "bg-gray-100 text-gray-800"
    }
  }

  // Calculate total workflow count
  const totalWorkflows = folders.reduce(
    (acc, folder) => acc + (workflows[folder.id]?.length || 0), 
    0
  )

  return (
    <Sidebar className="border-r border-gray-200">
      <SidebarHeader className="border-b border-gray-200 p-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-[#7575e4] rounded-lg flex items-center justify-center">
            <Workflow className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-semibold text-gray-900">FlowBit</h1>
            <p className="text-xs text-gray-500">Orchestration</p>
          </div>
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel className="flex items-center justify-between">
            <span>Workflows</span>
            <Button variant="ghost" size="sm" onClick={onManageFolders} className="h-6 w-6 p-0">
              <Settings className="w-3 h-3" />
            </Button>
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton
                  onClick={() => onFolderSelect(null)}
                  isActive={selectedFolder === null}
                  className="w-full justify-start"
                >
                  <Workflow className="w-4 h-4" />
                  <span>All Workflows</span>
                  <Badge variant="secondary" className="ml-auto">
                    {totalWorkflows}
                  </Badge>
                </SidebarMenuButton>
              </SidebarMenuItem>

              {folders.map((folder) => {
                const folderName = folder.id === "unassigned" ? "Document Classification" : folder.name
                const folderWorkflows = getWorkflowsForFolder(folder.id)
                return (
                  <Collapsible
                    key={folder.id}
                    open={expandedFolders.includes(folder.id)}
                    onOpenChange={() => toggleFolder(folder.id)}
                  >
                    <SidebarMenuItem>
                      <CollapsibleTrigger asChild>
                        <SidebarMenuButton className="w-full justify-start">
                          {expandedFolders.includes(folder.id) ? (
                            <ChevronDown className="w-4 h-4" />
                          ) : (
                            <ChevronRight className="w-4 h-4" />
                          )}
                          {expandedFolders.includes(folder.id) ? (
                            <FolderOpen className="w-4 h-4" />
                          ) : (
                            <Folder className="w-4 h-4" />
                          )}
                          <span>{folderName}</span>
                          <Badge variant="secondary" className="ml-auto">
                            {folderWorkflows.length}
                          </Badge>
                        </SidebarMenuButton>
                      </CollapsibleTrigger>
                      <CollapsibleContent>
                        <SidebarMenuSub>
                          {folderWorkflows.map((workflow) => (
                            <SidebarMenuSubItem key={workflow.id}>
                              <SidebarMenuSubButton
                                onClick={() => onFolderSelect(folder.id)}
                                isActive={selectedFolder === folder.id}
                                className="flex items-center justify-between"
                              >
                                <span className="truncate">{workflow.name}</span>
                                <Badge variant="outline" className={`text-xs ${getEngineColor(workflow.engine)}`}>
                                  {workflow.engine}
                                </Badge>
                              </SidebarMenuSubButton>
                            </SidebarMenuSubItem>
                          ))}
                        </SidebarMenuSub>
                      </CollapsibleContent>
                    </SidebarMenuItem>
                  </Collapsible>
                )
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t border-gray-200 p-4">
        <div className="text-xs text-gray-500">FlowBit Orchestration v1.1</div>
      </SidebarFooter>
    </Sidebar>
  )
}
