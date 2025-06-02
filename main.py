"""from fastapi import Request
from fastapi import FastAPI, UploadFile
from agents.classifier_agent.classifier import ClassifierAgent
from agents.email_agent.email_agent import EmailAgent
from agents.json_agent.json_agent import JSONAgent
from agents.pdf_agent.pdf_agent import PDFAgent
import os

app = FastAPI()
classifier = ClassifierAgent()
email_agent = EmailAgent()
json_agent = JSONAgent()
pdf_agent = PDFAgent()


@app.post("/process-file")
async def process_file(file: UploadFile):
    # Read file content
    content = (await file.read()).decode("utf-8")
    
    # Classify
    classification = classifier.classify(file.filename, content)
    
    # Route processing
    if classification["format"] == "Email":
        result = email_agent.process(file.filename, content, classification)
    elif classification["format"] == "JSON":
        result = json_agent.process(file.filename, content, classification)
    elif classification["format"] == "PDF":
        result = pdf_agent.process(file.filename, classification)
    else:
        return {"error": "Unsupported format"}
    
    return {
        "classification": classification,
        "processing_result": result
    }
    
@app.post("/crm/escalate")
async def escalate(request: Request):
    data = await request.json()
    return {"message": "Escalation received", "data": data}

@app.post("/crm/log")
async def log(request: Request):
    data = await request.json()
    return {"message": "Logged", "data": data}

@app.post("/risk_alert")
async def risk_alert(request: Request):
    data = await request.json()
    return {"message": "Risk alert received", "data": data}

@app.post("/compliance/flag")
async def compliance_flag(request: Request):
    data = await request.json()
    return {"message": "Compliance flag received", "data": data}

@app.post("/compliance/accept")
async def compliance_accept(request: Request):
    data = await request.json()
    return {"message": "Compliance accept received", "data": data}
"""

from fastapi import FastAPI, UploadFile, Request
from agents.classifier_agent.classifier import ClassifierAgent
from agents.email_agent.email_agent import EmailAgent
from agents.json_agent.json_agent import JSONAgent
from agents.pdf_agent.pdf_agent import PDFAgent
from core.routers.action_router import ActionRouter
from core.memory.redis_client import MemoryStore
import os

app = FastAPI()

# Dummy endpoints for ActionRouter simulation
@app.post("/crm/escalate")
async def escalate(request: Request):
    data = await request.json()
    return {"message": "Escalation received", "data": data}

@app.post("/crm/log")
async def log(request: Request):
    data = await request.json()
    return {"message": "Logged", "data": data}

@app.post("/risk_alert")
async def risk_alert(request: Request):
    data = await request.json()
    return {"message": "Risk alert received", "data": data}

@app.post("/compliance/flag")
async def compliance_flag(request: Request):
    data = await request.json()
    return {"message": "Compliance flag received", "data": data}

@app.post("/compliance/accept")
async def compliance_accept(request: Request):
    data = await request.json()
    return {"message": "Compliance accept received", "data": data}

# Multi-agent pipeline
classifier = ClassifierAgent()
email_agent = EmailAgent()
json_agent = JSONAgent()
pdf_agent = PDFAgent()
action_router = ActionRouter()
memory_store = MemoryStore()

@app.post("/process-file")
async def process_file(file: UploadFile):
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    source_id = os.path.splitext(filename)[0]

    # Read file content
    if ext == ".pdf":
        # Save PDF temporarily for PyPDF2
        temp_path = f"temp_{filename}"
        with open(temp_path, "wb") as f_out:
            f_out.write(await file.read())
        content = None  # Not used for PDF
    else:
        content = (await file.read()).decode("utf-8")
        temp_path = None

    # Classify
    classification = classifier.classify(filename, content if content else "")

    # Route to the correct agent
    if classification["format"] == "Email":
        result = email_agent.process(filename, content, classification)
        action = result["action"]
    elif classification["format"] == "JSON":
        result = json_agent.process(filename, content, classification)
        action = "alert" if not result["valid"] else "accept"
    elif classification["format"] == "PDF":
        result = pdf_agent.process(temp_path, classification)
        action = result.get("flag", "accepted")
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
    else:
        return {"error": "Unsupported format"}

    # Trigger action via ActionRouter
    payload = {
        "source_id": source_id,
        "result": result
    }
    action_result = action_router.route_action(action if action in action_router.endpoints else "routine", payload)

    # Get full trace from Redis
    trace = memory_store.get_full_trace(source_id)

    return {
        "classification": classification,
        "processing_result": result,
        "action_router_result": action_result,
        "full_trace": trace
    }
