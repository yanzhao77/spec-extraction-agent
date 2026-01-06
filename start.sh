#!/bin/bash

# Start the FastAPI server (primary service)
echo "Starting FastAPI server on port 8000..."
uvicorn src.api_server:app --host 0.0.0.0 --port 8000 &

# Check if the Gradio UI should be run
if [ "$RUN_GRADIO_UI" = "true" ]; then
  echo "Starting optional Gradio UI on port 7860..."
  python src/gradio_app.py
else
  echo "Gradio UI is disabled. API server is running."
  # Keep the container alive
  wait
fi
