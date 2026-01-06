#!/bin/bash

# Start the FastAPI server in the background
echo "Starting FastAPI server..."
uvicorn src.api_server:app --host 0.0.0.0 --port 8000 &

# Start the Gradio UI in the foreground
echo "Starting Gradio UI..."
python src/gradio_app.py
