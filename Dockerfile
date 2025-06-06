# Use the official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    ffmpeg \
    libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create and switch to a non-root user
RUN useradd -m -r user && chown -R user /app
USER user

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set Python to unbuffered mode for better logging
ENV PYTHONUNBUFFERED=1

# Cloud Run will set PORT environment variable
ENV PORT=8080

# Command to run the application
CMD ["python", "main.py"]
