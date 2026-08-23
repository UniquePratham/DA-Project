"""BharatGov Access State and Central Benchmark Analysis Engine.

Computes state-by-state and central ministry comparative analytics:
- State Web Accessibility Index (0 - 100)
- GIGW Compliance Adoption Rate (%)
- Multilingual Adoption Rate (%)
- Feature Richness Index (0 - 100)
- Core Web Vitals Latency & LCP Trends
- Recommended Website Feature Blueprint for State & Central IT Decision Makers.
"""

from __future__ import annotations

from typing import List, Dict, Any
from collections import defaultdict
import pandas as pd


class StateCentralBenchmarkEngine:
    """Computes state-level and central-level web maturity benchmarks for government decision makers."""

    @classmethod
    def compute_benchmarks(cls, website_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not website_rows:
            return {"states": {}, "central": {}, "national_summary": {}}

        df = pd.DataFrame(website_rows)

        # 1. State-Wise Analysis
        state_benchmarks: Dict[str, Dict[str, Any]] = {}
        states = [s for s in df["state_or_ut"].unique() if s and s != "Central Government"]

        for state in states:
            sdf = df[df["state_or_ut"] == state]
            total_sites = len(sdf)
            reachable_sites = len(sdf[sdf["is_reachable"] == True])

            avg_acc = round(sdf["overall_accessibility_score"].dropna().mean(), 1) if not sdf["overall_accessibility_score"].dropna().empty else 0.0
            avg_perf = round(sdf["overall_performance_score"].dropna().mean(), 1) if not sdf["overall_performance_score"].dropna().empty else 0.0
            gigw_score = round(sdf["gigw_accessibility_score"].dropna().mean(), 1) if "gigw_accessibility_score" in sdf.columns and not sdf["gigw_accessibility_score"].dropna().empty else 0.0
            
            multilingual_pct = round((sdf["is_multilingual"].sum() / total_sites) * 100.0, 1) if total_sites > 0 else 0.0
            grievance_pct = round((sdf["has_grievance_portal"].sum() / total_sites) * 100.0, 1) if "has_grievance_portal" in sdf.columns and total_sites > 0 else 0.0
            payment_pct = round((sdf["has_payment_gateway"].sum() / total_sites) * 100.0, 1) if "has_payment_gateway" in sdf.columns and total_sites > 0 else 0.0
            mobile_app_pct = round((sdf["has_mobile_app_links"].sum() / total_sites) * 100.0, 1) if "has_mobile_app_links" in sdf.columns and total_sites > 0 else 0.0
            search_pct = round((sdf["has_search_bar"].sum() / total_sites) * 100.0, 1) if "has_search_bar" in sdf.columns and total_sites > 0 else 0.0

            # Language breakdown
            langs = sdf["primary_language"].value_counts().to_dict()

            state_benchmarks[state] = {
                "total_websites": total_sites,
                "reachable_websites": reachable_sites,
                "reachability_rate_pct": round((reachable_sites / total_sites) * 100.0, 1) if total_sites > 0 else 0.0,
                "state_accessibility_index": avg_acc,
                "state_performance_index": avg_perf,
                "gigw_compliance_score": gigw_score,
                "multilingual_adoption_pct": multilingual_pct,
                "grievance_portal_adoption_pct": grievance_pct,
                "payment_gateway_adoption_pct": payment_pct,
                "mobile_app_integration_pct": mobile_app_pct,
                "search_functionality_pct": search_pct,
                "language_distribution": langs,
            }

        # 2. Central Government Analysis
        cdf = df[df["state_or_ut"] == "Central Government"]
        c_total = len(cdf)
        c_reachable = len(cdf[cdf["is_reachable"] == True])
        
        central_benchmarks = {
            "total_websites": c_total,
            "reachable_websites": c_reachable,
            "reachability_rate_pct": round((c_reachable / c_total) * 100.0, 1) if c_total > 0 else 0.0,
            "central_accessibility_index": round(cdf["overall_accessibility_score"].dropna().mean(), 1) if not cdf["overall_accessibility_score"].dropna().empty else 0.0,
            "central_performance_index": round(cdf["overall_performance_score"].dropna().mean(), 1) if not cdf["overall_performance_score"].dropna().empty else 0.0,
            "gigw_compliance_score": round(cdf["gigw_accessibility_score"].dropna().mean(), 1) if "gigw_accessibility_score" in cdf.columns and not cdf["gigw_accessibility_score"].dropna().empty else 0.0,
            "multilingual_adoption_pct": round((cdf["is_multilingual"].sum() / c_total) * 100.0, 1) if c_total > 0 else 0.0,
            "grievance_portal_adoption_pct": round((cdf["has_grievance_portal"].sum() / c_total) * 100.0, 1) if "has_grievance_portal" in cdf.columns and c_total > 0 else 0.0,
            "payment_gateway_adoption_pct": round((cdf["has_payment_gateway"].sum() / c_total) * 100.0, 1) if "has_payment_gateway" in cdf.columns and c_total > 0 else 0.0,
        }

        # 3. National Summary Benchmark
        national_summary = {
            "total_websites_analyzed": len(df),
            "national_accessibility_index": round(df["overall_accessibility_score"].dropna().mean(), 1) if not df["overall_accessibility_score"].dropna().empty else 0.0,
            "national_performance_index": round(df["overall_performance_score"].dropna().mean(), 1) if not df["overall_performance_score"].dropna().empty else 0.0,
            "national_multilingual_pct": round((df["is_multilingual"].sum() / len(df)) * 100.0, 1),
            "top_performing_states_by_accessibility": sorted(
                state_benchmarks.items(),
                key=lambda item: item[1]["state_accessibility_index"],
                reverse=True
            )[:5],
        }

        return {
            "states": state_benchmarks,
            "central": central_benchmarks,
            "national_summary": national_summary,
        }
