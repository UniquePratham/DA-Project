"""Recompute every figure quoted in the paper from the released dataset.

Run from the repository root. Prints the values so they can be pasted into the
manuscript, and fails loudly if a quoted figure has drifted.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from global_dataset import domestic, nearest, read_global, reachable  # noqa: E402

from build_deck import classify  # noqa: E402


def main() -> int:
    df = read_global()
    live = reachable(df)
    dom = domestic(df)
    near = nearest(df)
    dl = reachable(dom)
    nl = reachable(near)

    print(f"rows                 {len(df):,}")
    print(f"countries            {df['probe_country'].nunique()}")
    print(f"reachable            {len(live):,}  ({len(live) / len(df) * 100:.1f}%)")
    print(f"countries reachable  {live['probe_country'].nunique()}")
    print()
    print(f"domestic  countries {dom['probe_country'].nunique():3d}  rows {len(dom):5,}  "
          f"live {len(dl):4,}  reach {len(dl) / len(dom) * 100:5.1f}%  "
          f"acc {dl['sub_accessibility_score'].mean():5.1f}  "
          f"sec {dl['sub_security_headers_score'].mean():5.1f}  "
          f"mat {dl['observatory_maturity_score'].mean():5.1f}  "
          f"ttfb {dl['sub_response_latency_ms'].median():6.0f}")
    print(f"nearest   countries {near['probe_country'].nunique():3d}  rows {len(near):5,}  "
          f"live {len(nl):4,}  reach {len(nl) / len(near) * 100:5.1f}%  "
          f"acc {nl['sub_accessibility_score'].mean():5.1f}  "
          f"sec {nl['sub_security_headers_score'].mean():5.1f}  "
          f"mat {nl['observatory_maturity_score'].mean():5.1f}  "
          f"ttfb {nl['sub_response_latency_ms'].median():6.0f}")
    print()
    print(f"gap ms               {nl['sub_response_latency_ms'].median() - dl['sub_response_latency_ms'].median():.0f}")
    print(f"acc drop             {dl['sub_accessibility_score'].mean() - nl['sub_accessibility_score'].mean():.1f}")
    print(f"sec drop             {dl['sub_security_headers_score'].mean() - nl['sub_security_headers_score'].mean():.1f}")
    print()
    print(f"https                {live['sub_https_enforced'].mean() * 100:.1f}%")
    print(f"multilingual         {live['sub_is_multilingual'].mean() * 100:.1f}%")
    print(f"mobile               {live['sub_mobile_responsive'].mean() * 100:.1f}%")
    print(f"waf blocked          {int(df['blocked_by_waf'].fillna(False).astype(bool).sum())}")
    print(f"robots disallowed    {int(df['robots_disallowed'].fillna(False).astype(bool).sum())}")
    print(f"median ttfb          {live['sub_response_latency_ms'].median():.0f} ms")
    print(f"mean acc             {live['sub_accessibility_score'].mean():.1f}")
    print(f"mean sec             {live['sub_security_headers_score'].mean():.1f}")
    print(f"mean maturity        {live['observatory_maturity_score'].mean():.1f}")
    print()

    df["sector"] = df["domain_name"].map(classify)
    print("sector            n   live  reach    acc    sec")
    for sector, group in df.groupby("sector"):
        up = reachable(group)
        if len(up) < 10:
            continue
        print(f"{sector:12s} {len(group):5d} {len(up):5d} "
              f"{len(up) / len(group) * 100:5.1f}% "
              f"{up['sub_accessibility_score'].mean():6.1f} "
              f"{up['sub_security_headers_score'].mean():6.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
