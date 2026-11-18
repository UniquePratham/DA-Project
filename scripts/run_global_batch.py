"""Run measurements from several countries and record real results.

Each country gets its own ephemeral probe in a domestic region, runs the same
worker, and is destroyed. Results are appended to a single global dataset with
full provenance: which country was measured, which region measured it, and
whether that region is genuinely domestic.

The provenance rule is enforced, not assumed. A row is only marked
``domestic_probe: true`` when the probe's region country equals the target
country. Where no domestic region exists the country is skipped rather than
measured from a neighbour, because a foreign probe cannot support a domestic
claim.

Usage:
    VULTR_API_KEY=... python scripts/run_global_batch.py --countries IN,US,GB
    VULTR_API_KEY=... python scripts/run_global_batch.py --all --max 6
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import pandas as pd
import paramiko

from services.infrastructure.budget import BudgetGuard
from services.infrastructure.catalog import (
    cheapest_plan_for,
    cost_model_from_catalog,
    load_catalog,
    regions_from_catalog,
)
from services.infrastructure.lifecycle import InfrastructureManager
from services.infrastructure.selection import RegionHistory, RegionSelector
from services.infrastructure.vultr import VultrProvider

STATE = REPO / "data" / "infra" / "state.json"
LEDGER = REPO / "data" / "infra" / "ledger.json"
RESULTS = REPO / "data" / "infra" / "results"
GLOBAL_CSV = REPO / "data" / "real" / "global_measurements.csv"
WORKER = REPO / "scripts" / "crawl_real.py"

#: Real national portals and ministries per country. Chosen because they are
#: the least likely to be geo-blocked and the most likely to be up. The point
#: is a comparable cross-country sample, not a census.
SEEDS = {
    "IN": ["india.gov.in", "meity.gov.in", "nic.in", "rbi.org.in"],
    "US": ["usa.gov", "whitehouse.gov", "senate.gov", "supremecourt.gov"],
    "GB": ["gov.uk", "parliament.uk", "nhs.uk", "ons.gov.uk"],
    "DE": ["bundesregierung.de", "bundestag.de", "bmi.bund.de", "destatis.de"],
    "JP": ["japan.go.jp", "kantei.go.jp", "mofa.go.jp", "stat.go.jp"],
    "AU": ["australia.gov.au", "aph.gov.au", "ato.gov.au", "abs.gov.au"],
    "CA": ["canada.ca", "parl.ca", "justice.gc.ca", "statcan.gc.ca"],
    "FR": ["gouvernement.fr", "assemblee-nationale.fr", "legifrance.gouv.fr", "insee.fr"],
    "BR": ["gov.br", "planalto.gov.br", "camara.leg.br", "ibge.gov.br"],
    "ZA": ["gov.za", "parliament.gov.za", "sars.gov.za", "statssa.gov.za"],
    "SG": ["gov.sg", "parliament.gov.sg", "mas.gov.sg", "singstat.gov.sg"],
    "NL": ["rijksoverheid.nl", "tweedekamer.nl", "cbs.nl", "rechtspraak.nl"],
    "ES": ["lamoncloa.gob.es", "congreso.es", "ine.es", "boe.es"],
    "IT": ["governo.it", "camera.it", "istat.it", "gazzettaufficiale.it"],
    "SE": ["regeringen.se", "riksdagen.se", "scb.se", "domstol.se"],
    "PL": ["gov.pl", "sejm.gov.pl", "gus.pl", "sn.pl"],
    "KR": ["korea.kr", "assembly.go.kr", "kostat.go.kr", "scourt.go.kr"],
    "MX": ["gob.mx", "diputados.gob.mx", "inegi.org.mx", "scjn.gob.mx"],
    "CL": ["gob.cl", "congreso.cl", "ine.cl", "pjud.cl"],
    "IL": ["gov.il", "knesset.gov.il", "cbs.gov.il", "court.gov.il"],
}


def make_keypair() -> tuple[str, str]:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519

    key = ed25519.Ed25519PrivateKey.generate()
    priv = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.OpenSSH,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    pub = key.public_key().public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH,
    ).decode()
    return priv, pub


def cloud_init(public_key: str) -> str:
    return (
        "#cloud-config\n"
        "ssh_authorized_keys:\n"
        f"  - {public_key}\n"
        "package_update: true\n"
        "packages:\n"
        "  - python3-pip\n"
        "runcmd:\n"
        "  - pip3 install --quiet requests beautifulsoup4\n"
    )


def wait_for_ssh(host: str, private_key: str, timeout: float = 420.0):
    pkey = paramiko.Ed25519Key.from_private_key(io.StringIO(private_key))
    deadline = time.time() + timeout
    last = ""
    while time.time() < deadline:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(
                host, username="root", pkey=pkey, timeout=15,
                banner_timeout=20, auth_timeout=20,
                allow_agent=False, look_for_keys=False,
            )
            return client
        except Exception as exc:  # noqa: BLE001
            last = f"{type(exc).__name__}"
            client.close()
            time.sleep(10)
    raise TimeoutError(f"SSH to {host} failed within {timeout:.0f}s ({last})")


def run(client, cmd: str, timeout: float = 600.0):
    _i, out, err = client.exec_command(cmd, timeout=timeout)
    o = out.read().decode(errors="replace")
    e = err.read().decode(errors="replace")
    return o, e, out.channel.recv_exit_status()


def measure_country(
    country: str,
    catalog: dict,
    regions: list,
    budget: BudgetGuard,
    provider: VultrProvider,
    cost,
    history: RegionHistory,
) -> dict:
    """Provision, measure, verify and destroy one country's probe."""
    selector = RegionSelector(regions, history)
    chosen = selector.select(country)
    if chosen is None:
        return {"country": country, "skipped": "no domestic region"}

    plan = cheapest_plan_for(catalog, chosen.region.id, min_ram_mb=1024)
    if plan is None:
        return {"country": country, "skipped": "no suitable plan"}

    mgr = InfrastructureManager(
        provider=provider, budget=budget, cost_model=cost,
        state_path=STATE, max_concurrent_instances=1,
        max_instance_lifetime_seconds=2400,
    )

    job_id = f"global-{country.lower()}-{int(time.time())}"
    private_key, public_key = make_keypair()
    record = None
    client = None
    out: dict = {
        "country": country,
        "region": chosen.region.id,
        "region_city": chosen.region.city,
        "region_country": chosen.region.country,
        "domestic_probe": chosen.region.country == country,
        "plan": plan["id"],
        "job_id": job_id,
    }

    try:
        record = mgr.provision(
            job_id=job_id, country_code=country,
            region_id=chosen.region.id, plan_id=plan["id"],
            expected_runtime_seconds=1200, user_data=cloud_init(public_key),
        )
        mgr.wait_until_ready(job_id, timeout_seconds=600, poll_seconds=10)
        inst = provider.get_instance(record.instance_id)
        out["instance_id"] = record.instance_id
        out["public_ip"] = inst.main_ip

        client = wait_for_ssh(inst.main_ip, private_key)

        # Wait for cloud-init to finish installing deps.
        run(
            client,
            "for i in $(seq 1 30); do python3 -c 'import requests,bs4' 2>/dev/null "
            "&& exit 0; sleep 10; done; exit 1",
            timeout=400,
        )

        sftp = client.open_sftp()
        sftp.put(str(WORKER), "/root/crawl_real.py")
        domains = SEEDS.get(country, [])[:4]
        sftp.putfo(io.BytesIO(json.dumps(domains).encode()), "/root/domains.json")
        sftp.close()

        mgr.mark_running(job_id)
        run(
            client,
            "cd /root && PYTHONWARNINGS=ignore python3 crawl_real.py "
            "--domains domains.json --out results.csv --workers 4 --timeout 25",
            timeout=900,
        )

        mgr.mark_uploading(job_id)
        RESULTS.mkdir(parents=True, exist_ok=True)
        local = RESULTS / f"{job_id}.csv"
        sftp = client.open_sftp()
        sftp.get("/root/results.csv", str(local))
        remote_hash = run(client, "sha256sum /root/results.csv | cut -d' ' -f1")[0].strip()
        sftp.close()

        h = hashlib.sha256()
        with local.open("rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        verified = h.hexdigest() == remote_hash

        df = pd.read_csv(local)
        df["probe_country"] = country
        df["probe_region"] = chosen.region.id
        df["probe_region_country"] = chosen.region.country
        df["domestic_probe"] = chosen.region.country == country
        df["measured_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        df["job_id"] = job_id

        GLOBAL_CSV.parent.mkdir(parents=True, exist_ok=True)
        header = not GLOBAL_CSV.exists()
        df.to_csv(GLOBAL_CSV, mode="a", header=header, index=False)

        out["rows"] = len(df)
        out["reachable"] = int(df.is_reachable.sum())
        out["verified"] = verified
        mgr.mark_verified(job_id, verified, f"sha256 {h.hexdigest()[:16]}")

    except Exception as exc:  # noqa: BLE001
        out["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        if client is not None:
            client.close()
        if record and record.instance_id:
            try:
                final = mgr.destroy(job_id, force=not record.results_verified)
                out["destroyed"] = True
                out["actual_usd"] = final.actual_usd
            except Exception as exc:  # noqa: BLE001
                out["destroy_error"] = str(exc)

    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--countries", default="")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--max", type=int, default=6)
    args = ap.parse_args()

    catalog = load_catalog()
    regions = regions_from_catalog(catalog)
    cost = cost_model_from_catalog(catalog)
    budget = BudgetGuard(per_job_usd=0.05, monthly_usd=2.00, ledger_path=LEDGER)
    provider = VultrProvider()
    history = RegionHistory()

    if args.all:
        targets = [c for c in SEEDS if RegionSelector(regions).select(c)]
    else:
        targets = [c.strip().upper() for c in args.countries.split(",") if c.strip()]
    targets = targets[: args.max]

    print(f"targets: {', '.join(targets)}")
    print(f"budget : ${budget.month_spend():.4f} spent of ${budget.monthly_usd:.2f}\n")

    results = []
    for i, country in enumerate(targets, 1):
        print(f"[{i}/{len(targets)}] {country}")
        r = measure_country(country, catalog, regions, budget, provider, cost, history)
        results.append(r)
        if r.get("skipped"):
            print(f"  skipped: {r['skipped']}")
        elif r.get("error"):
            print(f"  ERROR: {r['error']}")
        else:
            print(
                f"  {r['region']} ({r['region_city']}) "
                f"{r['reachable']}/{r['rows']} reachable, "
                f"verified={r.get('verified')}, ${r.get('actual_usd') or 0:.4f}"
            )
        print()

    summary = REPO / "data" / "infra" / "global_batch.json"
    summary.write_text(json.dumps(results, indent=2), encoding="utf-8")

    ok = [r for r in results if not r.get("error") and not r.get("skipped")]
    print(f"completed: {len(ok)}/{len(targets)}")
    print(f"total cost: ${sum(r.get('actual_usd') or 0 for r in results):.4f}")
    if GLOBAL_CSV.exists():
        df = pd.read_csv(GLOBAL_CSV)
        print(f"global dataset: {len(df)} rows from {df.probe_country.nunique()} countries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
