'''
FastAPI server to expose the Engineering Specification Extraction Agent as a RESTful API.

This server provides an endpoint to upload a document and receive the extracted
structured data in JSON format. It is designed to be used for programmatic
integration and as the backend for the Gradio UI.
'''

import os
import uuid
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from .agent import ExtractionAgentFinal

# Initialize FastAPI app
app = FastAPI(
    title="Engineering Specification Extraction Agent",
    description="An agent for structured data extraction from engineering documents.",
    version="2.3.0",
)

class ExtractionResponse(BaseModel):
    task_id: str
    filename: str
    content: dict

class ErrorResponse(BaseModel):
    error: str

@app.post("/v1/extract", 
            response_model=ExtractionResponse, 
            summary="Extract Constraints from a Document",
            tags=["Extraction"])
async def extract_from_document(file: UploadFile = File(..., description="The engineering specification document to process."),
                                schema: Optional[str] = Form(None, description="Custom JSON schema for extraction (Not yet implemented).")):
    '''
    Accepts a document file, processes it with the ExtractionAgent, and returns the 
    structured JSON output.
    '''
    # Ensure API key is set
    if not os.getenv('OPENAI_API_KEY'):
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY environment variable not set on the server."
        )

    # Create a temporary directory to store the uploaded file
    temp_dir = f"/tmp/{uuid.uuid4()}"
    os.makedirs(temp_dir)
    temp_file_path = os.path.join(temp_dir, file.filename)

    try:
        # Save the uploaded file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # --- Run the Agent ---
        agent = ExtractionAgentFinal(document_path=temp_file_path)
        final_json_output = agent.run()
        
        if not final_json_output:
            raise HTTPException(status_code=500, detail="Agent execution failed to produce output.")

        # --- Format the Response ---
        response_data = {
            "task_id": str(uuid.uuid4()),
            "filename": file.filename,
            "content": json.loads(final_json_output)
        }
        
        return JSONResponse(content=response_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    finally:
        # Clean up the temporary directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

@app.get("/health", summary="Health Check", tags=["Management"])
async def health_check():
    '''
    Simple health check endpoint.
    '''
    return {"status": "ok"}

# To run this server:
# uvicorn src.api_server:app --reload
import json
