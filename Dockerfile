'''
# Dockerfile for the Engineering Specification Extraction Agent

# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application'''s code into the container at /app
COPY . .

# Expose ports for the API server and the Gradio UI
EXPOSE 8000
EXPOSE 7860

# Define environment variable for the API key (to be passed at runtime)
ENV OPENAI_API_KEY=""

# Command to run the application
# This will start the FastAPI server in the background and the Gradio app in the foreground
CMD ["./start.sh"]
