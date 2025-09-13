# Start from official Python image
FROM python:3.11-slim

# Install system dependencies for git and building
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency list and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port App Runner expects
EXPOSE 8080

# Run FastAPI app with Uvicorn
CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8080"]
