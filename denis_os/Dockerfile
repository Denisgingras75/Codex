# Use a lightweight Python 3.9 image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Prevent Python from generating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (needed for some math/plot libraries)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Default port (Railway will override with $PORT)
ENV PORT=8501
EXPOSE $PORT

# Command to run the app (uses shell form to expand $PORT)
CMD streamlit run main.py --server.port=$PORT --server.address=0.0.0.0
