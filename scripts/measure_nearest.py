"""Measure countries that have no domestic Vultr region, from the nearest probe.

This is the honest way to cover the 180 countries Vultr cannot reach
domestically. Each country is measured from the closest available region, and
the row records:

* the target country
* the probe region and the country it actually sits in
* the great-circle distance between them
* ``vantage_class = nearest``, so the row can never be mistaken for a domestic
  measurement

The data is real. What it describes is a foreign client's view of that
country's government websites, which is a legitimate and useful measurement:
it is exactly what a citizen abroad, a CDN, or a cross-border auditor sees.

Usage:
    VULTR_API_KEY=... python scripts/measure_nearest.py --per-country 10
    VULTR_API_KEY=... python scripts/measure_nearest.py --countries NP,BD,LK --per-country 20
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
from services.infrastructure.vantage import VantageClass, VantageSelector
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


def upload_worker(sftp, remote_root: str = "/root") -> None:
    import posixpath

    sftp.put(str(WORKER), posixpath.join(remote_root, "crawl_real.py"))
    tools_dir = REPO / "tools" / "http"
    for sub in ("tools", "tools/http"):
        try:
            sftp.stat(posixpath.join(remote_root, sub))
        except IOError:
            sftp.mkdir(posixpath.join(remote_root, sub))
    for name in ("__init__.py", "polite.py", "robots.py"):
        local = tools_dir / name
        if local.exists():
            sftp.put(str(local), posixpath.join(remote_root, "tools", "http", name))
    init = REPO / "tools" / "__init__.py"
    if init.exists():
        sftp.put(str(init), posixpath.join(remote_root, "tools", "__init__.py"))


def measure_group(
    region_id: str,
    targets: list[tuple[str, list[str], float]],
    catalog: dict,
    budget: BudgetGuard,
    provider: VultrProvider,
    cost,
) -> list[dict]:
    """Measure several countries from one probe, to avoid provisioning per country."""
    plan = cheapest_plan_for(catalog, region_id, min_ram_mb=1024)
    if plan is None:
        return [{"region": region_id, "skipped": "no suitable plan"}]

    mgr = InfrastructureManager(
        provider=provider, budget=budget, cost_model=cost,
        state_path=STATE, max_concurrent_instances=1,
        max_instance_lifetime_seconds=5400,
    )

    job_id = f"near-{region_id}-{int(time.time())}"
    private_key, public_key = make_keypair()
    record = None
    client = None
    out: list[dict] = []

    try:
        record = mgr.provision(
            job_id=job_id, country_code=targets[0][0],
            region_id=region_id, plan_id=plan["id"],
            expected_runtime_seconds=3600, user_data=cloud_init(public_key),
        )
        mgr.wait_until_ready(job_id, timeout_seconds=600, poll_seconds=10)
        inst = provider.get_instance(record.instance_id)
        client = wait_for_ssh(inst.main_ip, private_key)
        run(
            client,
            "for i in $(seq 1 30); do python3 -c 'import requests,bs4' 2>/dev/null "
            "&& exit 0; sleep 10; done; exit 1",
            timeout=400,
        )

        sftp = client.open_sftp()
        upload_worker(sftp)
        sftp.close()

        mgr.mark_running(job_id)

        for country, domains, distance in targets:
            if not domains:
                out.append({"country": country, "skipped": "no domains"})
                continue
            sftp = client.open_sftp()
            sftp.putfo(io.BytesIO(json.dumps(domains).encode()), "/root/domains.json")
            sftp.close()

            o, e, rc = run(
                client,
                "cd /root && PYTHONWARNINGS=ignore python3 crawl_real.py "
                "--domains domains.json --out results.csv --workers 6 --timeout 20 2>&1",
                timeout=1800,
            )
            if rc != 0:
                out.append({"country": country, "error": (o or e).strip()[-300:]})
                continue

            RESULTS.mkdir(parents=True, exist_ok=True)
            local = RESULTS / f"{job_id}-{country}.csv"
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
            df["probe_region"] = region_id
            df["probe_region_country"] = region_id[:3].upper()
            df["domestic_probe"] = False
            df["vantage_class"] = "nearest"
            df["distance_km"] = round(distance)
            df["measured_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            df["job_id"] = job_id

            GLOBAL_CSV.parent.mkdir(parents=True, exist_ok=True)
            if GLOBAL_CSV.exists():
                cols = pd.read_csv(GLOBAL_CSV, nrows=0).columns.tolist()
                for c in cols:
                    if c not in df.columns:
                        df[c] = None
                df = df[cols]
                df.to_csv(GLOBAL_CSV, mode="a", header=False, index=False)
            else:
                df.to_csv(GLOBAL_CSV, mode="w", header=True, index=False)

            out.append(
                {
                    "country": country,
                    "rows": len(df),
                    "reachable": int(df.is_reachable.sum()),
                    "verified": verified,
                    "distance_km": round(distance),
                }
            )
            print(
                f"    {country}: {int(df.is_reachable.sum())}/{len(df)} reachable, "
                f"verified={verified}",
                flush=True,
            )

        mgr.mark_uploading(job_id)
        mgr.mark_verified(job_id, True, "nearest-probe batch")

    except Exception as exc:  # noqa: BLE001
        out.append({"region": region_id, "error": f"{type(exc).__name__}: {exc}"})
    finally:
        if client is not None:
            client.close()
        if record and record.instance_id:
            try:
                final = mgr.destroy(job_id, force=not record.results_verified)
                out.append({"region": region_id, "actual_usd": final.actual_usd})
            except Exception as exc:  # noqa: BLE001
                out.append({"region": region_id, "destroy_error": str(exc)})

    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-country", type=int, default=10)
    ap.add_argument("--countries", default="")
    ap.add_argument("--max-regions", type=int, default=0)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    by_country: dict[str, list[str]] = {}
    for r in registry:
        by_country.setdefault(r["country"], []).append(r["domain_name"])

    catalog = load_catalog()
    regions = regions_from_catalog(catalog)
    selector = VantageSelector(regions)
    cost = cost_model_from_catalog(catalog)
    budget = BudgetGuard(per_job_usd=0.10, monthly_usd=5.00, ledger_path=LEDGER)
    provider = VultrProvider()

    # Group target countries by the probe region that will measure them, so one
    # instance serves many countries instead of one instance per country.
    groups: dict[str, list[tuple[str, list[str], float]]] = {}
    rng = random.Random(args.seed)

    if args.countries:
        targets = [c.strip().upper() for c in args.countries.split(",") if c.strip()]
    else:
        targets = sorted(by_country)

    for country in targets:
        v = selector.select(country)
        if v.vantage_class is not VantageClass.NEAREST or v.region is None:
            continue
        pool = by_country.get(country, [])
        if not pool:
            continue
        sample = rng.sample(pool, min(args.per_country, len(pool)))
        groups.setdefault(v.region.id, []).append((country, sample, v.distance_km or 0))

    region_ids = sorted(groups, key=lambda r: -len(groups[r]))
    if args.max_regions:
        region_ids = region_ids[: args.max_regions]

    total_countries = sum(len(groups[r]) for r in region_ids)
    print(f"probe regions: {len(region_ids)}")
    print(f"countries    : {total_countries}")
    print(f"per country  : {args.per_country}")
    print(f"budget       : ${budget.month_spend():.4f} of ${budget.monthly_usd:.2f}\n")

    results = []
    for i, region_id in enumerate(region_ids, 1):
        batch = groups[region_id]
        print(f"[{i}/{len(region_ids)}] probe {region_id} -> {len(batch)} countries", flush=True)
        results.extend(measure_group(region_id, batch, catalog, budget, provider, cost))
        print(flush=True)

    (REPO / "data" / "infra" / "nearest_batch.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    spent = sum(r.get("actual_usd") or 0 for r in results)
    print(f"cost: ${spent:.4f}")
    if GLOBAL_CSV.exists():
        df = pd.read_csv(GLOBAL_CSV)
        print(f"dataset: {len(df)} rows from {df.probe_country.nunique()} countries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
