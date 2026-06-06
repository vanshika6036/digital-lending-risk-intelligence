import streamlit as st
from dashboard_pages import portfolio_overview, risk_analytics, customer_segments, early_warning, recommendations

st.set_page_config(page_title="Lending Risk Intelligence", layout="wide")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "Portfolio Overview",
    "Risk Analytics", 
    "Customer Segments",
    "Early Warning Alerts",
    "Strategic Recommendations"
])

if page == "Portfolio Overview":
    portfolio_overview()
elif page == "Risk Analytics":
    risk_analytics()
elif page == "Customer Segments":
    customer_segments()
elif page == "Early Warning Alerts":
    early_warning()
elif page == "Strategic Recommendations":
    recommendations()