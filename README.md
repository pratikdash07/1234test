# Flowbit Multi-Agent Document Processing System

## Overview

Flowbit is an AI-powered, multi-format document processing system that classifies, extracts, and routes business documents such as Emails, JSON files, and PDFs. It features a modular multi-agent architecture, LLM-enhanced intelligence, automated action routing, and full auditability.

## Features

- Multi-format document classification (Email, JSON, PDF)
- Business intent detection (RFQ, Complaint, Invoice, Regulation, Fraud Risk)
- Specialized agents for Email, JSON, and PDF
- Automated action routing with retry logic
- Shared memory store for audit and traceability
- Modern React-based frontend for file upload and result display
- Dockerized backend and frontend for deployment

## Tech Stack

- **Backend:** Python, FastAPI, LangChain, Redis
- **Frontend:** React, Vite (custom UI)
- **Containerization:** Docker

## Project Structure
multi-agent-system/
├── agents/
├── core/
├── frontend/
│ ├── public/
│ ├── src/
│ ├── package.json
├── main.py
├── requirements.txt
├── .env
└── README.md

## Frontend

The frontend is a React application that provides a clean, modern UI for uploading documents and displaying detailed processing results, including classification, urgency, tone, and action routing outcomes.

- Tab title and favicon are customized for project branding.
- Displays all results returned by the backend: classification, processing results, agent processing, action router responses, and full trace logs.

### Running the Frontend

1. Navigate to the `frontend/` directory.
2. Install dependencies: `npm install`
3. Start the development server: `npm run dev`
4. Access the UI at [http://localhost:5173/demo](http://localhost:5173/demo)

## Backend

The backend is a FastAPI server that runs the multi-agent pipeline.

### Running the Backend

1. Create and activate a Python virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables in `.env`.
4. Start the backend: `uvicorn main:app --reload`

## Usage

- Upload documents via the frontend.
- The backend processes each document through classification, agent extraction, and action routing.
- Results are displayed in the frontend UI.

## Dockerization

The project supports Docker for simplified deployment of both backend and frontend.

## Architecture Diagram


flowchart TD
    A[User Uploads Document<br/>(Email, JSON, PDF)] --> B{Classifier Agent}
    B -->|Email| C[Email Agent<br/>Extracts sender, urgency, tone, issue]
    B -->|JSON| D[JSON Agent<br/>Schema validation, anomaly detection]
    B -->|PDF| E[PDF Agent<br/>Extracts invoice/policy data, flags]
    C --> F{Action Router}
    D --> F
    E --> F
    F -->|Escalate| G[POST /crm/escalate]
    F -->|Alert| H[POST /risk_alert]
    F -->|Flag| I[POST /compliance/flag]
    F -->|Accept| J[POST /compliance/accept]
    F --> K[Log in Memory Store<br/>(Redis)]
    K --> L[Frontend UI<br/>Shows Results & Trace]


## Sample Screenshots

![UI Screenshot](./docs/ui_screenshot.png)

## License

MIT

## Author

Pratik Dash
