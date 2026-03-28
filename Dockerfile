FROM python:3.11-slim

# Install system dependencies required for psycopg2 and others
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Add /app to PYTHONPATH so modules can be imported across boundaries
ENV PYTHONPATH="/app"

CMD ["sh", "-c", "pytest && tail -f /dev/null"]
