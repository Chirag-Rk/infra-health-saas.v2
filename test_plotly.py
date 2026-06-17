import streamlit as st
import plotly.graph_objects as go
st.write("Hello")
fig_g = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=50,
    title={"text": "Health Score", "font": {"color": "#e0e0e0"}},
    number={"font": {"color": "#e0e0e0", "size": 48}},
))
st.plotly_chart(fig_g)
