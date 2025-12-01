# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire project first
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install the quantum_simulator package (editable)
RUN pip install -e ./quantum_simulator

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "backend/start.py"]
