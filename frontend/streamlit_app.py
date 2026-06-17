"""
Urban Infrastructure Intelligence Portal
Streamlit Frontend Entry Point
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

st.set_page_config(
    page_title="Urban Infrastructure Intelligence Portal",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

import base64
def set_background(image_path):
    try:
        with open(image_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            ext = image_path.split('.')[-1]
            
            page_bg_img = f'''
            <style>
            .stApp {{
                # background-image: url("data:image/{ext};base64,{b64}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
                
            }}
            /* Dark overlay to make everything readable */
            .stApp::before {{
                content: "";
                position: fixed;
                top: 0; left: 0; width: 100vw; height: 100vh;
                background-color: rgba(0, 0, 0, 0.7);
                z-index: -1;
            }}
            /* Transparent sidebar */
            [data-testid="stSidebar"] {{
                # background-color: rgba(14, 17, 23, 0.8) !important;
                background-color: rgba(ff, ff, ff, 0.8) !important;
            }}
            </style>
            '''
            st.markdown(page_bg_img, unsafe_allow_html=True)
    except FileNotFoundError:
        pass # If you haven't saved the image yet, it won't crash

set_background(os.path.join(os.path.dirname(__file__), "background.jpg"))

# Sidebar navigation
st.sidebar.title("🏙️ Urban Infrastructure Portal")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["📊 Dashboard", "🗺️ Map View", "🔍 Asset Explorer", "🔧 Maintenance Priority", "🏗️ Infrastructure Management"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.caption("v1.0.0 | Metropolis City")

API_BASE = "http://localhost:8000"
st.session_state["API_BASE"] = API_BASE

if page == "📊 Dashboard":
    from frontend.pages.dashboard import render
    render(API_BASE)
elif page == "🗺️ Map View":
    from frontend.pages.map_view import render
    render(API_BASE)
elif page == "🔍 Asset Explorer":
    from frontend.pages.asset_explorer import render
    render(API_BASE)
elif page == "🔧 Maintenance Priority":
    from frontend.pages.maintenance_priority import render
    render(API_BASE)
elif page == "🏗️ Infrastructure Management":
    from frontend.pages.infrastructure_management import render
    render(API_BASE)

