FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY pyproject.toml .
RUN pip install .

# Copy application code
COPY . .

# Expose port for FastAPI
EXPOSE 8000

# Start command (can be overridden to run the telegram bot instead)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
