FROM python:3.14.2-slim

WORKDIR /app

# Install dependencies
COPY requirements*.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy application code
COPY . .

# Expose port for local development
EXPOSE 8000

# Run with uvicorn for local development
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
