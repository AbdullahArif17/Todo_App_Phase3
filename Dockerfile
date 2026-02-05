FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY apps/backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY apps/backend/src/ ./src/
COPY apps/backend/main.py ./main.py
COPY apps/backend/startup.py ./startup.py
COPY apps/backend/requirements.txt ./requirements.txt
COPY .env.example .env

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=7860
ENV ENVIRONMENT=production
ENV DEBUG=false

# Expose port
EXPOSE 7860

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app

# Clean up Python cache files
RUN find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
RUN find . -type f -name "*.pyc" -delete 2>/dev/null || true
RUN find . -type f -name "*.pyo" -delete 2>/dev/null || true

# Switch to non-root user
USER appuser

# Run the application
CMD ["python", "startup.py"]