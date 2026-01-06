
import os
import uuid
import logging
import json
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Optional, Dict, Any

from .agent import ExtractionAgentFinal
from .billing_decision import decide_billing, REASON_AGENT_FAILURE

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- API Key Security ---
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Depends(api_key_header)):
    expected_api_key = os.getenv("AGENT_API_KEY")
    if not expected_api_key:
        return None
    if api_key != expected_api_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Engineering Specification Extraction Agent API",
    description="A task-oriented Agent API for high-reliability structured data extraction.",
    version="2.6.0",
    docs_url="/docs",
    redoc_url=None
)

# --- Request & Response Models ---
class ExtractionRequest(BaseModel):
    document_path: str
    user_id: Optional[str] = "default_user"
    # Optional LLM override
    llm_base_url: Optional[str] = None
    llm_model_name: Optional[str] = None
    llm_api_key: Optional[str] = None

class BillingInfo(BaseModel):
    billable: bool
    reason: str
    unit: str

class ExtractionResponse(BaseModel):
    task_id: str
    user_id: str
    document_path: str
    status: str
    billing: BillingInfo
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

# --- API Endpoint ---
@app.post("/v1/extract", 
            response_model=ExtractionResponse, 
            summary="Run a Billable Extraction Task",
            tags=["Agent API"])
async def extract_from_document(request: ExtractionRequest, api_key: Optional[str] = Depends(get_api_key)):
    task_id = f"task_{uuid.uuid4()}"
    
    if not os.path.exists(request.document_path) or os.path.getsize(request.document_path) == 0:
        return ExtractionResponse(
            task_id=task_id, user_id=request.user_id, document_path=request.document_path,
            status="failed",
            billing=decide_billing({"status": "EMPTY_OR_INVALID_DOCUMENT"}),
            error_message="Document not found or is empty."
        )

    try:
        logging.info(f"Starting Agent task {task_id} for user {request.user_id}")
        
        # --- Initialize Agent with dynamic LLM config ---
        agent = ExtractionAgentFinal(
            document_path=request.document_path,
            llm_base_url=request.llm_base_url,
            llm_model_name=request.llm_model_name,
            llm_api_key=request.llm_api_key
        )
        
        final_json_output = agent.run()
        
        if not final_json_output:
            raise ValueError("Agent execution failed to produce output.")

        agent_result = json.loads(final_json_output)
        
        billing_info = decide_billing({
            "status": agent_result.get("status", "completed"),
            "validated_count": len(agent_result.get("validated_items", [])),
        })

        if billing_info["billable"]:
            logging.info(f"BILLABLE_EVENT: Task {task_id} for user {request.user_id}. Reason: {billing_info['reason']}")

        return ExtractionResponse(
            task_id=task_id,
            user_id=request.user_id,
            document_path=request.document_path,
            status="completed",
            billing=billing_info,
            result=agent_result
        )

    except Exception as e:
        logging.error(f"Agent task {task_id} failed for user {request.user_id}. Error: {e}")
        return ExtractionResponse(
            task_id=task_id,
            user_id=request.user_id,
            document_path=request.document_path,
            status="failed",
            billing=decide_billing({"status": "AGENT_EXECUTION_FAILURE"}),
            error_message=str(e)
        )

@app.get("/health", summary="Health Check", tags=["Management"])
async def health_check():
    return {"status": "ok"}
