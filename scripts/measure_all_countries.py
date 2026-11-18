"""Measure a sample from every country in the global registry.

For each country: pick a random sample of discovered domains, provision a
domestic probe, measure them, verify the checksum, destroy the probe, and
append the results with full provenance.

The sample is random from the discovered registry, not hand-picked. That is the
difference between a measurement and an illustration.

Usage:
    VULTR_API_KEY=... python scripts/measure_all_countries.py --per-country 20
    VULTR_API_KEY=... python scripts/measure_all_countries.py --countries IN,US --per-country 50
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import random
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
REGISTRY = REPO / "data" / "fixtures" / "global_domains.json"
WORKER = REPO / "scripts" / "crawl_real.py"


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
        except Exception:  # noqa: BLE001
            client.close()
            time.sleep(10)
    raise TimeoutError(f"SSH to {host} failed within {timeout:.0f}s")


def run(client, cmd: str, timeout: float = 900.0):
    _i, out, err = client.exec_command(cmd, timeout=timeout)
    o = out.read().decode(errors="replace")
    e = err.read().decode(errors="replace")
    return o, e, out.channel.recv_exit_status()


def measure_country(
    country: str, domains: list[str], catalog: dict, regions: list,
    budget: BudgetGuard, provider: VultrProvider, cost, history: RegionHistory,
) -> dict:
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
        max_instance_lifetime_seconds=3600,
    )

    job_id = f"all-{country.lower()}-{int(time.time())}"
    private_key, public_key = make_keypair()
    record = None
    client = None
    out: dict = {
        "country": country, "region": chosen.region.id,
        "region_city": chosen.region.city,
        "region_country": chosen.region.country,
        "domestic_probe": chosen.region.country == country,
        "plan": plan["id"], "job_id": job_id, "requested": len(domains),
    }

    try:
        record = mgr.provision(
            job_id=job_id, country_code=country,
            region_id=chosen.region.id, plan_id=plan["id"],
            expected_runtime_seconds=2400, user_data=cloud_init(public_key),
        )
        mgr.wait_until_ready(job_id, timeout_seconds=600, poll_seconds=10)
        inst = provider.get_instance(record.instance_id)
        out["instance_id"] = record.instance_id
        out["public_ip"] = inst.main_ip

        client = wait_for_ssh(inst.main_ip, private_key)
        run(
            client,
            "for i in $(seq 1 30); do python3 -c 'import requests,bs4' 2>/dev/null "
            "&& exit 0; sleep 10; done; exit 1",
            timeout=400,
        )

        sftp = client.open_sftp()
        upload_worker(sftp)
        sftp.putfo(io.BytesIO(json.dumps(domains).encode()), "/root/domains.json")
        sftp.close()

        mgr.mark_running(job_id)
        out_text, err_text, rc = run(
            client,
            "cd /root && PYTHONWARNINGS=ignore python3 crawl_real.py "
            "--domains domains.json --out results.csv --workers 8 --timeout 20 2>&1",
            timeout=1800,
        )
        if rc != 0:
            raise RuntimeError(
                f"remote worker exited {rc}: {(out_text or err_text).strip()[-600:]}"
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
        if GLOBAL_CSV.exists():
            # Align to the existing schema so a new column does not corrupt the
            # file. Missing columns are added as NaN, extra ones are dropped.
            existing_cols = pd.read_csv(GLOBAL_CSV, nrows=0).columns.tolist()
            for col in existing_cols:
                if col not in df.columns:
                    df[col] = None
            df = df[existing_cols]
            df.to_csv(GLOBAL_CSV, mode="a", header=False, index=False)
        else:
            df.to_csv(GLOBAL_CSV, mode="w", header=True, index=False)

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



def upload_worker(sftp, remote_root: str = "/root") -> None:
    """Upload the crawler and the tools package it imports.

    The worker is not self-contained: it imports tools.http.polite, which in
    turn imports tools.http.robots. Uploading only crawl_real.py produces a
    ModuleNotFoundError on the instance, so the package goes with it.
    """
    import posixpath

    sftp.put(str(WORKER), posixpath.join(remote_root, "crawl_real.py"))

    tools_dir = REPO / "tools" / "http"
    try:
        sftp.stat(posixpath.join(remote_root, "tools"))
    except IOError:
        sftp.mkdir(posixpath.join(remote_root, "tools"))
    try:
        sftp.stat(posixpath.join(remote_root, "tools", "http"))
    except IOError:
        sftp.mkdir(posixpath.join(remote_root, "tools", "http"))

    for name in ("__init__.py", "polite.py", "robots.py"):
        local = tools_dir / name
        if local.exists():
            sftp.put(str(local), posixpath.join(remote_root, "tools", "http", name))

    init = REPO / "tools" / "__init__.py"
    if init.exists():
        sftp.put(str(init), posixpath.join(remote_root, "tools", "__init__.py"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-country", type=int, default=20)
    ap.add_argument("--countries", default="")
    ap.add_argument("--max-countries", type=int, default=0)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    by_country: dict[str, list[str]] = {}
    for r in registry:
        by_country.setdefault(r["country"], []).append(r["domain_name"])

    catalog = load_catalog()
    regions = regions_from_catalog(catalog)
    cost = cost_model_from_catalog(catalog)
    budget = BudgetGuard(per_job_usd=0.05, monthly_usd=5.00, ledger_path=LEDGER)
    provider = VultrProvider()
    history = RegionHistory()

    if args.countries:
        targets = [c.strip().upper() for c in args.countries.split(",") if c.strip()]
    else:
        # Only countries with a domestic region can be measured honestly.
        sel = RegionSelector(regions)
        targets = sorted(c for c in by_country if sel.select(c))
    if args.max_countries:
        targets = targets[: args.max_countries]

    rng = random.Random(args.seed)
    print(f"countries: {len(targets)}")
    print(f"per country: {args.per_country}")
    print(f"budget: ${budget.month_spend():.4f} of ${budget.monthly_usd:.2f}\n")

    results = []
    for i, country in enumerate(targets, 1):
        pool = by_country.get(country, [])
        sample = rng.sample(pool, min(args.per_country, len(pool)))
        print(f"[{i}/{len(targets)}] {country} ({len(pool)} discovered, sampling {len(sample)})")
        r = measure_country(
            country, sample, catalog, regions, budget, provider, cost, history
        )
        results.append(r)
        if r.get("skipped"):
            print(f"  skipped: {r['skipped']}")
        elif r.get("error"):
            print(f"  ERROR: {r['error']}")
        else:
            print(
                f"  {r['region']} {r['reachable']}/{r['rows']} reachable, "
                f"verified={r.get('verified')}, ${r.get('actual_usd') or 0:.4f}"
            )
        print(flush=True)

    (REPO / "data" / "infra" / "all_countries.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    ok = [r for r in results if not r.get("error") and not r.get("skipped")]
    print(f"completed: {len(ok)}/{len(targets)}")
    print(f"cost: ${sum(r.get('actual_usd') or 0 for r in results):.4f}")
    if GLOBAL_CSV.exists():
        df = pd.read_csv(GLOBAL_CSV)
        print(f"dataset: {len(df)} rows from {df.probe_country.nunique()} countries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
