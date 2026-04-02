FROM python:3.11-slim

# install system dependencies (curl is needed for scraper)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy application files
COPY . .

# cloud run configuration
ENV PORT=8080
ENV HOST=0.0.0.0

# run application
CMD ["python", "main.py"]
