import asyncio
import json
from datetime import datetime
from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from core.memory.redis_client import MemoryStore
from typing import Optional
from pydantic import BaseModel, ValidationError
import logging
import uuid

print("langflow_api.py loaded")

REDIS_RUNS_KEY = "workflow_runs"
REDIS_MAX_RUNS = 50

class WorkflowRun(BaseModel):
    id: str
    flow_id: str
    status: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None

def store_run(run: WorkflowRun):
    memory_store = MemoryStore()
    try:
        memory_store.conn.zadd(REDIS_RUNS_KEY, {run.json(): run.start_time})
        memory_store.conn.zremrangebyrank(REDIS_RUNS_KEY, 0, -REDIS_MAX_RUNS)
    except Exception as e:
        print(f"Error storing run: {e}")

router = APIRouter()

flows = [
    {"id": "email", "name": "Email Agent"},
    {"id": "json", "name": "JSON Agent"},
    {"id": "pdf", "name": "PDF Agent"},
    {"id": "classifier", "name": "Classifier Agent"}
]

# ===== CHANGED: Removed /api from all paths =====
@router.get("/langflow/flows")
async def list_flows():
    return flows

logger = logging.getLogger(__name__)

@router.get("/langflow/runs")
async def list_runs():
    memory_store = MemoryStore()
    runs = memory_store.conn.zrevrange(REDIS_RUNS_KEY, 0, 50)
    if not runs:
        return []
    
    valid_runs = []
    for run in runs:
        try:
            run_str = run.decode("utf-8") if isinstance(run, bytes) else run
            run_dict = json.loads(run_str)
            
            if not run_dict.get("flow_id"):
                run_dict["flow_id"] = "unknown"
                
            valid_runs.append(WorkflowRun(**run_dict))
            
        except (json.JSONDecodeError, ValidationError) as e:
            logger.error(f"Invalid run format: {run_str}. Error: {str(e)}")
            continue
            
    return valid_runs

@router.post("/langflow/trigger")
async def trigger_flow(request: Request, background_tasks: BackgroundTasks):
    try:
        data = await request.json()
        
        workflow_id = data.get("workflowId")
        if not workflow_id:
            raise HTTPException(status_code=400, detail="workflowId is required")

        run_id = f"run_{workflow_id}_{uuid.uuid4()}"
        run = WorkflowRun(
            id=run_id,
            flow_id=workflow_id,
            status="started",
            start_time=datetime.now().timestamp(),
            end_time=None,
            duration=None
        )
        store_run(run)

        async def run_flow():
            await asyncio.sleep(2)
            run.status = "completed"
            run.end_time = datetime.now().timestamp()
            run.duration = run.end_time - run.start_time
            store_run(run)

        background_tasks.add_task(run_flow)
        return {"runId": run_id, "status": "started"}

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

@router.post("/langflow/webhook/{flow_id}")
async def webhook_trigger(
    flow_id: str,
    request: Request,
    background_tasks: BackgroundTasks
):
    try:
        data = await request.json()
        run_id = f"run_{flow_id}_{uuid.uuid4()}"
        run = WorkflowRun(
            id=run_id,
            flow_id=flow_id,
            status="started",
            start_time=datetime.now().timestamp(),
            end_time=None,
            duration=None
        )
        store_run(run)

        async def run_flow():
            await asyncio.sleep(2)
            run.status = "completed"
            run.end_time = datetime.now().timestamp()
            run.duration = run.end_time - run.start_time
            store_run(run)

        background_tasks.add_task(run_flow)
        return {"runId": run_id, "status": "started"}
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

@router.get("/langflow/runs/{run_id}/stream")
async def stream_logs(run_id: str):
    async def event_generator():
        for i in range(5):
            await asyncio.sleep(1)
            yield f"data: Log line {i+1} for {run_id}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/test")
async def test():
    return {"status": "ok"}

langflow_router = router
