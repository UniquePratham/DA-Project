"""Validate and clean the global domain registry.

Certificate Transparency is a log of every certificate ever issued, so a raw
query returns three kinds of noise that must be removed before the registry can
be called a government registry:

1. **Wrong-namespace contamination.** An earlier run queried bare ccTLDs
   (``.fr``, ``.se``), which returned commercial sites. Every domain is now
   re-checked against the country's restricted namespace.
2. **Internal and test hosts.** ``intranet``, ``test``, ``staging``, ``admin``,
   ``mail``, ``vpn`` and similar. These are machines, not portals.
3. **Infrastructure subdomains.** ``autodiscover``, ``smtp``, ``cpanel``,
   ``webdisk``, ``owa``. Same problem.

The cleaner is deliberately strict: it would rather drop a real portal than
keep a commercial site, because a false positive corrupts every average
downstream while a false negative only shrinks the sample.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import importlib.util

spec = importlib.util.spec_from_file_location(
    "discover", REPO / "scripts" / "discover_global_domains.py"
)
discover = importlib.util.module_from_spec(spec)
spec.loader.exec_module(discover)

REGISTRY = REPO / "data" / "fixtures" / "global_domains.json"

#: Additional infrastructure markers found by inspecting real output.
EXTRA_INFRA = (
    "autodiscover",
    "webdisk",
    "cpanel",
    "whm",
    "cpcalendars",
    "cpcontacts",
    "mail.",
    "smtp",
    "imap",
    "pop.",
    "webmail",
    "owa.",
    "exchange",
    "lyncdiscover",
    "sip.",
    "msoid",
    "enterpriseregistration",
    "enterpriseenrollment",
    "preview",
    "valid.",
    "-valid",
    "acc.",
    "acceptance",
    "recette",
    "preprod",
    "qualif",
    "demo.",
    "-demo",
    "old.",
    "-old",
    "legacy",
    "v1.",
    "v2.",
    "beta.",
    "-beta",
    "alpha.",
    "temp.",
    "-temp",
    "tmp.",
    "backup",
    "bak.",
    "archive",
    "mirror",
    "cdn.",
    "static.",
    "assets.",
    "img.",
    "images.",
    "media.",
    "files.",
    "download",
    "ftp.",
    "sftp",
    "ns1",
    "ns2",
    "dns",
    "mx.",
    "relay",
    "gateway",
    "gw.",
    "router",
    "switch",
    "fw.",
    "firewall",
    "waf.",
    "lb.",
    "load",
    "cluster",
    "node",
    "server",
    "host",
    "vm.",
    "srv",
    "app-",
    "-app",
    "api-",
    "-api",
    "internal",
    "corp",
    "office",
    "staff",
    "employee",
    "hr.",
    "payroll",
    "erp",
    "crm",
    "jira",
    "confluence",
    "sharepoint",
    "teams",
    "zoom",
    "meet.",
    "webex",
    "vpn",
    "remote",
    "rdp",
    "ssh",
    "jump",
    "bastion",
    "proxy",
    "squid",
    "cache",
    "redis",
    "mongo",
    "mysql",
    "postgres",
    "oracle",
    "sap",
    "erp-",
    "sso",
    "idp",
    "auth",
    "login",
    "signin",
    "oauth",
    "saml",
    "adfs",
    "ldap",
    "dc.",
    "dc1",
    "dc2",
    "ad.",
    "domain",
    "print",
    "scan",
    "fax",
    "voip",
    "pbx",
    "camera",
    "cctv",
    "iot",
    "sensor",
    "monitor",
    "nagios",
    "zabbix",
    "grafana",
    "kibana",
    "elastic",
    "splunk",
    "log.",
    "logs.",
    "syslog",
    "metrics",
    "prometheus",
    "jenkins",
    "gitlab",
    "github",
    "bitbucket",
    "svn",
    "nexus",
    "artifactory",
    "docker",
    "k8s",
    "kube",
    "openshift",
    "rancher",
    "terraform",
    "ansible",
    "puppet",
    "chef",
    "salt",
    "vagrant",
    "packer",
)

#: Markers that must match a whole label. Derived from EXTRA_INFRA by stripping
#: the trailing dot some entries carry, so "ad." becomes the label "ad" and no
#: longer matches "saniDAD".
EXTRA_INFRA_LABELS = {
    m.rstrip(".") for m in EXTRA_INFRA if not m.endswith("-") and "." not in m.rstrip(".")
}

#: Markers that are prefixes, e.g. "app-" or "api-".
EXTRA_INFRA_PREFIXES = tuple(m for m in EXTRA_INFRA if m.endswith("-"))


def is_clean(host: str, country: str) -> tuple[bool, str]:
    """Return (keep, reason). Reason is empty when kept."""
    h = host.lower()
    labels = h.split(".")

    # 1. Must be inside the country's restricted government namespace.
    tlds = discover.GOV_TLDS.get(country, [])
    if not tlds:
        return False, "no restricted namespace for country"
    if not any(discover.matches_tld(h, t) for t in tlds):
        return False, "outside government namespace"

    # 2. Must not look internal or infrastructural.
    if not discover.is_public_portal(h):
        return False, "internal or test host"

    # 3. Infrastructure markers are matched against whole labels, not as
    #    substrings. Substring matching produced false positives: the marker
    #    "ad." matched "saniDAD.gob.es", rejecting every Spanish health domain.
    for label in labels[:-2]:  # skip the namespace itself
        if label in EXTRA_INFRA_LABELS:
            return False, "infrastructure host"
        if any(label.startswith(m) for m in EXTRA_INFRA_PREFIXES):
            return False, "infrastructure host"

    # 4. A hostname with more than four labels is almost always a machine.
    if h.count(".") > 3:
        return False, "too many labels"

    # 5. Reject anything with a numeric-only first label (IP-like or hashed).
    first = labels[0]
    if first.isdigit():
        return False, "numeric label"

    # 6. Reject labels that look like machine names.
    for label in labels[:-2]:
        if len(label) > 20:
            return False, "machine-like label"
        digits = sum(c.isdigit() for c in label)
        if digits and digits / max(1, len(label)) > 0.4:
            return False, "machine-like label"
        if any(tok in label for tok in ("pool", "node", "srv", "host", "vm")):
            return False, "machine-like label"

    return True, ""


def main() -> int:
    raw = json.loads(REGISTRY.read_text(encoding="utf-8"))
    print(f"raw registry: {len(raw)} domains\n")

    kept: list[dict] = []
    dropped: Counter = Counter()
    examples: dict[str, list[str]] = {}

    for r in raw:
        host = r["domain_name"]
        country = r["country"]
        ok, reason = is_clean(host, country)
        if ok:
            kept.append(r)
        else:
            dropped[reason] += 1
            examples.setdefault(reason, []).append(host)

    print(f"kept   : {len(kept)}")
    print(f"dropped: {len(raw) - len(kept)}\n")
    for reason, n in dropped.most_common():
        print(f"  {reason:32s} {n:6d}  e.g. {examples[reason][:2]}")

    by_country = Counter(r["country"] for r in kept)
    print(f"\ncountries: {len(by_country)}")
    for c, n in by_country.most_common():
        print(f"  {c}: {n}")

    REGISTRY.write_text(
        json.dumps(sorted(kept, key=lambda r: r["domain_name"]), indent=1, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\nwrote {len(kept)} clean domains to {REGISTRY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
