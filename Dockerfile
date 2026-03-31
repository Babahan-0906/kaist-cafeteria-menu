FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Cloud Run expects application to listen on PORT environment variable
ENV PORT 8080
ENV HOST 0.0.0.0

# Using uvicorn to run the app
CMD ["python", "main.py"]
