#!/usr/bin/env bash
set -euo pipefail

echo "========================================================="
echo " BharatGov Access - VM Infrastructure Initialization"
echo " Target VM: 24 vCPU / 96 GB RAM / 1600 GB NVMe"
echo "========================================================="

# 1. Ensure docker compose is available
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed. Please install Docker first."
    exit 1
fi

# 2. Setup .env from .env.example if missing
if [ ! -f .env ]; then
    echo "[*] Creating .env from .env.example..."
    cp .env.example .env
fi

# 3. Create required data directories
echo "[*] Initializing data directory structure..."
mkdir -p data/raw/{html,screenshots,axe,lighthouse,headers,metadata}
mkdir -p data/{processed,releases,quarantine,logs}

# 4. Start Infrastructure Containers
echo "[*] Launching PostgreSQL, Redis, MinIO, and Ollama services..."
docker compose up -d postgres redis minio ollama

# 5. Wait for Ollama to become healthy
echo "[*] Waiting for Ollama container..."
until docker compose exec ollama ollama list &> /dev/null; do
    sleep 2
done

# 6. Pull open-weight model Qwen3 4B & fallback Qwen3 8B
echo "[*] Pulling Qwen3 4B model into Ollama..."
docker compose exec ollama ollama pull qwen3:4b || docker compose exec ollama ollama pull qwen2.5:3b

echo "[*] Infrastructure initialization complete!"
echo "========================================================="
