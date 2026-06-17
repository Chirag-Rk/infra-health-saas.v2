import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import pandas as pd
from datetime import date

pio.templates.default = "plotly"


def fetch_assets(api_base: str) -> list:
    try:
        r = requests.get(f"{api_base}/assets/", params={"limit": 200}, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return []


def fetch_asset_detail(api_base: str, asset_id: int) -> dict:
    try:
        r = requests.get(f"{api_base}/assets/{asset_id}", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {}


def fetch_asset_history(api_base: str, asset_id: int) -> dict:
    try:
        r = requests.get(f"{api_base}/assets/{asset_id}/history", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {}


def render(api_base: str):
    st.title("🔍 Asset Explorer")
    st.caption("Browse infrastructure assets, view health details, and track lifecycle history")

    assets = fetch_assets(api_base)

    if not assets:
        st.error("⚠️ No assets found or API unavailable.")
        return

    # Asset selector
    asset_options = {f"{a['id']} — {a['asset_name']} [{a['asset_type']}]": a['id'] for a in assets}
    selected_label = st.selectbox("Select an Asset", list(asset_options.keys()))
    selected_id = asset_options[selected_label]

    detail = fetch_asset_detail(api_base, selected_id)
    history = fetch_asset_history(api_base, selected_id)

    if not detail:
        st.warning("Could not load asset details.")
        return

    st.markdown("---")

    # Asset header
    risk_emoji = {"healthy": "🟢", "warning": "🟡", "critical": "🔴"}.get(detail.get("risk_level", ""), "⚪")
    st.subheader(f"{risk_emoji} {detail['asset_name']}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Health Score", f"{detail.get('health_score', 0):.1f} / 100")
    col2.metric("Risk Level", detail.get("risk_level", "N/A").title())
    col3.metric("Status", detail.get("status", "N/A").replace("_", " ").title())
    col4.metric("Maintenance Logs", detail.get("maintenance_count", 0))

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Asset Type", detail.get("asset_type", "").replace("_", " ").title())
    col6.metric("Department", detail.get("department", "N/A"))
    col7.metric("Installation Year", detail.get("installation_year", "N/A"))
    col8.metric("Citizen Reports", detail.get("citizen_report_count", 0))

    st.markdown("---")

    col_a, col_b = st.columns([1, 1])

    with col_a:
        # Health score gauge
        hs = detail.get("health_score", 0)
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=hs,
            delta={"reference": 50, "valueformat": ".1f"},
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Health Score", "font": {"color": "#e0e0e0"}},
            number={"font": {"color": "#e0e0e0", "size": 48}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#888"},
                "bar": {"color": "#3b82f6"},
                "bgcolor": "rgba(0,0,0,0)",
                "steps": [
                    {"range": [0, 30], "color": "rgba(34,197,94,0.2)"},
                    {"range": [30, 60], "color": "rgba(234,179,8,0.2)"},
                    {"range": [60, 100], "color": "rgba(239,68,68,0.2)"},
                ],
                "threshold": {
                    "line": {"color": "white", "width": 3},
                    "thickness": 0.75,
                    "value": hs
                }
            }
        ))
        fig_g.update_layout(
            height=280, paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e0e0e0"), margin=dict(t=40, b=10, l=20, r=20)
        )
        st.plotly_chart(fig_g, use_container_width=True, theme=None)

    with col_b:
        # Age profile
        if history:
            age_profile = history.get("age_profile", {})
            if age_profile:
                st.subheader("📅 Lifecycle Profile")
                pct = age_profile.get("percent_life_used", 0)
                stage = age_profile.get("lifecycle_stage", "unknown").replace("_", " ").title()

                st.progress(pct / 100)
                st.caption(f"**{pct}%** of design life consumed — Stage: **{stage}**")

                m1, m2, m3 = st.columns(3)
                m1.metric("Age", f"{age_profile.get('current_age_years', 0)} yrs")
                m2.metric("Design Life", f"{age_profile.get('design_life_years', 0)} yrs")
                m3.metric("Remaining", f"{age_profile.get('remaining_life_years', 0)} yrs")

                stats = history.get("stats", {})
                st.markdown("**Lifecycle Summary**")
                df_stats = pd.DataFrame([{
                    "Metric": k.replace("_", " ").title(),
                    "Value": v
                } for k, v in stats.items() if k not in ("timeline_start", "timeline_end")])
                st.dataframe(df_stats, use_container_width=True, hide_index=True)

    # Connected assets
    connected_ids = detail.get("connected_asset_ids", [])
    if connected_ids:
        st.markdown("---")
        st.subheader("🔗 Connected Infrastructure")
        asset_map = {a["id"]: a for a in assets}
        conn_rows = []
        for cid in connected_ids:
            ca = asset_map.get(cid)
            if ca:
                conn_rows.append({
                    "ID": ca["id"],
                    "Asset": ca["asset_name"],
                    "Type": ca["asset_type"].replace("_", " ").title(),
                    "Risk": {"healthy": "🟢", "warning": "🟡", "critical": "🔴"}.get(ca["risk_level"], "") + " " + ca["risk_level"].title(),
                    "Health Score": ca["health_score"],
                })
        if conn_rows:
            st.dataframe(pd.DataFrame(conn_rows), use_container_width=True, hide_index=True)

    # Lifecycle Timeline
    if history and history.get("timeline"):
        st.markdown("---")
        st.subheader("⏱️ Lifecycle Timeline")

        timeline = history["timeline"]

        for event in timeline:
            severity_colors = {
                "critical": "#ef4444",
                "warning": "#eab308",
                "info": "#3b82f6",
            }
            border_color = severity_colors.get(event.get("severity", "info"), "#3b82f6")

            st.markdown(
                f"""<div style='border-left: 4px solid {border_color}; padding: 8px 12px; margin: 8px 0;
                background: rgba(255,255,255,0.03); border-radius: 0 8px 8px 0'>
                <b>{event.get("icon", "")} {event.get("date", "")} — {event.get("title", "")}</b><br>
                <small style='color:#94a3b8'>{event.get("description", "")}</small>
                </div>""",
                unsafe_allow_html=True
            )
