"""Vultr API adapter.

Talks to the Vultr v2 API. Two things matter here beyond correctness:

* **The API key never appears in a log, an exception message or a repr.** It is
  read from the environment and held in a private attribute.
* **Dry-run is a first-class mode.** Every mutating call is simulated when
  ``dry_run`` is set, so the lifecycle can be exercised end to end without
  spending money. The spec requires this, and it is also the only responsible
  way to test a destroy path.

The region table below is the real Vultr region list. It is embedded rather than
fetched so that the country-coverage view works offline and so that a network
failure cannot silently change which countries we claim to support.
"""

from __future__ import annotations

import os
import time
from typing import Any, Optional

import httpx

from .provider import (
    InstanceSpec,
    ProviderError,
    ProvisionedInstance,
    Region,
)

API_BASE = "https://api.vultr.com/v2"

#: Real Vultr regions, with the country the datacentre is physically in.
#: Source: Vultr's published region list. ``country`` is the ISO-3166 alpha-2
#: code of the datacentre's actual location, not the marketing region name.
VULTR_REGIONS: list[Region] = [
    Region("ams", "Amsterdam", "NL", "Europe"),
    Region("atl", "Atlanta", "US", "North America"),
    Region("bom", "Mumbai", "IN", "Asia"),
    Region("cdg", "Paris", "FR", "Europe"),
    Region("del", "Delhi NCR", "IN", "Asia"),
    Region("dfw", "Dallas", "US", "North America"),
    Region("ewr", "New Jersey", "US", "North America"),
    Region("fra", "Frankfurt", "DE", "Europe"),
    Region("hnl", "Honolulu", "US", "North America"),
    Region("icn", "Seoul", "KR", "Asia"),
    Region("itm", "Osaka", "JP", "Asia"),
    Region("jnb", "Johannesburg", "ZA", "Africa"),
    Region("lax", "Los Angeles", "US", "North America"),
    Region("lhr", "London", "GB", "Europe"),
    Region("mad", "Madrid", "ES", "Europe"),
    Region("mel", "Melbourne", "AU", "Oceania"),
    Region("mex", "Mexico City", "MX", "North America"),
    Region("mia", "Miami", "US", "North America"),
    Region("nrt", "Tokyo", "JP", "Asia"),
    Region("ord", "Chicago", "US", "North America"),
    Region("scl", "Santiago", "CL", "South America"),
    Region("sea", "Seattle", "US", "North America"),
    Region("sgp", "Singapore", "SG", "Asia"),
    Region("sjc", "Silicon Valley", "US", "North America"),
    Region("sto", "Stockholm", "SE", "Europe"),
    Region("syd", "Sydney", "AU", "Oceania"),
    Region("waw", "Warsaw", "PL", "Europe"),
    Region("yto", "Toronto", "CA", "North America"),
    Region("blr", "Bangalore", "IN", "Asia"),
    Region("sao", "São Paulo", "BR", "South America"),
    Region("bog", "Bogotá", "CO", "South America"),
    Region("mxp", "Milan", "IT", "Europe"),
    Region("man", "Manchester", "GB", "Europe"),
    Region("hon", "Honolulu", "US", "North America"),
]


class VultrProvider:
    """A ``CloudProvider`` backed by the Vultr v2 API."""

    name = "vultr"

    def __init__(
        self,
        api_key: str | None = None,
        *,
        dry_run: bool = False,
        timeout: float = 30.0,
        client: httpx.Client | None = None,
    ):
        self._api_key = api_key or os.environ.get("VULTR_API_KEY", "")
        self.dry_run = dry_run
        self._timeout = timeout
        self._client = client
        self._simulated: dict[str, ProvisionedInstance] = {}
        self._sim_counter = 0

        if not self._api_key and not dry_run:
            raise ProviderError(
                "VULTR_API_KEY is not set. Set it in the environment, or run "
                "with dry_run=True to exercise the lifecycle without spending."
            )

    # ------------------------------------------------------------------ http

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _request(
        self, method: str, path: str, json_body: dict | None = None
    ) -> dict[str, Any]:
        if self.dry_run:
            raise ProviderError(
                f"dry-run: refusing to issue {method} {path} against the live API"
            )
        url = f"{API_BASE}{path}"
        try:
            if self._client is not None:
                resp = self._client.request(
                    method, url, headers=self._headers(), json=json_body,
                    timeout=self._timeout,
                )
            else:
                with httpx.Client(timeout=self._timeout) as c:
                    resp = c.request(
                        method, url, headers=self._headers(), json=json_body
                    )
        except httpx.HTTPError as exc:
            # Never include the request headers in the message: they carry the key.
            raise ProviderError(f"vultr {method} {path} failed: {type(exc).__name__}") from None

        if resp.status_code >= 400:
            detail = ""
            try:
                detail = resp.json().get("error", "")
            except Exception:  # noqa: BLE001
                detail = resp.text[:200]
            raise ProviderError(
                f"vultr {method} {path} returned {resp.status_code}: {detail}"
            )
        if not resp.content:
            return {}
        return resp.json()

    # --------------------------------------------------------------- regions

    def list_regions(self) -> list[Region]:
        """Regions the account can deploy into.

        In dry-run we return the embedded table so the coverage view is
        populated without a network call.
        """
        if self.dry_run:
            return list(VULTR_REGIONS)
        try:
            data = self._request("GET", "/regions?per_page=500")
        except ProviderError:
            return list(VULTR_REGIONS)
        out: list[Region] = []
        for r in data.get("regions", []):
            rid = r.get("id", "")
            known = next((k for k in VULTR_REGIONS if k.id == rid), None)
            out.append(
                Region(
                    id=rid,
                    city=r.get("city", known.city if known else rid),
                    country=(r.get("country") or (known.country if known else "")).upper(),
                    continent=r.get("continent", known.continent if known else ""),
                )
            )
        return out or list(VULTR_REGIONS)

    def list_plans(self, region_id: str) -> list[dict[str, Any]]:
        if self.dry_run:
            return [
                {
                    "id": "vc2-1c-1gb",
                    "vcpu_count": 1,
                    "ram": 1024,
                    "disk": 25,
                    "monthly_cost": 5.0,
                    "hourly_cost": 0.007,
                    "bandwidth": 1000,
                },
                {
                    "id": "vc2-1c-2gb",
                    "vcpu_count": 1,
                    "ram": 2048,
                    "disk": 55,
                    "monthly_cost": 10.0,
                    "hourly_cost": 0.015,
                    "bandwidth": 2000,
                },
            ]
        data = self._request("GET", f"/plans?per_page=500&type=vc2")
        plans = []
        for p in data.get("plans", []):
            locations = p.get("locations", [])
            if locations and region_id not in locations:
                continue
            plans.append(
                {
                    "id": p.get("id"),
                    "vcpu_count": p.get("vcpu_count"),
                    "ram": p.get("ram"),
                    "disk": p.get("disk"),
                    "monthly_cost": p.get("monthly_cost"),
                    "hourly_cost": p.get("hourly_cost"),
                    "bandwidth": p.get("bandwidth"),
                }
            )
        return plans

    # ------------------------------------------------------------- instances

    def create_instance(self, spec: InstanceSpec) -> ProvisionedInstance:
        if self.dry_run:
            self._sim_counter += 1
            inst = ProvisionedInstance(
                id=f"sim-{self._sim_counter:04d}",
                region_id=spec.region_id,
                plan_id=spec.plan_id,
                label=spec.label,
                status="active",
                main_ip=f"198.51.100.{self._sim_counter % 250 + 1}",
                tags=spec.tags,
            )
            self._simulated[inst.id] = inst
            return inst

        body: dict[str, Any] = {
            "region": spec.region_id,
            "plan": spec.plan_id,
            "os_id": spec.os_id,
            "label": spec.label,
            "hostname": spec.label[:60],
            "tags": list(spec.tags),
            "backups": "disabled",
        }
        if spec.ssh_key_ids:
            body["sshkey_id"] = list(spec.ssh_key_ids)
        if spec.user_data:
            body["user_data"] = spec.user_data

        data = self._request("POST", "/instances", body)
        inst = data.get("instance", {})
        return ProvisionedInstance(
            id=inst.get("id", ""),
            region_id=inst.get("region", spec.region_id),
            plan_id=inst.get("plan", spec.plan_id),
            label=inst.get("label", spec.label),
            status=inst.get("status", "pending"),
            main_ip=inst.get("main_ip"),
            tags=tuple(inst.get("tags") or spec.tags),
            raw=inst,
        )

    def get_instance(self, instance_id: str) -> Optional[ProvisionedInstance]:
        if self.dry_run:
            return self._simulated.get(instance_id)
        try:
            data = self._request("GET", f"/instances/{instance_id}")
        except ProviderError:
            return None
        inst = data.get("instance")
        if not inst:
            return None
        return ProvisionedInstance(
            id=inst.get("id", instance_id),
            region_id=inst.get("region", ""),
            plan_id=inst.get("plan", ""),
            label=inst.get("label", ""),
            status=inst.get("status", ""),
            main_ip=inst.get("main_ip"),
            tags=tuple(inst.get("tags") or ()),
            raw=inst,
        )

    def list_instances(self, tag: Optional[str] = None) -> list[ProvisionedInstance]:
        if self.dry_run:
            vals = list(self._simulated.values())
            return [i for i in vals if tag is None or tag in i.tags]
        data = self._request("GET", "/instances?per_page=500")
        out = []
        for inst in data.get("instances", []):
            tags = tuple(inst.get("tags") or ())
            if tag is not None and tag not in tags:
                continue
            out.append(
                ProvisionedInstance(
                    id=inst.get("id", ""),
                    region_id=inst.get("region", ""),
                    plan_id=inst.get("plan", ""),
                    label=inst.get("label", ""),
                    status=inst.get("status", ""),
                    main_ip=inst.get("main_ip"),
                    tags=tags,
                    raw=inst,
                )
            )
        return out

    def destroy_instance(self, instance_id: str) -> bool:
        if self.dry_run:
            self._simulated.pop(instance_id, None)
            return True
        self._request("DELETE", f"/instances/{instance_id}")
        # Deletion is asynchronous; poll briefly so the caller can trust the
        # return value rather than discovering a ghost instance later.
        for _ in range(20):
            if self.get_instance(instance_id) is None:
                return True
            time.sleep(3)
        return self.get_instance(instance_id) is None

    def account_balance(self) -> Optional[float]:
        if self.dry_run:
            return None
        try:
            data = self._request("GET", "/account")
        except ProviderError:
            return None
        return data.get("account", {}).get("balance")

    def __repr__(self) -> str:  # pragma: no cover - display only
        # Never leak the key, even in a repr.
        return f"VultrProvider(dry_run={self.dry_run}, key={'set' if self._api_key else 'unset'})"
