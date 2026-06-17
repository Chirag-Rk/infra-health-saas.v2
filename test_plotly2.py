import streamlit as st
import plotly.io as pio
import plotly.graph_objects as go

st.write("Applying streamlit template to indicator globally...")
pio.templates.default = "streamlit"
fig_g = go.Figure(go.Indicator(
    mode="gauge+number",
    value=50,
))
st.plotly_chart(fig_g)
