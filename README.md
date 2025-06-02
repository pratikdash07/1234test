# Flowbit Multi-Agent Document Processing System

## Overview

A modular, multi-agent backend system that classifies, extracts, and routes business documents (Email, JSON, PDF), triggers automated actions, and logs all steps for auditability. Built with Python, FastAPI, Redis, and Google Gemini LLM.

---

## Features

- **Classifier Agent:** Detects document format and business intent (LLM-powered, with fallback).
- **Email Agent:** Extracts sender, urgency, tone, and triggers escalation or logs.
- **JSON Agent:** Validates schema, flags anomalies.
- **PDF Agent:** Extracts text, flags high invoice totals or compliance mentions.
- **Action Router:** Triggers simulated REST actions with retry logic.
- **Shared Memory:** All steps and decisions logged in Redis.
- **LLM Integration:** Uses Google Gemini for intent detection, with fallback logic.
- **Robust to large/bulky inputs.**

---

## Setup

1. **Clone the repo & create a virtual environment:**
    ```
    git clone https://github.com/yourusername/flowbit_multi_agent.git
    cd flowbit_multi_agent
    python -m venv venv
    venv\Scripts\activate  # On Windows
    ```

2. **Install dependencies:**
    ```
    pip install -r requirements.txt
    ```

3. **Configure environment:**
    - Create a `.env` file in the root:
      ```
      GOOGLE_API_KEY=your-google-api-key-here
      ```

4. **Start Redis server:**
    - On Windows: Run `redis-server.exe` in a terminal.

5. **Start FastAPI servers:**
    - Main app:
      ```
      uvicorn main:app --reload
      ```
    - Dummy endpoints (in a new terminal):
      ```
      uvicorn main:app --port 8001
      ```

6. **Test with sample files:**
    ```
    curl -X POST -F "file=@samples/emails/complaint_escalate.eml" http://localhost:8000/process-file
    ```

---

## Folder Structure

.
├── agents/
│ ├── classifier_agent/
│ ├── email_agent/
│ ├── json_agent/
│ └── pdf_agent/
├── core/
│ ├── memory/
│ └── routers/
├── samples/
│ ├── emails/
│ ├── jsons/
│ └── pdfs/
├── tests/
├── main.py
├── requirements.txt
├── .env
└── README.md

---

## Example Output

{
"classification": {"format": "Email", "intent": "Complaint"},
"processing_result": {...},
"action_router_result": {"status": "success", ...},
"full_trace": {...}
}

---

## Testing

Run all unit tests:
python -m unittest discover


---

## Docker & UI

- Dockerization and UI integration instructions will be added in the next commit.

---

## Author

- Pratik Dash

---

## License

MIT
