# Use official Python image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install torch torchvision --extra-index-url https://download.pytorch.org/whl/cpu

# Install YOLOv8
RUN pip install ultralytics

# Copy the entire project
COPY . .

# Create data directories
RUN mkdir -p /app/data/raw && \
    mkdir -p /app/data/images && \
    mkdir -p /app/data/processed

# Expose FastAPI port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]