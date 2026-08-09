# BharatGov Access — Production VM Deployment & Setup Guide

This guide provides step-by-step instructions for deploying and running **BharatGov Access** on your **Vultr VM (24 vCPU / 96 GB RAM / 1600 GB Storage)**.

---

## 1. SSH into the Vultr Server

Open your local terminal (PowerShell, Command Prompt, or Bash) and connect to your VM:

```bash
ssh root@<YOUR_VM_IP>
```

---

## 2. Server Package & Docker Installation

Run the following commands on the VM to ensure system updates, Git, Docker, and Docker Compose are installed:

```bash
# Update system repositories
apt-get update && apt-get upgrade -y

# Install essential build tools, Git, and Python
apt-get install -y git curl wget build-essential python3 python3-pip python3-venv

# Install Docker & Docker Compose Plugin
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
apt-get install -y docker-compose-plugin
```

Verify installations:
```bash
docker --version
docker compose version
```

---

## 3. Clone Repository

Clone the project from GitHub into `/opt/bharatgov-access`:

```bash
git clone https://github.com/UniquePratham/DA-Project.git /opt/bharatgov-access
cd /opt/bharatgov-access
```

---

## 4. Initialize Infrastructure (PostgreSQL, Redis, MinIO, Ollama)

Run the automated infrastructure initialization script:

```bash
chmod +x scripts/init_infra.sh
./scripts/init_infra.sh
```

### What this does automatically:
1. Generates `.env` with optimized configuration for 24 vCPUs and 96 GB RAM.
2. Creates data storage directories (`data/raw/`, `data/releases/`, etc.).
3. Starts PostgreSQL 16, Redis 7, MinIO S3, and Ollama containers in detached mode.
4. Downloads the `qwen3:4b` local AI model into the Ollama container.

Verify running containers:
```bash
docker compose ps
```

---

## 5. Python Environment & Dependency Setup

Set up a Python virtual environment on the host for running collector workers and pipelines:

```bash
# Create and activate virtualenv
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright Chromium browser binary
playwright install chromium
playwright install-deps chromium
```

---

## 6. Run Test Suite Verification

Verify that all modules, Safety Governor, auditors, and validator engines pass:

```bash
pytest tests/ -v
```
*(All 28 tests should pass).*

---

## 7. Running the Observatory Pipelines

### A. Run 10-Site Pilot Run
```bash
python scripts/run_pilot.py
```

### B. Run Full Observatory Collection (Batch Mode)
To inspect 100 domains live and generate versioned Parquet dataset releases:

```bash
python scripts/run_pipeline.py --live --limit 100 --version 0.1.0
```

### C. Run Continuous Long-Running Background Collection
To keep the collection running continuously in the background using `tmux` or `nohup`:

```bash
# Using nohup:
nohup python scripts/run_pipeline.py --live --limit 1000 --version 1.0.0 > crawl.log 2>&1 &

# Check live progress:
tail -f crawl.log
```

---

## 8. Accessing Generated Datasets & Releases

All exported datasets are saved to `data/releases/`:

- **Columnar Dataset (Parquet)**: `data/releases/bharatgov_access_v0.1.0.parquet`
- **JSONL Stream**: `data/releases/bharatgov_access_v0.1.0.jsonl`
- **Coverage Audit**: `data/releases/coverage_audit_0.1.0.json`
- **DataHub Manifest**: `data/releases/manifest_0.1.0.json`

To copy datasets from your VM to your local computer:
```bash
# Run this from your local machine:
scp root@<YOUR_VM_IP>:/opt/bharatgov-access/data/releases/* ./downloads/
```

---

## 9. Useful Management Commands

| Task | Command |
|---|---|
| View container logs | `docker compose logs -f` |
| View Ollama models | `docker compose exec ollama ollama list` |
| Monitor VM resources | `htop` |
| Stop infrastructure | `docker compose down` |
| Restart infrastructure | `docker compose up -d` |
