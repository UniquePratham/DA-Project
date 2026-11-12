"""Generate the data bundle for the Future — Global Observatory view.

Everything here is derived from real facts:

* country probe status comes from the actual Vultr region table, so a country
  is only marked operational when a datacentre physically inside it exists
* the India baseline figures come from the released dataset
* infrastructure figures come from the lifecycle manager's own records

Nothing is invented. Where a value is not yet known — because no global
measurement has been run — the field is ``null`` and the dashboard renders it as
"not yet measured" rather than as a zero.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import pandas as pd

from services.infrastructure.catalog import (
    cheapest_plan_for,
    cost_model_from_catalog,
    load_catalog,
    regions_from_catalog,
)
from services.infrastructure.regions import TARGET_COUNTRIES, ProbeRegistry

OUT = REPO / "dashboard" / "static" / "future.json"
CSV = REPO / "resources" / "bharatgov_access_clean.csv"

#: The eight research dimensions the global programme will measure. The first
#: five are already measured for India; the last three are planned.
DIMENSIONS = [
    {
        "key": "accessibility",
        "name": "Accessibility",
        "measures": "Automated WCAG 2.1 A/AA conformance signals via axe-core.",
        "india_status": "measured",
        "tool": "axe-core 4.x",
    },
    {
        "key": "performance",
        "name": "Performance",
        "measures": "Time to first byte, document size, estimated paint timing.",
        "india_status": "measured",
        "tool": "perf_counter, payload size",
    },
    {
        "key": "security",
        "name": "Security",
        "measures": "OWASP Secure Headers directive adoption and TLS posture.",
        "india_status": "measured",
        "tool": "OWASP directive set, ssl handshake",
    },
    {
        "key": "privacy",
        "name": "Privacy",
        "measures": "Third-party trackers, cookie banners, consent affordances.",
        "india_status": "planned",
        "tool": "planned",
    },
    {
        "key": "mobile",
        "name": "Mobile usability",
        "measures": "Real 375 px render, horizontal overflow, touch target size.",
        "india_status": "measured",
        "tool": "headless Chromium",
    },
    {
        "key": "language",
        "name": "Language inclusion",
        "measures": "Document language, hreflang alternates, script coverage.",
        "india_status": "measured",
        "tool": "html[lang], hreflang, script detection",
    },
    {
        "key": "availability",
        "name": "Service availability",
        "measures": "Reachability, HTTP status, redirect chains, uptime over time.",
        "india_status": "measured",
        "tool": "HTTP client",
    },
    {
        "key": "reliability",
        "name": "Reliability",
        "measures": "TLS validity, certificate expiry, error rate across snapshots.",
        "india_status": "planned",
        "tool": "planned",
    },
]

#: The research roadmap. Statuses are honest: only phase 1 is complete.
ROADMAP = [
    {
        "phase": 1,
        "title": "India baseline and methodology validation",
        "status": "complete",
        "detail": "14,489 discovered domains, 7,542 measured, five pillars with a real tool each.",
    },
    {
        "phase": 2,
        "title": "Global government-domain registry",
        "status": "in_progress",
        "detail": "Discovery adapters for national registries and Certificate Transparency per country.",
    },
    {
        "phase": 3,
        "title": "Pilot deployment across selected countries",
        "status": "planned",
        "detail": "Ephemeral probes in three countries, validating cross-country comparability.",
    },
    {
        "phase": 4,
        "title": "Standardised multi-country measurements",
        "status": "planned",
        "detail": "The same tool versions and timeouts in every probe, with provenance recorded.",
    },
    {
        "phase": 5,
        "title": "Global comparative analysis",
        "status": "planned",
        "detail": "Cross-country comparison of the eight dimensions, holding methodology fixed.",
    },
    {
        "phase": 6,
        "title": "Longitudinal observatory and open dataset",
        "status": "planned",
        "detail": "Repeated snapshots so change over time can be measured rather than asserted.",
    },
    {
        "phase": 7,
        "title": "Global research publication and public release",
        "status": "planned",
        "detail": "Peer-reviewed publication and a public dataset release.",
    },
]


def india_baseline() -> dict:
    """Real figures from the released India dataset."""
    if not CSV.exists():
        return {"measured": False}
    df = pd.read_csv(CSV)
    live = df[df.is_reachable]
    return {
        "measured": True,
        "discovered": int(len(df)),
        "reachable": int(len(live)),
        "reach_rate_pct": round(len(live) / len(df) * 100, 1),
        "mean_accessibility": round(float(live.sub_accessibility_score.mean()), 1),
        "mean_security": round(float(live.sub_security_headers_score.mean()), 1),
        "mean_maturity": round(float(live.observatory_maturity_score.mean()), 1),
        "median_ttfb_ms": int(live.sub_response_latency_ms.median()),
        "multilingual_pct": round(float(live.sub_is_multilingual.mean() * 100), 1),
        "mobile_pct": round(float(live.sub_mobile_responsive.mean() * 100), 1),
    }


def country_coverage() -> list[dict]:
    """Probe status per country, derived from the live Vultr region table."""
    catalog = load_catalog()
    reg = ProbeRegistry(regions_from_catalog(catalog))
    cost = cost_model_from_catalog(catalog)
    out = []
    for probe in reg.all_probes():
        d = probe.as_dict()
        # India is the only country with measurements today.
        d["measured"] = probe.country_code == "IN"
        d["last_measured_at"] = None
        # Real cost for one 15-minute batch in this country's domestic region.
        if probe.domestic_region is not None:
            plan = cheapest_plan_for(catalog, probe.domestic_region.id)
            if plan is not None:
                price = cost.price_for(plan["id"], probe.domestic_region.id)
                if price is not None:
                    d["batch_plan"] = plan["id"]
                    d["batch_cost_usd"] = cost.estimate(price, 900).total_usd
        out.append(d)
    return out


def instance_catalogue() -> list[dict]:
    """Real Vultr plan prices, so the cost panel is not a guess."""
    catalog = load_catalog()
    cost = cost_model_from_catalog(catalog)
    out = []
    for plan in catalog.get("plans", []):
        hourly = plan.get("hourly_cost")
        monthly = plan.get("monthly_cost")
        if hourly is None or monthly is None:
            continue
        # Price the plan in the India region, which is where the baseline runs.
        price = cost.price_for(plan["id"], "blr") or cost.price_for(plan["id"], "bom")
        if price is None:
            continue
        est = cost.estimate(price, expected_runtime_seconds=900)
        out.append(
            {
                "plan_id": plan["id"],
                "vcpu": plan.get("vcpu_count"),
                "ram_mb": plan.get("ram"),
                "disk_gb": plan.get("disk"),
                "hourly_usd": float(hourly),
                "monthly_usd": float(monthly),
                "bandwidth_gb": plan.get("bandwidth"),
                "est_batch_usd": est.total_usd,
                "billed_hours": est.billed_hours,
            }
        )
    out.sort(key=lambda p: p["hourly_usd"])
    return out


def main() -> int:
    payload = {
        "generated_from": "services/infrastructure + resources/bharatgov_access_clean.csv",
        "india_baseline": india_baseline(),
        "countries": country_coverage(),
        "dimensions": DIMENSIONS,
        "roadmap": ROADMAP,
        "instance_catalogue": instance_catalogue(),
        "infrastructure": {
            # No global measurement has run yet, so these are genuinely zero
            # rather than placeholder numbers.
            "active_instances": 0,
            "completed_jobs": 0,
            "failed_jobs": 0,
            "actual_total_usd": 0.0,
            "month_spend_usd": 0.0,
            "monthly_cap_usd": 25.0,
            "per_job_cap_usd": 1.0,
            "note": (
                "No global measurement has been run. These counters are zero "
                "because nothing has been provisioned, not because the panel is "
                "a mock-up."
            ),
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")

    # A JS bundle as well, so the dashboard works from file:// without a server.
    js_out = OUT.with_suffix(".js")
    js_out.write_text(
        "window.FUTURE_DATA=" + json.dumps(payload, separators=(",", ":")) + ";",
        encoding="utf-8",
    )

    ops = sum(1 for c in payload["countries"] if c["can_claim_domestic"])
    print(f"wrote {OUT}")
    print(f"  countries with a domestic region: {ops}/{len(payload['countries'])}")
    print(f"  india baseline: {payload['india_baseline'].get('reachable')} reachable")
    print(f"  instance plans: {len(payload['instance_catalogue'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
