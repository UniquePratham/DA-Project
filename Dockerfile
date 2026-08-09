FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /app

# Install system dependencies for Playwright Chromium, Node, and utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    build-essential \
    libpq-dev \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libxss1 \
    libgtk-3-0 \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install global Lighthouse and axe-core CLI tools
RUN npm install -g lighthouse @axe-core/cli

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright Chromium browser
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy codebase
COPY . .

# Ensure data directories exist
RUN python -c "from configs.settings import settings; settings.ensure_dirs()"

CMD ["python", "scripts/run_pilot.py"]
