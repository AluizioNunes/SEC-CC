FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY Backend/FastAPI/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (FastAPI)
COPY Backend/FastAPI/app ./app
# Copy tests and pytest configuration for container runs
COPY Backend/FastAPI/tests ./tests
COPY Backend/FastAPI/pytest.ini ./pytest.ini

# Copy Backend modules needed by FastAPI (AI and Redis)
COPY Backend/__init__.py ./Backend/__init__.py
COPY Backend/AI ./Backend/AI
COPY Backend/Redis ./Backend/Redis

EXPOSE 8000

# Ajusta uvicorn para 2 workers e keep-alive maior para melhor throughput com bcrypt
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--timeout-keep-alive", "75"]
