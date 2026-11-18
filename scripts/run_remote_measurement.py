"""Deploy the measurement worker to a provisioned instance and run a job.

This closes the gap between "the lifecycle works" and "the observatory works":
the instance is provisioned, the worker is installed over SSH, a real
measurement batch runs on the instance, the results are pulled back, and the
checksum is verified before the instance is destroyed.

The worker is the same `scripts/crawl_real.py` used for the India census, so a
measurement taken on an ephemeral probe is directly comparable to one taken on
the permanent node. That comparability is the whole point of the global
expansion.

Safety:
* the instance is destroyed in a ``finally`` block
* results are verified by SHA-256 before destruction is permitted
* the budget guard caps the run at $0.05
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

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
WORKER = REPO / "scripts" / "crawl_real.py"

#: A tiny, stable set of government domains per country. These are the national
#: portal and a ministry, chosen because they are the least likely to be
#: geo-blocked and the most likely to be up. The point of the proof is the
#: pipeline, not the sample size.
SEED_DOMAINS = {
    "IN": ["india.gov.in", "meity.gov.in", "nic.in"],
    "US": ["usa.gov", "whitehouse.gov", "senate.gov"],
    "GB": ["gov.uk", "parliament.uk", "nhs.uk"],
    "DE": ["bundesregierung.de", "bundestag.de", "bmi.bund.de"],
    "JP": ["japan.go.jp", "kantei.go.jp", "mofa.go.jp"],
    "AU": ["australia.gov.au", "aph.gov.au", "ato.gov.au"],
    "CA": ["canada.ca", "parl.ca", "justice.gc.ca"],
    "FR": ["gouvernement.fr", "assemblee-nationale.fr", "legifrance.gouv.fr"],
    "BR": ["gov.br", "planalto.gov.br", "camara.leg.br"],
    "ZA": ["gov.za", "parliament.gov.za", "sars.gov.za"],
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def make_keypair() -> tuple[str, str]:
    """Generate a throwaway SSH keypair for one instance.

    The private key exists only in memory for the duration of the run. It is
    never written to disk and never reused, so a leaked instance cannot be
    reached after the job ends.
    """
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
    """Cloud-init that installs the ephemeral key and the worker's deps."""
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


def wait_for_ssh(host: str, private_key: str, timeout: float = 420.0) -> paramiko.SSHClient:
    """Poll until SSH accepts the ephemeral key, then return the client."""
    import io as _io

    pkey = paramiko.Ed25519Key.from_private_key(_io.StringIO(private_key))
    deadline = time.time() + timeout
    last = ""
    while time.time() < deadline:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(
                host,
                username="root",
                pkey=pkey,
                timeout=15,
                banner_timeout=20,
                auth_timeout=20,
                allow_agent=False,
                look_for_keys=False,
            )
            return client
        except Exception as exc:  # noqa: BLE001
            last = f"{type(exc).__name__}: {exc}"
            client.close()
            time.sleep(10)
    raise TimeoutError(f"SSH to {host} did not come up within {timeout:.0f}s ({last})")


def run(client: paramiko.SSHClient, cmd: str, timeout: float = 600.0) -> tuple[str, str, int]:
    _in, out, err = client.exec_command(cmd, timeout=timeout)
    o = out.read().decode(errors="replace")
    e = err.read().decode(errors="replace")
    return o, e, out.channel.recv_exit_status()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", default="IN")
    ap.add_argument("--domains", type=int, default=3)
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    catalog = load_catalog()
    regions = regions_from_catalog(catalog)
    selector = RegionSelector(regions, RegionHistory())
    chosen = selector.select_or_raise(args.country)
    plan = cheapest_plan_for(catalog, chosen.region.id, min_ram_mb=1024)

    cost = cost_model_from_catalog(catalog)
    price = cost.price_for(plan["id"], chosen.region.id)

    print(f"country   : {args.country}")
    print(f"region    : {chosen.region.id} ({chosen.region.city})")
    print(f"plan      : {plan['id']} ({plan['ram']} MB)")

    budget = BudgetGuard(per_job_usd=0.05, monthly_usd=1.00, ledger_path=LEDGER)
    provider = VultrProvider(dry_run=args.dry_run)
    mgr = InfrastructureManager(
        provider=provider,
        budget=budget,
        cost_model=cost,
        state_path=STATE,
        dry_run=args.dry_run,
        max_concurrent_instances=1,
        max_instance_lifetime_seconds=2400,
    )

    job_id = f"measure-{args.country.lower()}-{int(time.time())}"
    record = None
    client = None
    outcome: dict = {"job_id": job_id, "country": args.country}
    private_key, public_key = make_keypair()

    try:
        record = mgr.provision(
            job_id=job_id,
            country_code=args.country,
            region_id=chosen.region.id,
            plan_id=plan["id"],
            expected_runtime_seconds=1200,
            user_data=cloud_init(public_key),
        )
        print(f"instance  : {record.instance_id}")

        mgr.wait_until_ready(job_id, timeout_seconds=600, poll_seconds=10)
        inst = provider.get_instance(record.instance_id)
        host = inst.main_ip
        print(f"public ip : {host}")

        if args.dry_run:
            print("dry-run: skipping SSH and measurement")
            mgr.mark_running(job_id)
            mgr.mark_uploading(job_id)
            mgr.mark_verified(job_id, True, "dry-run")
            outcome["dry_run"] = True
            return 0

        print("waiting for ssh...")
        client = wait_for_ssh(host, private_key)
        print("ssh       : connected")

        # Cloud-init installs the deps; verify rather than reinstall.
        print("checking worker deps...")
        o, e, rc = run(
            client,
            "for i in $(seq 1 30); do "
            "python3 -c 'import requests,bs4' 2>/dev/null && { echo 'deps ok'; exit 0; }; "
            "sleep 10; done; echo 'deps missing'; exit 1",
            timeout=400,
        )
        print("  ", (o or e).strip().splitlines()[-1] if (o or e).strip() else "done")

        sftp = client.open_sftp()
        sftp.put(str(WORKER), "/root/crawl_real.py")
        domains = SEED_DOMAINS.get(args.country.upper(), [])[: args.domains]
        sftp.putfo(io.BytesIO(json.dumps(domains).encode()), "/root/domains.json")
        sftp.close()
        print(f"worker    : uploaded, {len(domains)} domains")

        mgr.mark_running(job_id)
        print("measuring...")
        o, e, rc = run(
            client,
            "cd /root && PYTHONWARNINGS=ignore python3 crawl_real.py "
            "--domains domains.json --out results.csv --workers 3 --timeout 25 2>&1 | tail -6",
            timeout=900,
        )
        print("  ", o.strip().replace("\n", "\n   "))

        # Pull the results back and verify the checksum before destroying.
        mgr.mark_uploading(job_id)
        RESULTS.mkdir(parents=True, exist_ok=True)
        local = RESULTS / f"{job_id}.csv"
        sftp = client.open_sftp()
        sftp.get("/root/results.csv", str(local))
        remote_hash = run(client, "sha256sum /root/results.csv | cut -d' ' -f1")[0].strip()
        sftp.close()

        local_hash = sha256_file(local)
        verified = bool(remote_hash) and remote_hash == local_hash
        print(f"results   : {local.name} ({local.stat().st_size} bytes)")
        print(f"checksum  : {'MATCH' if verified else 'MISMATCH'} ({local_hash[:16]}…)")

        outcome["results_file"] = str(local)
        outcome["sha256"] = local_hash
        outcome["verified"] = verified

        mgr.mark_verified(job_id, verified, f"sha256 {local_hash[:16]}")

    except Exception as exc:  # noqa: BLE001
        print(f"FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        outcome["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        if client is not None:
            client.close()
        if record and record.instance_id and not args.keep:
            try:
                final = mgr.destroy(job_id, force=not record.results_verified)
                print(f"destroyed : {final.instance_id}")
                print(f"cost      : ${final.actual_usd or 0:.4f}")
                outcome["destroyed"] = True
                outcome["actual_usd"] = final.actual_usd
            except Exception as exc:  # noqa: BLE001
                print(f"DESTROY FAILED: {exc}", file=sys.stderr)
                outcome["destroy_error"] = str(exc)

    outcome["summary"] = mgr.summary()
    (REPO / "data" / "infra" / "last_run.json").write_text(
        json.dumps(outcome, indent=2), encoding="utf-8"
    )
    return 0 if "error" not in outcome and "destroy_error" not in outcome else 1


if __name__ == "__main__":
    raise SystemExit(main())
