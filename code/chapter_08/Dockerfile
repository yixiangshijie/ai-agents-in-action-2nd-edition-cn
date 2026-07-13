# Use an official lightweight Python image
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Install system deps that are commonly required (adjust if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements if present and install; otherwise install minimal runtime deps
COPY requirements.txt /app/requirements.txt
RUN if [ -f /app/requirements.txt ]; then \
    pip install --no-cache-dir -r /app/requirements.txt; \
    else \
    pip install --no-cache-dir "uvicorn[standard]" fastapi; \
    fi

# Copy project files
COPY . /app

# Expose port and run uvicorn. The app module is 02_app:app
EXPOSE ${PORT}
CMD ["sh", "-c", "uvicorn 02_app:app --host 0.0.0.0 --port ${PORT}"]