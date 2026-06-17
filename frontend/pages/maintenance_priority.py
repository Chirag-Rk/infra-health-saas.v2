import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

pio.templates.default = "plotly"


def fetch_priority(api_base: str) -> list:
    try:
        r = requests.get(f"{api_base}/maintenance/priority", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return []


def fetch_network_risk(api_base: str) -> dict:
    try:
        r = requests.get(f"{api_base}/analytics/network-risk", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {}


ACTION_STYLES = {
    "EMERGENCY": ("🚨", "#ef4444"),
    "URGENT": ("⚠️", "#f97316"),
    "HIGH PRIORITY": ("🔶", "#eab308"),
    "SCHEDULE": ("📋", "#3b82f6"),
    "ROUTINE": ("✅", "#22c55e"),
    "MONITOR": ("👁️", "#8b5cf6"),
}


def get_action_style(action: str):
    for key, (icon, color) in ACTION_STYLES.items():
        if action.startswith(key):
            return icon, color
    return "📌", "#6b7280"


def render(api_base: str):
    st.title("🔧 Maintenance Priority Intelligence")
    st.caption("AI-ranked asset maintenance queue based on risk, population impact, and infrastructure importance")

    priority_list = fetch_priority(api_base)
    network = fetch_network_risk(api_base)

    if not priority_list:
        st.error("⚠️ Could not load priority data. Is the API running?")
        return

    # Network cascade summary
    if network:
        net_summary = network.get("summary", {})
        st.info(
            f"🕸️ **Network Risk:** {net_summary.get('directly_critical', 0)} directly critical assets "
            f"are causing risk cascade to {net_summary.get('propagation_affected', 0)} connected assets. "
            f"Network Health Index: **{net_summary.get('network_health_index', 0):.1f}/100**"
        )

    st.markdown("---")

    # Filter controls
    col1, col2 = st.columns(2)
    with col1:
        show_count = st.slider("Show top N assets", min_value=5, max_value=len(priority_list), value=min(15, len(priority_list)))
    with col2:
        risk_filter = st.multiselect("Filter by Risk Level", ["healthy", "warning", "critical"],
                                     default=["warning", "critical"])

    filtered = [p for p in priority_list if not risk_filter or p["risk_level"] in risk_filter]
    filtered = filtered[:show_count]

    st.markdown("---")
    st.subheader(f"🏆 Top {len(filtered)} Priority Assets")

    # Priority bar chart
    df = pd.DataFrame(filtered)
    color_map = {"healthy": "#22c55e", "warning": "#eab308", "critical": "#ef4444"}
    df["color"] = df["risk_level"].map(color_map)

    fig_bar = go.Figure()
    for rl in ["critical", "warning", "healthy"]:
        subset = df[df["risk_level"] == rl]
        if not subset.empty:
            fig_bar.add_trace(go.Bar(
                x=subset["asset_name"],
                y=subset["priority_score"],
                name=rl.title(),
                marker_color=color_map[rl],
                text=subset["priority_score"].apply(lambda s: f"{s:.1f}"),
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Priority: %{y:.1f}<extra></extra>"
            ))

    fig_bar.update_layout(
        barmode="overlay",
        title="Priority Score by Asset",
        xaxis_tickangle=-35,
        yaxis=dict(title="Priority Score", range=[0, 115], showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e0e0e0"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        height=360,
        margin=dict(t=50, b=100, l=20, r=20)
    )
    st.plotly_chart(fig_bar, use_container_width=True, theme=None)

    st.markdown("---")
    st.subheader("📋 Priority Queue")

    # Render styled priority cards
    for item in filtered:
        icon, color = get_action_style(item.get("recommended_action", ""))
        risk_badge = {"healthy": "🟢 Healthy", "warning": "🟡 Warning", "critical": "🔴 Critical"}.get(
            item["risk_level"], item["risk_level"]
        )

        with st.container():
            st.markdown(
                f"""
                <div style='border: 1px solid {color}33; border-left: 5px solid {color};
                     padding: 14px 16px; margin: 8px 0; border-radius: 0 8px 8px 0;
                     background: rgba(255,255,255,0.02)'>
                    <div style='display:flex; justify-content:space-between; align-items:center'>
                        <span style='font-size:1.1rem; font-weight:bold; color:#e0e0e0'>
                            #{item['rank']} &nbsp; {item['asset_name']}
                        </span>
                        <span style='background:{color}22; color:{color}; padding:4px 10px;
                               border-radius:20px; font-size:0.85rem; border: 1px solid {color}44'>
                            {icon} {item['recommended_action'].split(':')[0]}
                        </span>
                    </div>
                    <div style='margin-top:8px; color:#94a3b8; font-size:0.9rem'>
                        <b>Type:</b> {item['asset_type'].replace('_',' ').title()} &nbsp;|&nbsp;
                        <b>Dept:</b> {item['department']} &nbsp;|&nbsp;
                        <b>Risk:</b> {risk_badge} &nbsp;|&nbsp;
                        <b>Health:</b> {item['health_score']:.1f} &nbsp;|&nbsp;
                        <b>Priority Score:</b> <span style='color:{color}; font-weight:bold'>{item['priority_score']:.1f}</span>
                    </div>
                    <div style='margin-top:6px; color:#64748b; font-size:0.85rem'>
                        📌 {item['recommended_action']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("---")

    # Full data table
    with st.expander("📊 View Full Priority Table"):
        display_df = pd.DataFrame(priority_list)
        display_df["risk_level"] = display_df["risk_level"].map(
            {"healthy": "🟢 Healthy", "warning": "🟡 Warning", "critical": "🔴 Critical"}
        )
        display_df = display_df.rename(columns={
            "rank": "Rank", "asset_name": "Asset", "asset_type": "Type",
            "risk_level": "Risk", "health_score": "Health Score",
            "priority_score": "Priority Score", "recommended_action": "Action",
            "department": "Dept"
        })
        st.dataframe(
            display_df[["Rank", "Asset", "Type", "Risk", "Health Score", "Priority Score", "Action", "Dept"]],
            use_container_width=True,
            hide_index=True
        )
