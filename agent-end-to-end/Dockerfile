# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir flask langchain openai

# Expose the Flask port
EXPOSE 8080

# Command to run the app
CMD ["python", "agent_app.py"]