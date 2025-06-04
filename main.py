from fastapi import FastAPI, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from agents.classifier_agent.classifier import ClassifierAgent
from agents.email_agent.email_agent import EmailAgent
from agents.json_agent.json_agent import JSONAgent
from agents.pdf_agent.pdf_agent import PDFAgent
from core.routers.action_router import ActionRouter
from core.memory.redis_client import MemoryStore
import os

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

#multi agent pipeline
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

    # Read content
    if ext == ".pdf":
        #PDF temporarily saved for PyPDF2
        temp_path = f"temp_{filename}"
        with open(temp_path, "wb") as f_out:
            f_out.write(await file.read())
        content = None  # Not needed PDF
    else:
        content = (await file.read()).decode("utf-8")
        temp_path = None


    classification = classifier.classify(filename, content if content else "")

    # correct agent routing
    if classification["format"] == "Email":
        result = email_agent.process(filename, content, classification)
        action = result["action"]
    elif classification["format"] == "JSON":
        result = json_agent.process(filename, content, classification)
        action = "alert" if not result["valid"] else "accept"
    elif classification["format"] == "PDF":
        result = pdf_agent.process(temp_path, classification)
        action = result.get("flag", "accepted")
        #Clean up temporary file
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
    else:
        return {"error": "Unsupported format"}

    #Trigger action by ActionRouter
    payload = {
        "source_id": source_id,
        "result": result
    }
    action_result = action_router.route_action(action if action in action_router.endpoints else "routine", payload)

    trace = memory_store.get_full_trace(source_id)

    return {
        "classification": classification,
        "processing_result": result,
        "action_router_result": action_result,
        "full_trace": trace
    }
