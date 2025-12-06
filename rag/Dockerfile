FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for confluent-kafka (requires librdkafka)
# and OpenGL libraries for docling (requires libGL.so.1)
RUN apt-get update && apt-get install -y --no-install-recommends \
    librdkafka-dev \
    libgl1 \
    libglib2.0-0 \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker layer caching for dependencies
COPY requirements.txt /app/requirements.txt

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code into the container
COPY . /app

# Set default command to run the worker
CMD ["python", "worker.py"]