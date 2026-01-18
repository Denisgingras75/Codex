# Root Dockerfile - builds from denis_os subfolder
FROM python:3.9-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8501

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install from denis_os
COPY denis_os/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY denis_os/ .

EXPOSE $PORT

CMD streamlit run main.py --server.port=$PORT --server.address=0.0.0.0
