import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import pandas as pd

pio.templates.default = "plotly"


def fetch_overview(api_base: str) -> dict:
    try:
        r = requests.get(f"{api_base}/analytics/overview", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return None


def fetch_network_risk(api_base: str) -> dict:
    try:
        r = requests.get(f"{api_base}/analytics/network-risk", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def render(api_base: str):
    st.title("📊 Infrastructure Intelligence Dashboard")
    st.caption("Real-time overview of city infrastructure health, risk, and performance")

    data = fetch_overview(api_base)

    if not data:
        st.error("⚠️ Cannot connect to the API. Please start the FastAPI backend first.\n\n"
                 "Run: `uvicorn app.main:app --reload`")
        return

    summary = data.get("summary", {})

    # KPI Row
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Assets", summary.get("total_assets", 0))
    col2.metric("✅ Healthy", summary.get("healthy", 0),
                delta=f"{round(summary.get('healthy', 0) / max(summary.get('total_assets', 1), 1) * 100, 1)}%",
                delta_color="normal")
    col3.metric("⚠️ Warning", summary.get("warning", 0), delta_color="inverse")
    col4.metric("🔴 Critical", summary.get("critical", 0), delta_color="inverse")
    col5.metric("📋 Overdue Inspections", summary.get("overdue_inspections", 0), delta_color="inverse")

    st.markdown("---")

    col_a, col_b = st.columns([1, 1])

    with col_a:
        # Health distribution donut chart
        labels = ["Healthy", "Warning", "Critical"]
        values = [summary.get("healthy", 0), summary.get("warning", 0), summary.get("critical", 0)]
        colors = ["#22c55e", "#eab308", "#ef4444"]

        fig_donut = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.55,
            marker=dict(colors=colors, line=dict(color='#1e1e2e', width=2)),
            textinfo="label+percent",
            hoverinfo="label+value",
        )])
        fig_donut.update_layout(
            title="Asset Health Distribution",
            showlegend=True,
            height=320,
            margin=dict(t=50, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e0e0e0")
        )
        fig_donut.add_annotation(
            text=f"NHI<br>{summary.get('network_health_index', 0):.1f}",
            font_size=16, showarrow=False,
            font=dict(color="#e0e0e0", size=18)
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_b:
        # Asset type breakdown bar chart
        by_type = data.get("by_type", [])
        if by_type:
            df_type = pd.DataFrame(by_type)
            df_type["asset_type"] = df_type["asset_type"].str.replace("_", " ").str.title()

            fig_bar = px.bar(
                df_type,
                x="asset_type",
                y="avg_health_score",
                color="avg_health_score",
                color_continuous_scale=["#22c55e", "#eab308", "#ef4444"],
                range_color=[0, 100],
                title="Avg Health Score by Asset Type",
                labels={"asset_type": "Type", "avg_health_score": "Avg Score"},
                text="count"
            )
            fig_bar.update_traces(textposition="outside")
            fig_bar.update_layout(
                height=320,
                coloraxis_showscale=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e0e0e0"),
                margin=dict(t=50, b=10, l=10, r=10),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)", range=[0, 110])
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    col_c, col_d = st.columns([1, 1])

    with col_c:
        # Department distribution
        by_dept = data.get("by_department", [])
        if by_dept:
            df_dept = pd.DataFrame(by_dept)
            fig_dept = px.bar(
                df_dept.sort_values("count", ascending=True),
                x="count", y="department",
                orientation="h",
                title="Assets by Department",
                color="count",
                color_continuous_scale="Blues"
            )
            fig_dept.update_layout(
                height=300,
                coloraxis_showscale=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e0e0e0"),
                margin=dict(t=50, b=10, l=10, r=10),
                xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig_dept, use_container_width=True)

    with col_d:
        # Network risk cascade summary
        network_data = fetch_network_risk(api_base)
        if network_data:
            net_summary = network_data.get("summary", {})

            st.subheader("🕸️ Network Risk Analysis")
            m1, m2 = st.columns(2)
            m1.metric("Directly Critical", net_summary.get("directly_critical", 0))
            m2.metric("Cascade Affected", net_summary.get("propagation_affected", 0))

            m3, m4 = st.columns(2)
            m3.metric("Risk Escalated", net_summary.get("risk_escalated", 0))
            m4.metric("Network Health Index", f"{net_summary.get('network_health_index', 0):.1f}")

            # Mini gauge for network health
            nhi = net_summary.get("network_health_index", 0)
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=nhi,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Network Health Index", "font": {"color": "#e0e0e0"}},
                number={"font": {"color": "#e0e0e0"}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#e0e0e0"},
                    "bar": {"color": "#3b82f6"},
                    "bgcolor": "rgba(0,0,0,0)",
                    "steps": [
                        {"range": [0, 40], "color": "#ef4444"},
                        {"range": [40, 70], "color": "#eab308"},
                        {"range": [70, 100], "color": "#22c55e"},
                    ],
                }
            ))
            fig_gauge.update_layout(
                height=220,
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e0e0e0"),
                margin=dict(t=30, b=10, l=20, r=20)
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

    # Recent reports
    reports = data.get("recent_citizen_reports", [])
    if reports:
        st.markdown("---")
        st.subheader("📢 Recent Citizen Reports")
        df_reports = pd.DataFrame(reports)
        severity_map = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        df_reports["severity"] = df_reports["severity"].map(lambda s: f"{severity_map.get(s, '')} {s.title()}")
        df_reports = df_reports.rename(columns={
            "id": "ID", "asset_id": "Asset ID", "report_type": "Type",
            "severity": "Severity", "timestamp": "Reported At"
        })
        st.dataframe(df_reports[["ID", "Asset ID", "Type", "Severity", "Reported At"]], use_container_width=True)
