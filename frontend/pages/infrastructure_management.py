import streamlit as st
import requests

def render(api_base: str):
    st.title("🏗️ Infrastructure Management")
    st.caption("Admin control panel for adding, updating, and removing infrastructure assets.")

    # Fetch data
    try:
        r = requests.get(f"{api_base}/assets/", params={"limit": 1000}, timeout=5)
        assets = r.json() if r.status_code == 200 else []
    except Exception as e:
        assets = []
        st.error(f"Cannot connect to backend API: {e}")
    
    # Statistics
    total = len(assets)
    roads = sum(1 for a in assets if a.get('asset_type') == 'road')
    utilities = sum(1 for a in assets if a.get('asset_type') in ['pipeline', 'drainage', 'street_light'])
    facilities = sum(1 for a in assets if a.get('asset_type') == 'public_facility')

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Infrastructure", total)
    col2.metric("Roads", roads)
    col3.metric("Utilities", utilities)
    col4.metric("Facilities", facilities)

    st.markdown("---")
    st.subheader("➕ Add New Infrastructure")
    
    with st.expander("Create New Asset", expanded=False):
        with st.form("add_asset_form", clear_on_submit=False):
            cols = st.columns(2)
            asset_name = cols[0].text_input("Asset Name")
            asset_type = cols[1].selectbox("Asset Type", ["road", "bridge", "pipeline", "drainage", "street_light", "public_facility"])
            
            lat = cols[0].number_input("Latitude", value=0.0, format="%.6f")
            lon = cols[1].number_input("Longitude", value=0.0, format="%.6f")
            
            dept = cols[0].text_input("Department", value="City Works")
            install_year = cols[1].number_input("Installation Year", min_value=1900, max_value=2100, value=2020)
            status = cols[0].selectbox("Status", ["active", "inactive", "under_maintenance", "decommissioned"])

            submitted = st.form_submit_button("✅ Add Asset")
            if submitted:
                if not asset_name:
                    st.error("Asset Name is required.")
                else:
                    payload = {
                        "asset_name": asset_name,
                        "asset_type": asset_type,
                        "latitude": lat,
                        "longitude": lon,
                        "department": dept,
                        "installation_year": install_year,
                        "status": status
                    }
                    res = requests.post(f"{api_base}/assets/", json=payload)
                    if res.status_code == 201:
                        st.success("Asset added successfully!")
                        st.rerun()
                    else:
                        st.error(f"Failed to add asset: {res.text}")

    st.markdown("---")
    
    col_t1, col_t2 = st.columns([0.8, 0.2])
    with col_t1:
        st.subheader("📋 Infrastructure Directory")
    with col_t2:
        if st.button("🔄 Refresh Data"):
            st.rerun()

    # Table View
    t_cols = st.columns([2, 1.5, 2, 1.5, 2])
    t_cols[0].markdown("**Name**")
    t_cols[1].markdown("**Type**")
    t_cols[2].markdown("**Location**")
    t_cols[3].markdown("**Condition**")
    t_cols[4].markdown("**Actions**")
    
    st.markdown("<hr style='margin: 0; padding: 0; border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)

    for asset in assets:
        cols = st.columns([2, 1.5, 2, 1.5, 2])
        cols[0].write(asset.get('asset_name', ''))
        cols[1].write(asset.get('asset_type', '').replace('_', ' ').title())
        cols[2].write(f"{asset.get('latitude', 0):.4f}, {asset.get('longitude', 0):.4f}")
        cols[3].write(asset.get('risk_level', 'Unknown').title())
        
        # Actions
        with cols[4]:
            btn_col1, btn_col2 = st.columns(2)
            edit_btn = btn_col1.button("✏️", key=f"edit_{asset['id']}", help="Edit Asset")
            del_btn = btn_col2.button("🗑️", key=f"del_{asset['id']}", help="Delete Asset")
            
            if del_btn:
                d_res = requests.delete(f"{api_base}/assets/{asset['id']}")
                if d_res.status_code == 204:
                    st.success("Asset deleted!")
                    st.rerun()
                else:
                    st.error("Failed to delete.")
            
        if edit_btn:
            st.session_state["editing_asset"] = asset['id']
            st.rerun()

    # Edit Modal / Section
    editing_id = st.session_state.get("editing_asset")
    if editing_id:
        asset_to_edit = next((a for a in assets if a['id'] == editing_id), None)
        if asset_to_edit:
            st.markdown("---")
            st.subheader(f"✏️ Edit Asset: {asset_to_edit.get('asset_name', '')}")
            with st.form("edit_asset_form", clear_on_submit=False):
                c1, c2 = st.columns(2)
                e_name = c1.text_input("Asset Name", value=asset_to_edit.get('asset_name', ''))
                
                type_options = ["road", "bridge", "pipeline", "drainage", "street_light", "public_facility"]
                try:
                    t_index = type_options.index(asset_to_edit.get('asset_type', 'road'))
                except ValueError:
                    t_index = 0
                e_type = c2.selectbox("Asset Type", type_options, index=t_index)
                
                e_lat = c1.number_input("Latitude", value=float(asset_to_edit.get('latitude', 0.0)), format="%.6f")
                e_lon = c2.number_input("Longitude", value=float(asset_to_edit.get('longitude', 0.0)), format="%.6f")
                e_dept = c1.text_input("Department", value=asset_to_edit.get('department', ''))
                e_year = c2.number_input("Installation Year", value=int(asset_to_edit.get('installation_year', 2020)))
                
                status_options = ["active", "inactive", "under_maintenance", "decommissioned"]
                try:
                    s_index = status_options.index(asset_to_edit.get('status', 'active'))
                except ValueError:
                    s_index = 0
                e_status = c1.selectbox("Status", status_options, index=s_index)

                col_btn1, col_btn2 = st.columns(2)
                updated = col_btn1.form_submit_button("💾 Save Changes")
                canceled = col_btn2.form_submit_button("❌ Cancel")

                if updated:
                    if not e_name:
                        st.error("Asset Name is required.")
                    else:
                        payload = {
                            "asset_name": e_name,
                            "asset_type": e_type,
                            "latitude": e_lat,
                            "longitude": e_lon,
                            "department": e_dept,
                            "installation_year": e_year,
                            "status": e_status
                        }
                        u_res = requests.put(f"{api_base}/assets/{editing_id}", json=payload)
                        if u_res.status_code == 200:
                            st.success("Updated successfully!")
                            st.session_state.pop("editing_asset", None)
                            st.rerun()
                        else:
                            st.error(f"Failed to update: {u_res.text}")
                
                if canceled:
                    st.session_state.pop("editing_asset", None)
                    st.rerun()
