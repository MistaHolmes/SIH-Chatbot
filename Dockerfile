# Dockerfile for Swaraj Desk RAG chatbot backend
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# install system deps needed by some pip packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# copy requirements and install
COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# copy application
COPY . /app

# ensure chroma_store exists (optional persistent store)
RUN mkdir -p /app/chroma_store || true

# expose port used by uvicorn
EXPOSE 8000

# lightweight healthcheck for docker
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://127.0.0.1:8000/health || exit 1

# run the app via uvicorn (no reload in production)
CMD ["python","-m","uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
