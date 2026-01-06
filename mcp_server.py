"""
ModelScope MCP Server Entry Point
"""

import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
import asyncio
import json

from src.agent import ExtractionAgentFinal
from src.billing_decision import decide_billing

app = FastAPI()

# --- Authentication ---
AGENT_API_KEY = os.environ.get("AGENT_API_KEY", "your_agent_api_key")

@app.middleware("http")
async def authenticate_request(request: Request, call_next):
    if request.url.path == "/health":
        return await call_next(request)
    
    api_key = request.headers.get("X-API-Key")
    if api_key != AGENT_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    
    response = await call_next(request)
    return response

# --- SSE Stream --- 
async def event_stream(request: Request):
    body = await request.json()
    document_path = body.get("document_path")
    user_id = body.get("user_id", "default_user")
    llm_base_url = body.get("llm_base_url")
    llm_model_name = body.get("llm_model_name")
    llm_api_key = body.get("llm_api_key")

    agent = ExtractionAgentFinal(
        document_path=document_path,
        llm_base_url=llm_base_url,
        llm_model_name=llm_model_name,
        llm_api_key=llm_api_key
    )

    async def stream_events():
        try:
            async for event in agent.run_in_stream():
                yield f"event: {event['event']}\ndata: {json.dumps(event['data'])}\n\n"
                await asyncio.sleep(0.1)
        except Exception as e:
            error_event = {
                "event": "error",
                "data": {"error": str(e)}
            }
            yield f"event: {error_event['event']}\ndata: {json.dumps(error_event['data'])}\n\n"

    return StreamingResponse(stream_events(), media_type="text/event-stream")

# --- API Endpoints ---
@app.post("/v1/extract")
async def extract(request: Request):
    return await event_stream(request)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
