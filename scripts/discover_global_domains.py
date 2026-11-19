"""Discover real government domains per country from Certificate Transparency.

This is the same method used for India, applied globally. Certificate
Transparency is a public append-only log of every TLS certificate ever issued,
so a domain found here provably existed and served HTTPS at some point. That is
an auditable observation, not a guess.

Each country has a government TLD convention. We query crt.sh for that
namespace and keep only hostnames that match it, so a `.gov` query cannot leak
a `.com` domain into the US registry.

Nothing is invented. A domain enters the registry because it appeared in a real
certificate.
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "data" / "fixtures" / "global_domains.json"

UA = "Mozilla/5.0 (compatible; CivicWebObservatory/1.0; research)"

#: Country -> the TLD namespaces its government actually uses.
#:
#: Only namespaces that are genuinely government-restricted are listed. A bare
#: ccTLD (``.fr``, ``.de``, ``.se``) is deliberately NOT used, because it returns
#: the entire commercial internet of that country and would make the registry
#: meaningless.
#:
#: Where a country has no restricted namespace, it is absent from this table
#: rather than approximated. Germany is the clearest example: federal sites use
#: ``bund.de``, but states and municipalities use plain ``.de``
#: (``berlin.de``, ``muenchen.de``), so a complete German registry needs a
#: national index, not a TLD query. We record that as partial coverage instead
#: of pretending otherwise.
GOV_TLDS: dict[str, list[str]] = {
    # --- restricted government namespaces, safe to query ---
    "IN": ["gov.in", "nic.in", "ac.in", "res.in", "edu.in"],
    "US": ["gov"],
    "GB": ["gov.uk", "nhs.uk", "police.uk", "parliament.uk", "mod.uk", "judiciary.uk"],
    "CA": ["gc.ca", "canada.ca"],
    "AU": ["gov.au", "edu.au"],
    "DE": ["bund.de", "bundestag.de"],
    "FR": ["gouv.fr"],
    "JP": ["go.jp", "lg.jp", "ac.jp"],
    "BR": ["gov.br", "leg.br", "jus.br", "mp.br"],
    "ZA": ["gov.za", "ac.za"],
    "SG": ["gov.sg", "edu.sg"],
    "NL": ["overheid.nl"],
    "ES": ["gob.es"],
    "IT": ["gov.it", "istruzione.it"],
    "PL": ["gov.pl"],
    "KR": ["go.kr", "or.kr", "ac.kr", "mil.kr"],
    "MX": ["gob.mx", "edu.mx"],
    "CL": ["gob.cl"],
    "IL": ["gov.il", "ac.il"],
    "NZ": ["govt.nz", "ac.nz"],
    "IE": ["gov.ie"],
    "AT": ["gv.at"],
    "BE": ["belgium.be", "fgov.be", "vlaanderen.be", "wallonie.be"],
    "CH": ["admin.ch"],
    "PT": ["gov.pt"],
    "GR": ["gov.gr"],
    "CZ": ["gov.cz"],
    "HU": ["gov.hu"],
    "RO": ["gov.ro"],
    "BG": ["government.bg"],
    "HR": ["gov.hr"],
    "SK": ["gov.sk"],
    "SI": ["gov.si"],
    "LT": ["lrv.lt"],
    "LV": ["gov.lv"],
    "EE": ["riik.ee"],
    "AR": ["gob.ar", "gov.ar"],
    "CO": ["gov.co"],
    "PE": ["gob.pe"],
    "UY": ["gub.uy"],
    "EC": ["gob.ec"],
    "NG": ["gov.ng"],
    "KE": ["go.ke"],
    "GH": ["gov.gh"],
    "EG": ["gov.eg"],
    "MA": ["gov.ma"],
    "TN": ["gov.tn"],
    "DZ": ["gov.dz"],
    "ET": ["gov.et"],
    "TZ": ["go.tz"],
    "UG": ["go.ug"],
    "ZW": ["gov.zw"],
    "ZM": ["gov.zm"],
    "BW": ["gov.bw"],
    "NA": ["gov.na"],
    "MU": ["govmu.org"],
    "ID": ["go.id", "ac.id"],
    "PH": ["gov.ph", "edu.ph"],
    "MY": ["gov.my", "edu.my"],
    "TH": ["go.th", "ac.th"],
    "VN": ["gov.vn", "edu.vn"],
    "PK": ["gov.pk", "edu.pk"],
    "BD": ["gov.bd", "edu.bd"],
    "LK": ["gov.lk", "ac.lk"],
    "NP": ["gov.np", "edu.np"],
    "AE": ["gov.ae", "ac.ae"],
    "SA": ["gov.sa", "edu.sa"],
    "QA": ["gov.qa"],
    "KW": ["gov.kw"],
    "BH": ["gov.bh"],
    "OM": ["gov.om"],
    "JO": ["gov.jo"],
    "LB": ["gov.lb"],
    "TR": ["gov.tr", "edu.tr"],
    "UA": ["gov.ua"],
    "RU": ["gov.ru"],
    "CN": ["gov.cn", "edu.cn"],
    "TW": ["gov.tw", "edu.tw"],
    "HK": ["gov.hk"],
    "MO": ["gov.mo"],
    "MN": ["gov.mn"],
    "KZ": ["gov.kz"],
    "UZ": ["gov.uz"],
    "AZ": ["gov.az"],
    "GE": ["gov.ge"],
    "AM": ["gov.am"],
    "IS": ["gov.is"],
    "LU": ["gouvernement.lu"],
    "MT": ["gov.mt"],
    "CY": ["gov.cy"],
    "AL": ["gov.al"],
    "RS": ["gov.rs"],
    "BA": ["gov.ba"],
    "MK": ["gov.mk"],
    "ME": ["gov.me"],
    "MD": ["gov.md"],
    "BY": ["gov.by"],
}

#: Countries where the TLD approach cannot give complete coverage, with the
#: reason. Recorded so the dashboard can say "partial" rather than implying a
#: full census.
PARTIAL_COVERAGE: dict[str, str] = {
    "DE": (
        "Federal sites use bund.de, but states and municipalities use plain .de "
        "(berlin.de, muenchen.de). A complete registry needs a national index."
    ),
    "FR": (
        "Central government uses gouv.fr, but local authorities use plain .fr. "
        "Coverage is central-government only."
    ),
    "US": (
        "The .gov namespace is complete for federal and state government, but "
        "some public bodies use .org or .us."
    ),
    "CH": (
        "admin.ch covers the federal administration; cantons use their own "
        "domains such as zh.ch."
    ),
    "AT": (
        "gv.at covers federal and state government; some municipalities use "
        "plain .at."
    ),
}

#: Substrings that mark a host as internal, test, or otherwise not a public
#: portal. Certificate Transparency logs certificates for machines that never
#: face the public, so these must be filtered out.
NON_PUBLIC_MARKERS = (
    "intranet",
    "internal",
    "localhost",
    "staging",
    "stage.",
    "test.",
    "-test",
    "test-",
    "dev.",
    "-dev",
    "dev-",
    "qa.",
    "-qa",
    "uat.",
    "-uat",
    "preprod",
    "pre-prod",
    "sandbox",
    "admin.",
    "-admin",
    "vpn",
    "proxy",
    "mail.",
    "smtp",
    "imap",
    "pop3",
    "ldap",
    "adfs",
    "autodiscover",
    "exchange",
    "owa.",
    "remote.",
    "citrix",
    "rdweb",
    "jump",
    "bastion",
    "backup",
    "db.",
    "-db",
    "sql",
    "monitor",
    "grafana",
    "prometheus",
    "kibana",
    "jenkins",
    "gitlab",
    "git.",
    "svn",
    "nexus",
    "artifactory",
    "docker",
    "registry.",
    "k8s",
    "kubernetes",
    "api-internal",
    "corp",
    "lan.",
    "dmz",
)


def is_public_portal(host: str) -> bool:
    """False for hosts that look internal, test, or infrastructural."""
    h = host.lower()
    return not any(marker in h for marker in NON_PUBLIC_MARKERS)

HOST_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+$")


def norm(host: str) -> str:
    host = host.lower().strip().rstrip(".")
    if host.startswith("*."):
        host = host[2:]
    if host.startswith("www."):
        host = host[4:]
    return host


def matches_tld(host: str, tld: str) -> bool:
    """True when the host is inside the given government namespace."""
    return host == tld or host.endswith("." + tld)


def fetch_ct(namespace: str, attempts: int = 3) -> list[dict]:
    url = f"https://crt.sh/?q=%25.{namespace}&output=json"
    for i in range(attempts):
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=240)
            if r.status_code == 200 and r.text.strip().startswith("["):
                return r.json()
            print(f"      {namespace}: HTTP {r.status_code}", flush=True)
        except Exception as exc:  # noqa: BLE001
            print(f"      {namespace}: {type(exc).__name__}", flush=True)
        time.sleep(6 * (i + 1))
    return []


def main() -> int:
    only = sys.argv[1].split(",") if len(sys.argv) > 1 else None
    targets = {k: v for k, v in GOV_TLDS.items() if not only or k in only}

    existing: dict[str, dict] = {}
    if OUT.exists():
        for r in json.loads(OUT.read_text(encoding="utf-8")):
            existing[r["domain_name"]] = r

    print(f"discovering for {len(targets)} countries")
    print(f"already have {len(existing)} domains\n")

    for country, tlds in targets.items():
        before = len(existing)
        for tld in dict.fromkeys(tlds):  # dedupe while preserving order
            certs = fetch_ct(tld)
            if not certs:
                continue
            for c in certs:
                for field in ("name_value", "common_name"):
                    for raw in str(c.get(field, "")).split("\n"):
                        h = norm(raw)
                        if not h or not HOST_RE.match(h) or len(h) > 100:
                            continue
                        if not matches_tld(h, tld):
                            continue
                        if not is_public_portal(h):
                            continue
                        if h not in existing:
                            existing[h] = {
                                "domain_name": h,
                                "country": country,
                                "tld": tld,
                                "first_seen": c.get("not_before", ""),
                                "source": "certificate_transparency",
                            }
            print(f"  {country} {tld:16s} {len(certs):5d} certs", flush=True)

        print(f"  -> {country}: +{len(existing) - before} new (total {len(existing)})\n", flush=True)

        # Persist after each country so a crash does not lose the work.
        rows = sorted(existing.values(), key=lambda r: r["domain_name"])
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")

    rows = sorted(existing.values(), key=lambda r: r["domain_name"])
    from collections import Counter

    by_country = Counter(r["country"] for r in rows)
    print(f"total domains: {len(rows)}")
    print(f"countries: {len(by_country)}")
    for c, n in by_country.most_common():
        print(f"  {c}: {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
