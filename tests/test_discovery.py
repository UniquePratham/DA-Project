"""Unit tests for the Discovery Harvester and Seed Sources."""

import pytest
from schemas.domain import GovernmentLevel, DomainStatus
from services.discovery.seed_sources import DomainSeedGenerator
from services.discovery.harvester import DomainHarvester
from services.discovery.registry import DomainRegistryManager


def test_seed_generator():
    seeds = DomainSeedGenerator.generate_all_seeds()
    assert len(seeds) > 100  # Central + 36 States + 100+ Districts

    # Check Central representation
    central_seeds = [s for s in seeds if s["government_level"] == "central"]
    assert len(central_seeds) >= 30
    assert any("india.gov.in" in s["domain_name"] for s in central_seeds)
    assert any("mha.gov.in" in s["domain_name"] for s in central_seeds)

    # Check District representation
    district_seeds = [s for s in seeds if s["government_level"] == "district"]
    assert len(district_seeds) >= 100
    assert any("varanasi.nic.in" in s["domain_name"] for s in district_seeds)
    assert any("pune.nic.in" in s["domain_name"] for s in district_seeds)


def test_candidate_domain_matching():
    assert DomainHarvester.is_candidate_domain("https://mohfw.gov.in/path") is True
    assert DomainHarvester.is_candidate_domain("varanasi.nic.in") is True
    assert DomainHarvester.is_candidate_domain("iitkgp.ac.in") is True
    assert DomainHarvester.is_candidate_domain("google.com") is False
    assert DomainHarvester.is_candidate_domain("commercial-site.in") is False


def test_html_gov_links_extraction():
    sample_html = """
    <div>
        <a href="https://digitalindia.gov.in">Digital India</a>
        <a href="/about">Internal Link</a>
        <a href="https://external-bank.com">Bank</a>
        <a href="https://uidai.gov.in/contact">UIDAI</a>
    </div>
    """
    links = DomainHarvester.extract_gov_links_from_html(sample_html, "https://sample.gov.in")
    assert "digitalindia.gov.in" in links
    assert "uidai.gov.in" in links
    assert "external-bank.com" not in links


def test_registry_manager(tmp_path):
    mgr = DomainRegistryManager(registry_file=tmp_path / "registry.json")
    count = mgr.load_seeds(verify_dns=False)
    assert count > 100

    # Filter by state
    up_districts = mgr.list_domains(state="Uttar Pradesh", level=GovernmentLevel.DISTRICT)
    assert len(up_districts) >= 10

    # Save to disk
    out_file = mgr.save_to_file()
    assert out_file.exists()
