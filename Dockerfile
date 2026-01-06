
# Dockerfile for the Engineering Specification Extraction Agent API

FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose ports for the API server and the optional Gradio UI
EXPOSE 8000
EXPOSE 7860

# Environment variables to be passed at runtime
ENV OPENAI_API_KEY=""
ENV AGENT_API_KEY=""
ENV RUN_GRADIO_UI="false"

# Make the startup script executable
RUN chmod +x start.sh

# Command to run the application
CMD ["./start.sh"]
