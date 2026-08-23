"""BharatGov Access Interactive Decision-Maker Dashboard.

Provides State-wise and Central Ministry Web Maturity Analytics:
- Comparative State Benchmarks (Accessibility, Speed, GIGW Compliance, Multilingualism)
- Feature Gap Analysis (Missing citizen features in state & central portals)
- Language & Script Trend Distribution
- Government Web Feature Blueprint & Policy Recommendations.
"""

from __future__ import annotations

import json
from pathlib import Path
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="BharatGov Access — State & Central Observatory Dashboard",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🏛️ BharatGov Access — Government Web Infrastructure Observatory")
st.caption("Empowering State & Central IT Decision Makers with Data-Driven Public Web Analytics")

# Load Latest Dataset Release
RELEASES_DIR = Path(__file__).resolve().parent.parent / "data" / "releases"


@st.cache_data
def load_latest_dataset():
    csv_files = list(RELEASES_DIR.glob("bharatgov_access_*.csv"))
    if not csv_files:
        # Fallback to resources directory
        csv_files = list((Path(__file__).resolve().parent.parent / "resources").glob("bharatgov_access_*.csv"))
    if not csv_files:
        return None
    
    latest_file = sorted(csv_files)[-1]
    df = pd.read_csv(latest_file)
    return df, latest_file.name


data = load_latest_dataset()
if not data:
    st.error("No dataset release files found in data/releases/ or resources/. Please run `scripts/run_pipeline.py` to generate the dataset.")
    st.stop()

df, file_name = data

st.sidebar.header("📌 Filter & Governance Controls")
st.sidebar.info(f"Dataset Version: **{file_name}** | Total Portals: **{len(df):,}**")

# Sidebar Filters
gov_level_filter = st.sidebar.multiselect(
    "Filter Governance Tier:",
    options=df["government_level"].unique(),
    default=df["government_level"].unique(),
)

df_filtered = df[df["government_level"].isin(gov_level_filter)]

# Tabs Interface
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 State-Wise Comparative Analytics",
    "🏛️ Central Ministries Analysis",
    "🧩 Feature Gap & GIGW Blueprint",
    "📋 Raw Dataset Explorer",
])

# Tab 1: State-Wise Comparative Analytics
with tab1:
    st.subheader("State & UT Web Maturity Benchmarks")

    states = [s for s in df_filtered["state_or_ut"].unique() if s and s != "Central Government"]
    selected_state = st.selectbox("Select State or Union Territory for Deep-Dive:", options=sorted(states))

    if selected_state:
        sdf = df_filtered[df_filtered["state_or_ut"] == selected_state]
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Portals Analyzed", f"{len(sdf):,}")
        col2.metric("Reachable Rate", f"{round((sdf['is_reachable'].sum() / len(sdf)) * 100, 1)}%")
        col3.metric("Accessibility Index", f"{round(sdf['overall_accessibility_score'].dropna().mean(), 1)} / 100")
        col4.metric("Multilingual Rate", f"{round((sdf['is_multilingual'].sum() / len(sdf)) * 100, 1)}%")

        st.markdown("---")
        st.write(f"### 🚀 Feature Penetration & Adoption in **{selected_state}**")
        
        f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns(5)
        if "has_search_bar" in sdf.columns:
            f_col1.metric("Native Search", f"{round((sdf['has_search_bar'].sum() / len(sdf)) * 100, 1)}%")
        if "has_grievance_portal" in sdf.columns:
            f_col2.metric("Grievance Link", f"{round((sdf['has_grievance_portal'].sum() / len(sdf)) * 100, 1)}%")
        if "has_payment_gateway" in sdf.columns:
            f_col3.metric("Payment Gateway", f"{round((sdf['has_payment_gateway'].sum() / len(sdf)) * 100, 1)}%")
        if "has_mobile_app_links" in sdf.columns:
            f_col4.metric("Mobile App Link", f"{round((sdf['has_mobile_app_links'].sum() / len(sdf)) * 100, 1)}%")
        if "gigw_accessibility_score" in sdf.columns:
            f_col5.metric("GIGW Toolbar Score", f"{round(sdf['gigw_accessibility_score'].dropna().mean(), 1)} / 100")

        # Comparative Bar Chart Across States
        st.write("### 🏆 Top 10 States by Web Accessibility Index")
        state_acc = df[df["state_or_ut"] != "Central Government"].groupby("state_or_ut")["overall_accessibility_score"].mean().dropna().sort_values(ascending=False).head(10)
        st.bar_chart(state_acc)

# Tab 2: Central Ministries Analysis
with tab2:
    st.subheader("Union Ministries & Apex Bodies Web Performance")
    cdf = df_filtered[df_filtered["government_level"] == "central"]

    if not cdf.empty:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Central Portals", f"{len(cdf):,}")
        c2.metric("Reachable Rate", f"{round((cdf['is_reachable'].sum() / len(cdf)) * 100, 1)}%")
        c3.metric("Avg Accessibility", f"{round(cdf['overall_accessibility_score'].dropna().mean(), 1)} / 100")
        c4.metric("Avg Performance", f"{round(cdf['overall_performance_score'].dropna().mean(), 1)} / 100")

        st.write("### Central Ministries Portal Breakdown")
        st.dataframe(cdf[["domain_name", "entity_name", "overall_accessibility_score", "overall_performance_score", "is_multilingual", "reachability_status"]])

# Tab 3: Feature Gap & GIGW Blueprint
with tab3:
    st.subheader("GIGW Guidelines & Mandatory Feature Adoption Rates")
    
    st.info("""
    **Guidelines for Indian Government Websites (GIGW)** specify mandatory features for every public service portal:
    1. Multilingual Support (Regional Language & Script)
    2. Accessibility Toolbar (Font Size Adjuster `A+ A-`, High Contrast Toggle)
    3. Skip to Main Content Link (`#main-content`)
    4. Online Grievance Redressal Integration (CPGRAMS / State Portal)
    5. Mobile App & Payment Gateway Integrations
    """)

    if "feature_richness_score" in df_filtered.columns:
        st.write("### Overall Feature Richness Score Distribution")
        st.hist_chart(df_filtered["feature_richness_score"].dropna())

# Tab 4: Raw Dataset Explorer
with tab4:
    st.subheader("Interactive Dataset Explorer")
    st.write(f"Showing **{len(df_filtered):,}** records:")
    st.dataframe(df_filtered)
