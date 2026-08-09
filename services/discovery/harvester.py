"""Domain Harvester, Link Extractor, and DNS Normalizer for BharatGov Access."""

from __future__ import annotations

import socket
import re
from typing import List, Dict, Any, Set, Optional
from urllib.parse import urlparse, urljoin
import lxml.html

from schemas.domain import GovernmentEntityRecord, GovernmentLevel, DomainStatus
from services.discovery.seed_sources import DomainSeedGenerator


class DomainHarvester:
    """Discovers, normalizes, deduplicates, and validates candidate Indian government domains."""

    GOV_TLD_PATTERNS = [
        re.compile(r"\.gov\.in$", re.I),
        re.compile(r"\.nic\.in$", re.I),
        re.compile(r"\.ac\.in$", re.I),
        re.compile(r"\.res\.in$", re.I),
        re.compile(r"\.edu\.in$", re.I),
    ]

    @classmethod
    def is_candidate_domain(cls, domain_or_url: str) -> bool:
        netloc = urlparse(domain_or_url).netloc.lower() if "://" in domain_or_url else domain_or_url.lower()
        netloc = netloc.split(":")[0]  # Remove port
        for pat in cls.GOV_TLD_PATTERNS:
            if pat.search(netloc):
                return True
        return False

    @classmethod
    def normalize_url(cls, url_or_domain: str) -> str:
        url = url_or_domain.strip().lower()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"https://{url}"
        parsed = urlparse(url)
        # Canonical scheme https, stripped trailing slashes
        return f"https://{parsed.netloc}".rstrip("/")

    @classmethod
    def verify_dns(cls, domain: str, timeout: float = 3.0) -> bool:
        clean_domain = domain.split(":")[0].strip().lower()
        try:
            socket.setdefaulttimeout(timeout)
            socket.gethostbyname(clean_domain)
            return True
        except (socket.gaierror, socket.timeout, Exception):
            return False

    @classmethod
    def extract_gov_links_from_html(cls, html_content: str, base_url: str) -> Set[str]:
        found_domains: Set[str] = set()
        if not html_content.strip():
            return found_domains

        try:
            doc = lxml.html.fromstring(html_content)
        except Exception:
            return found_domains

        for a in doc.xpath("//a[@href]"):
            href = (a.get("href") or "").strip()
            if not href or href.startswith("#") or href.startswith("javascript:"):
                continue

            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)
            netloc = parsed.netloc.lower().split(":")[0]

            if cls.is_candidate_domain(netloc):
                found_domains.add(netloc)

        return found_domains

    @classmethod
    def harvest_seed_registry(cls, verify_dns: bool = False) -> List[GovernmentEntityRecord]:
        raw_seeds = DomainSeedGenerator.generate_all_seeds()
        records: List[GovernmentEntityRecord] = []
        seen_domains: Set[str] = set()

        for s in raw_seeds:
            domain_name = s["domain_name"].lower().strip()
            if domain_name in seen_domains:
                continue
            seen_domains.add(domain_name)

            status = DomainStatus.VERIFIED
            if verify_dns:
                resolves = cls.verify_dns(domain_name)
                status = DomainStatus.ACTIVE if resolves else DomainStatus.UNRESOLVED

            records.append(
                GovernmentEntityRecord(
                    domain_name=domain_name,
                    base_url=f"https://{domain_name}",
                    canonical_url=f"https://{domain_name}/",
                    government_level=GovernmentLevel(s.get("government_level", GovernmentLevel.CENTRAL.value)),
                    state_or_ut=s.get("state_or_ut"),
                    district=s.get("district"),
                    entity_name=s["entity_name"],
                    status=status,
                    tags=s.get("tags", []),
                )
            )

        return records
