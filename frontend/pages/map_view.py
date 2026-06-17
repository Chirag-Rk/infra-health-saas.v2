import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
import json


def fetch_map_data(api_base: str, risk_level=None, asset_type=None) -> dict:
    params = {}
    if risk_level and risk_level != "All":
        params["risk_level"] = risk_level.lower()
    if asset_type and asset_type != "All":
        params["asset_type"] = asset_type.lower().replace(" ", "_")
    try:
        r = requests.get(f"{api_base}/map/assets", params=params, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def fetch_connections(api_base: str) -> dict:
    try:
        r = requests.get(f"{api_base}/map/connections", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


RISK_COLORS = {
    "healthy": [34, 197, 94, 220],
    "warning": [234, 179, 8, 220],
    "critical": [239, 68, 68, 220],
}

TYPE_ICONS = {
    "bridge": "🌉",
    "road": "🛣️",
    "pipeline": "🔧",
    "drainage": "💧",
    "street_light": "💡",
    "public_facility": "🏛️",
}


def render(api_base: str):
    st.title("🗺️ Geospatial Infrastructure Map")
    st.caption("Interactive map of all city infrastructure assets, color-coded by risk level")

    col_filters = st.columns(3)
    with col_filters[0]:
        risk_filter = st.selectbox("Filter by Risk Level", ["All", "Healthy", "Warning", "Critical"])
    with col_filters[1]:
        type_filter = st.selectbox("Filter by Asset Type", [
            "All", "Bridge", "Road", "Pipeline", "Drainage", "Street Light", "Public Facility"
        ])
    with col_filters[2]:
        show_connections = st.checkbox("Show Connections", value=True)

    data = fetch_map_data(api_base, risk_filter, type_filter)

    if not data:
        st.error("⚠️ Cannot connect to API. Start the backend first.")
        return

    geojson = data.get("geojson", {})
    bounds = data.get("bounds", {})
    features = geojson.get("features", [])

    if not features:
        st.warning("No assets found with the selected filters.")
        return

    # Build flat list for pydeck
    rows = []
    for feat in features:
        props = feat["properties"]
        coords = feat["geometry"]["coordinates"]
        rl = props.get("risk_level", "healthy")
        rows.append({
            "lon": coords[0],
            "lat": coords[1],
            "asset_name": props.get("asset_name", ""),
            "asset_type": props.get("asset_type", ""),
            "health_score": props.get("health_score", 0),
            "risk_level": rl,
            "department": props.get("department", ""),
            "installation_year": props.get("installation_year", 0),
            "r": RISK_COLORS.get(rl, [100, 100, 100, 200])[0],
            "g": RISK_COLORS.get(rl, [100, 100, 100, 200])[1],
            "b": RISK_COLORS.get(rl, [100, 100, 100, 200])[2],
            "a": RISK_COLORS.get(rl, [100, 100, 100, 200])[3],
        })

    df = pd.DataFrame(rows)

    center_lat = bounds.get("center_lat", 40.71)
    center_lon = bounds.get("center_lon", -74.01)

    # Scatter layer for assets
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["lon", "lat"],
        get_fill_color=["r", "g", "b", "a"],
        get_radius=120,
        radius_min_pixels=6,
        radius_max_pixels=20,
        pickable=True,
        auto_highlight=True,
    )

    layers = [scatter_layer]

    # Connection lines
    if show_connections:
        conn_data = fetch_connections(api_base)
        if conn_data and conn_data.get("connections"):
            conn_rows = conn_data["connections"]
            conn_df = pd.DataFrame(conn_rows)
            conn_layer = pdk.Layer(
                "LineLayer",
                data=conn_df,
                get_source_position=["from_lon", "from_lat"],
                get_target_position=["to_lon", "to_lat"],
                get_color=[100, 150, 255, 120],
                get_width=3,
                pickable=False,
            )
            layers.append(conn_layer)

    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=12,
        pitch=0,
    )

    tooltip = {
        "html": """
        <div style='background:#1e1e2e;color:#e0e0e0;padding:10px;border-radius:8px;font-family:sans-serif'>
            <b style='font-size:14px'>{asset_name}</b><br>
            <span style='color:#94a3b8'>Type:</span> {asset_type}<br>
            <span style='color:#94a3b8'>Risk:</span> {risk_level}<br>
            <span style='color:#94a3b8'>Health Score:</span> {health_score}<br>
            <span style='color:#94a3b8'>Department:</span> {department}<br>
            <span style='color:#94a3b8'>Year:</span> {installation_year}
        </div>
        """,
        "style": {"backgroundColor": "transparent"}
    }

    deck = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="mapbox://styles/mapbox/dark-v10",
    )

    st.pydeck_chart(deck)

    # Legend
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    col1.markdown("🟢 **Healthy** (Score 0–30)")
    col2.markdown("🟡 **Warning** (Score 31–60)")
    col3.markdown("🔴 **Critical** (Score 61–100)")
    col4.markdown(f"**Total shown:** {len(features)} assets")

    # Asset table below map
    st.markdown("---")
    st.subheader("Asset Details")
    display_df = df[["asset_name", "asset_type", "risk_level", "health_score", "department", "installation_year"]].copy()
    display_df.columns = ["Asset Name", "Type", "Risk Level", "Health Score", "Department", "Year"]
    display_df["Type"] = display_df["Type"].apply(lambda t: f"{TYPE_ICONS.get(t, '')} {t.replace('_', ' ').title()}")
    display_df["Risk Level"] = display_df["Risk Level"].apply(
        lambda r: {"healthy": "🟢 Healthy", "warning": "🟡 Warning", "critical": "🔴 Critical"}.get(r, r)
    )
    st.dataframe(display_df.sort_values("Health Score", ascending=False), use_container_width=True)
