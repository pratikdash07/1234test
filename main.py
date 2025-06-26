from fastapi import FastAPI, UploadFile, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from agents.classifier_agent.classifier import ClassifierAgent
from agents.email_agent.email_agent import EmailAgent
from agents.json_agent.json_agent import JSONAgent
from agents.pdf_agent.pdf_agent import PDFAgent
from core.routers.action_router import ActionRouter
from core.memory.redis_client import MemoryStore
from langflow_api import langflow_router
import os
from typing import Optional
import json
import logging
import asyncio
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import httpx
from pydantic import BaseModel

app = FastAPI()

# ===== CHANGED: Added prefix to router =====
app.include_router(langflow_router, prefix="/api")

# Set up logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/processing.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Redis configuration
REDIS_RUNS_KEY = "workflow_runs"
REDIS_MAX_RUNS = 50

# Cron job configuration
CRON_JOBS_FILE = "lib/cron-jobs.json"

class WorkflowRun(BaseModel):
    id: str
    flow_id: str
    status: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None

def load_cron_jobs():
    if os.path.exists(CRON_JOBS_FILE):
        with open(CRON_JOBS_FILE, "r") as f:
            return json.load(f)
    return []

def save_cron_jobs(jobs):
    with open(CRON_JOBS_FILE, "w") as f:
        json.dump(jobs, f, indent=2)

def trigger_workflow(workflow_id: str):
    try:
        response = httpx.post(
            "http://localhost:8000/api/langflow/trigger",
            json={
                "flowId": workflow_id,
                "triggerType": "cron",
                "inputPayload": {}
            }
        )
        logger.info(f"Triggered workflow {workflow_id}: {response.json()}")
    except Exception as e:
        logger.error(f"Error triggering workflow {workflow_id}: {str(e)}")

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Load existing cron jobs on startup
for job in load_cron_jobs():
    scheduler.add_job(
        trigger_workflow,
        "cron",
        args=[job["workflowId"]],
        id=job["id"],
        **job["schedule"]
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
classifier = ClassifierAgent()
email_agent = EmailAgent()
json_agent = JSONAgent()
pdf_agent = PDFAgent()
action_router = ActionRouter()
memory_store = MemoryStore()

flows = [
    {"id": "email", "name": "Email Agent"},
    {"id": "json", "name": "JSON Agent"},
    {"id": "pdf", "name": "PDF Agent"},
    {"id": "classifier", "name": "Classifier Agent"}
]

def store_run(run: WorkflowRun):
    try:
        memory_store.conn.zadd(REDIS_RUNS_KEY, {run.json(): run.start_time})
        memory_store.conn.zremrangebyrank(REDIS_RUNS_KEY, 0, -REDIS_MAX_RUNS)
    except Exception as e:
        logger.error(f"Error storing run: {str(e)}")

# Cron job management endpoints
@app.post("/api/cron-jobs")
async def add_cron_job(request: Request):
    try:
        data = await request.json()
        jobs = load_cron_jobs()
        
        if "id" not in data or "workflowId" not in data or "schedule" not in data:
            raise HTTPException(status_code=400, detail="Missing required fields: id, workflowId, schedule")
        
        jobs.append(data)
        save_cron_jobs(jobs)
        
        scheduler.add_job(
            trigger_workflow,
            "cron",
            args=[data["workflowId"]],
            id=data["id"],
            **data["schedule"]
        )
        
        return {"success": True}
    except Exception as e:
        logger.error(f"Error adding cron job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cron-jobs")
async def list_cron_jobs():
    return load_cron_jobs()

@app.post("/process-file")
async def process_file(file: UploadFile):
    try:
        filename = file.filename
        ext = os.path.splitext(filename)[1].lower()
        source_id = os.path.splitext(filename)[0]

        logger.info(f"Started processing: {filename}")

        # Read content
        if ext == ".pdf":
            temp_path = f"temp_{filename}"
            with open(temp_path, "wb") as f_out:
                content_bytes = await file.read()
                f_out.write(content_bytes)
            content = None
        else:
            content_bytes = await file.read()
            content = content_bytes.decode("utf-8")
            temp_path = None

        # Classify
        classification = classifier.classify(filename, content if content else "")
        logger.info(f"Classification result: {classification}")

        # Agent processing
        if classification["format"] == "Email":
            result = email_agent.process(filename, content, classification)
            action = result["action"]
        elif classification["format"] == "JSON":
            result = json_agent.process(filename, content, classification)
            action = "alert" if not result["valid"] else "accept"
        elif classification["format"] == "PDF":
            result = pdf_agent.process(temp_path, classification)
            action = result.get("flag", "accepted")
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")

        logger.info(f"Processing result: {result}")

        # Action routing
        payload = {"source_id": source_id, "result": result}
        action_result = action_router.route_action(
            action if action in action_router.endpoints else "routine", 
            payload
        )
        logger.info(f"Action result: {action_result}")

        # Get and log full trace
        trace = memory_store.get_full_trace(source_id)
        logger.info(f"Redis trace data: {trace}")

        # Cleanup
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        return {
            "classification": classification,
            "processing_result": result,
            "action_router_result": action_result,
            "full_trace": trace
        }

    except Exception as e:
        logger.error(f"Error processing {filename}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
