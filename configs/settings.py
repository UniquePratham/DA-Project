"""Configuration management for BharatGov Access Observatory."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Core Environment
    environment: str = Field(default="development")
    log_level: str = Field(default="INFO")
    data_dir: Path = Field(default=Path("./data"))

    # Hardware & Concurrency (Tuned for Vultr 24 vCPU / 96 GB RAM)
    cpu_workers: int = Field(default=16)
    max_concurrent_browsers: int = Field(default=8)
    domain_concurrency: int = Field(default=1)  # Strictly 1 per domain per Section 15
    requests_per_second_per_domain: float = Field(default=1.0)  # Max 1 req/sec per domain

    # Database
    postgres_user: str = Field(default="bharatgov")
    postgres_password: str = Field(default="bharatgov_password")
    postgres_db: str = Field(default="bharatgov_access")
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    database_url: Optional[str] = Field(
        default="postgresql+asyncpg://bharatgov:bharatgov_password@localhost:5432/bharatgov_access"
    )

    # Redis
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_url: str = Field(default="redis://localhost:6379/0")

    # Local AI / Ollama
    ollama_base_url: str = Field(default="http://localhost:11434")
    agent_model: str = Field(default="qwen3:4b")
    agent_fallback_model: str = Field(default="qwen3:8b")

    # Storage & Evidence
    minio_root_user: str = Field(default="minioadmin")
    minio_root_password: str = Field(default="minioadmin")
    minio_endpoint: str = Field(default="localhost:9000")
    minio_bucket: str = Field(default="bharatgov-evidence")

    # Safety Governor Limits
    max_pages_per_domain_per_cycle: int = Field(default=10)
    max_extra_pages_per_domain: int = Field(default=5)
    max_agent_steps_per_domain: int = Field(default=20)
    max_agent_runtime_seconds: int = Field(default=300)
    crawl_timeout_seconds: int = Field(default=30)
    max_retries: int = Field(default=2)
    cooldown_on_429_seconds: int = Field(default=60)
    cooldown_on_5xx_seconds: int = Field(default=30)
    user_agent: str = Field(
        default="BharatGovAccessObservatory/1.0 (+https://datahub.kgp/bharatgov-access; research-bot@bharatgov.in)"
    )

    # Storage Subdirectories
    @property
    def raw_evidence_dir(self) -> Path:
        return self.data_dir / "raw"

    @property
    def processed_dir(self) -> Path:
        return self.data_dir / "processed"

    @property
    def releases_dir(self) -> Path:
        return self.data_dir / "releases"

    @property
    def quarantine_dir(self) -> Path:
        return self.data_dir / "quarantine"

    def ensure_dirs(self) -> None:
        """Create necessary data storage directories."""
        self.raw_evidence_dir.mkdir(parents=True, exist_ok=True)
        (self.raw_evidence_dir / "html").mkdir(parents=True, exist_ok=True)
        (self.raw_evidence_dir / "screenshots").mkdir(parents=True, exist_ok=True)
        (self.raw_evidence_dir / "axe").mkdir(parents=True, exist_ok=True)
        (self.raw_evidence_dir / "lighthouse").mkdir(parents=True, exist_ok=True)
        (self.raw_evidence_dir / "headers").mkdir(parents=True, exist_ok=True)
        (self.raw_evidence_dir / "metadata").mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.releases_dir.mkdir(parents=True, exist_ok=True)
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
