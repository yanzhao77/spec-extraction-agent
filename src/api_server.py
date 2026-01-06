
import os
import uuid
import logging
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Optional

from .agent import ExtractionAgentFinal

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- API Key Security ---
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_api_key(api_key: str = Depends(api_key_header)):
    expected_api_key = os.getenv("AGENT_API_KEY")
    if not expected_api_key:
        raise HTTPException(
            status_code=500,
            detail="AGENT_API_KEY not configured on the server."
        )
    if api_key != expected_api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )
    return api_key

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Engineering Specification Extraction Agent API",
    description="A task-oriented Agent API for high-reliability structured data extraction.",
    version="2.4.0",
    docs_url="/docs",
    redoc_url=None
)

# --- Request & Response Models ---
class ExtractionRequest(BaseModel):
    document_path: str
    user_id: Optional[str] = "default_user"

class ExtractionResponse(BaseModel):
    task_id: str
    user_id: str
    document_path: str
    status: str
    result: dict

# --- API Endpoint ---
@app.post("/v1/extract", 
            response_model=ExtractionResponse, 
            summary="Run a Billable Extraction Task",
            tags=["Agent API"])
async def extract_from_document(request: ExtractionRequest, api_key: str = Depends(get_api_key)):
    """
    Run a single, billable Agent execution on a document.

    This is the primary product endpoint. Each successful call constitutes one billable event.
    """
    task_id = f"task_{uuid.uuid4()}"
    
    # Check for LLM API key
    if not os.getenv('OPENAI_API_KEY'):
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY environment variable not set on the server."
        )

    # Check if the document exists
    if not os.path.exists(request.document_path):
        raise HTTPException(
            status_code=400,
            detail=f"Document not found at path: {request.document_path}"
        )

    try:
        # --- Run the Agent ---
        logging.info(f"Starting Agent task {task_id} for user {request.user_id}")
        agent = ExtractionAgentFinal(document_path=request.document_path)
        final_json_output = agent.run()
        
        if not final_json_output:
            raise HTTPException(status_code=500, detail="Agent execution failed to produce output.")

        # --- Log Billable Event ---
        # This is where you would integrate with a real billing system.
        logging.info(f"BILLABLE_EVENT: Task {task_id} successful for user {request.user_id}")

        # --- Format the Response ---
        response_data = {
            "task_id": task_id,
            "user_id": request.user_id,
            "document_path": request.document_path,
            "status": "completed",
            "result": json.loads(final_json_output)
        }
        
        return response_data

    except Exception as e:
        logging.error(f"Agent task {task_id} failed for user {request.user_id}. Error: {e}")
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")

@app.get("/health", summary="Health Check", tags=["Management"])
async def health_check():
    return {"status": "ok"}

import json
