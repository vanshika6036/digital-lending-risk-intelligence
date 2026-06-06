import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np


# ─────────────────────────────────────────────
# PAGE 1: PORTFOLIO OVERVIEW
# ─────────────────────────────────────────────

def portfolio_overview():
    st.title("Portfolio Overview")

    # ── Fake data — replace with pd.read_csv later ──
    loans_df = pd.DataFrame({
        'loan_type': ['Personal', 'BNPL', 'Auto', 'Business', 'Education'],
        'count': [320, 180, 210, 150, 140],
        'portfolio_value': [12000000, 4500000, 9800000, 8200000, 5100000]
    })

    city_df = pd.DataFrame({
        'city': ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai',
                 'Pune', 'Kolkata', 'Ahmedabad', 'Jaipur', 'Lucknow'],
        'loan_count': [180, 160, 140, 120, 100, 90, 80, 70, 60, 50]
    })

    monthly_df = pd.DataFrame({
        'month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        'disbursements': [420, 390, 460, 510, 480, 530,
                          490, 520, 470, 560, 540, 580]
    })
    # ────────────────────────────────────────────────

    # KPI cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Active Loans", "8,000")
    col2.metric("Total Portfolio Value", "₹48.2 Cr")
    col3.metric("Average Interest Rate", "14.3%")
    col4.metric("Collection Efficiency", "87.4%")

    st.divider()

    # Row 1: loan type + city
    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(loans_df, x='loan_type', y='count',
                     title='Loan Distribution by Type',
                     color='loan_type',
                     color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig2 = px.bar(city_df, x='city', y='loan_count',
                      title='Geographic Portfolio Distribution',
                      color='loan_count',
                      color_continuous_scale='Blues')
        st.plotly_chart(fig2, width="stretch")

    # Row 2: monthly trend + PAR metrics
    col1, col2 = st.columns(2)

    with col1:
        fig3 = px.line(monthly_df, x='month', y='disbursements',
                       title='Monthly Disbursement Trend',
                       markers=True)
        st.plotly_chart(fig3, width="stretch")

    with col2:
        st.subheader("Portfolio Health (PAR Metrics)")
        par_df = pd.DataFrame({
            'Metric': ['PAR30', 'PAR60', 'PAR90'],
            'Value (%)': [12.4, 7.1, 4.8],
            'Status': ['⚠️ Watch', '⚠️ Watch', '🔴 Critical']
        })
        st.dataframe(par_df, width="stretch")


# ─────────────────────────────────────────────
# PAGE 2: RISK ANALYTICS
# ─────────────────────────────────────────────

def risk_analytics():
    st.title("Risk Analytics")

    # ── Fake data — replace with pd.read_csv later ──
    default_by_type = pd.DataFrame({
        'loan_type': ['Personal', 'BNPL', 'Auto', 'Business', 'Education'],
        'default_rate': [8, 18, 5, 12, 6]
    })

    default_by_grade = pd.DataFrame({
        'risk_grade': ['A', 'B', 'C', 'D'],
        'default_rate': [2, 7, 16, 34]
    })

    dpd_data = pd.DataFrame({
        'dpd': [0] * 600 + [15] * 150 + [30] * 100 + [60] * 80 + [90] * 70
    })

    corr_df = pd.DataFrame(
        np.random.uniform(-1, 1, (4, 4)),
        columns=['cashflow_stability', 'salary_delay_days',
                 'spending_volatility', 'financial_stress_score'],
        index=['cashflow_stability', 'salary_delay_days',
               'spending_volatility', 'financial_stress_score']
    )
    np.fill_diagonal(corr_df.values, 1.0)

    # ROC curve (fake)
    fpr = np.linspace(0, 1, 100)
    tpr = np.sqrt(fpr) * 0.92 + np.random.normal(0, 0.02, 100)
    tpr = np.clip(tpr, 0, 1)
    # ────────────────────────────────────────────────

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(default_by_type, x='loan_type', y='default_rate',
                     title='Default Rate by Loan Type (%)',
                     color='default_rate',
                     color_continuous_scale='Reds')
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig2 = px.bar(default_by_grade, x='risk_grade', y='default_rate',
                      title='Default Rate by Risk Grade (%)',
                      color='risk_grade',
                      color_discrete_sequence=['green', 'yellow', 'orange', 'red'])
        st.plotly_chart(fig2, width="stretch")

    col1, col2 = st.columns(2)

    with col1:
        fig3 = px.histogram(dpd_data, x='dpd',
                            title='DPD Distribution Across All Loans',
                            nbins=20)
        st.plotly_chart(fig3, width="stretch")

    with col2:
        fig4 = px.imshow(corr_df,
                         title='Behavioral Signals Correlation Heatmap',
                         color_continuous_scale='RdBu',
                         zmin=-1, zmax=1)
        st.plotly_chart(fig4, width="stretch")

    # ROC Curve
    st.subheader("Model Performance — ROC Curve")
    fig5 = go.Figure()
    fig5.add_trace(go.Scatter(x=fpr, y=tpr, name='Random Forest (AUC=0.87)',
                              line=dict(color='blue')))
    fig5.add_trace(go.Scatter(x=[0, 1], y=[0, 1], name='Random Baseline',
                              line=dict(dash='dash', color='gray')))
    fig5.update_layout(
        xaxis_title='False Positive Rate',
        yaxis_title='True Positive Rate',
        title='ROC Curve'
    )
    st.plotly_chart(fig5, width="stretch")


# ─────────────────────────────────────────────
# PAGE 3: CUSTOMER SEGMENTS
# ─────────────────────────────────────────────

def customer_segments():
    st.title("Customer Segments")

    # ── Fake data — replace with pd.read_csv later ──
    segment_df = pd.DataFrame({
        'segment': ['Prime', 'Stable', 'Stressed', 'High-Risk'],
        'count': [1800, 1500, 1000, 700],
        'default_rate': [2, 7, 18, 35],
        'avg_income': [95000, 65000, 40000, 28000],
        'avg_credit_score': [810, 690, 560, 420],
        'avg_stress_score': [15, 35, 62, 84]
    })

    scatter_df = pd.DataFrame({
        'income': np.random.randint(20000, 120000, 200),
        'risk_score': np.random.uniform(0, 100, 200),
        'segment': np.random.choice(
            ['Prime', 'Stable', 'Stressed', 'High-Risk'], 200)
    })
    # ────────────────────────────────────────────────

    col1, col2 = st.columns(2)

    with col1:
        fig = px.pie(segment_df, names='segment', values='count',
                     title='Customer Segment Distribution',
                     color_discrete_sequence=['#2ecc71', '#3498db', '#f39c12', '#e74c3c'])
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig2 = px.bar(segment_df, x='segment', y='default_rate',
                      title='Default Rate per Segment (%)',
                      color='segment',
                      color_discrete_sequence=['#2ecc71', '#3498db', '#f39c12', '#e74c3c'])
        st.plotly_chart(fig2, width="stretch")

    st.subheader("Segment Profiles")
    st.dataframe(segment_df, width="stretch")

    fig3 = px.scatter(scatter_df, x='income', y='risk_score',
                      color='segment',
                      title='Risk Score vs Income by Segment',
                      color_discrete_sequence=['#2ecc71', '#3498db', '#f39c12', '#e74c3c'])
    st.plotly_chart(fig3, width="stretch")


# ─────────────────────────────────────────────
# PAGE 4: EARLY WARNING ALERTS
# ─────────────────────────────────────────────

def early_warning():
    st.title("Early Warning Alerts")

    # ── Fake data — replace with pd.read_csv later ──
    alerts_df = pd.DataFrame({
        'customer_id': [f'CUST{str(i).zfill(3)}' for i in range(1, 21)],
        'alert_level': (['Red'] * 5 + ['Amber'] * 8 + ['Green'] * 7),
        'default_probability': (
            [0.82, 0.79, 0.76, 0.71, 0.68] +
            [0.58, 0.54, 0.51, 0.49, 0.45, 0.42, 0.38, 0.35] +
            [0.22, 0.18, 0.15, 0.12, 0.09, 0.07, 0.04]
        ),
        'financial_stress_score': (
            [88, 84, 79, 76, 72] +
            [62, 58, 55, 52, 49, 46, 42, 38] +
            [28, 24, 20, 17, 14, 11, 8]
        ),
        'salary_delay_days': (
            [14, 12, 11, 10, 9] +
            [7, 7, 6, 6, 5, 5, 4, 4] +
            [2, 2, 1, 1, 0, 0, 0]
        )
    })

    trend_df = pd.DataFrame({
        'month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'Red': [180, 195, 210, 222, 230, 234],
        'Amber': [750, 790, 820, 855, 875, 891],
        'Green': [7070, 7015, 6970, 6923, 6895, 6875]
    })
    # ────────────────────────────────────────────────

    # Alert count KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("🔴 Red Alerts", "234", "+4 this week")
    col2.metric("🟡 Amber Alerts", "891", "+16 this week")
    col3.metric("🟢 Green", "6,875", "-20 this week")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        alert_counts = alerts_df['alert_level'].value_counts().reset_index()
        alert_counts.columns = ['alert_level', 'count']
        fig = px.pie(alert_counts, names='alert_level', values='count',
                     title='Alert Distribution',
                     color='alert_level',
                     color_discrete_map={'Red': '#e74c3c', 'Amber': '#f39c12', 'Green': '#2ecc71'})
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig2 = px.line(trend_df, x='month', y=['Red', 'Amber'],
                       title='Alert Trend Over Time',
                       color_discrete_map={'Red': '#e74c3c', 'Amber': '#f39c12'})
        st.plotly_chart(fig2, width="stretch")

    st.subheader("Top 20 Highest Risk Customers")

    # Colour rows by alert level
    def colour_alert(val):
        if val == 'Red':
            return 'background-color: #ffd6d6'
        elif val == 'Amber':
            return 'background-color: #fff3cd'
        return 'background-color: #d6f5d6'

    styled = alerts_df.style.applymap(colour_alert, subset=['alert_level'])
    st.dataframe(styled, width="stretch")

    # Filters
    st.subheader("Filter Alerts")
    col1, col2 = st.columns(2)
    with col1:
        level_filter = st.selectbox("Alert Level", ["All", "Red", "Amber", "Green"])
    with col2:
        prob_filter = st.slider("Min Default Probability", 0.0, 1.0, 0.0)

    filtered = alerts_df.copy()
    if level_filter != "All":
        filtered = filtered[filtered['alert_level'] == level_filter]
    filtered = filtered[filtered['default_probability'] >= prob_filter]
    st.dataframe(filtered, width="stretch")


# ─────────────────────────────────────────────
# PAGE 5: STRATEGIC RECOMMENDATIONS
# ─────────────────────────────────────────────

def recommendations():
    st.title("Strategic Recommendations")

    # ── Fake data — replace with pd.read_csv later ──
    city_risk_df = pd.DataFrame({
        'city': ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai',
                 'Pune', 'Kolkata', 'Ahmedabad', 'Jaipur', 'Lucknow'],
        'risk_score': [42, 55, 38, 61, 44, 39, 67, 58, 71, 73],
        'recommended_action': [
            'Expand', 'Monitor', 'Expand', 'Restrict', 'Expand',
            'Expand', 'Restrict', 'Monitor', 'Restrict', 'Restrict'
        ]
    })

    product_df = pd.DataFrame({
        'product': ['Personal', 'BNPL', 'Auto', 'Business', 'Education'],
        'yield': [14.2, 18.5, 11.8, 15.6, 10.2],
        'default_rate': [8, 18, 5, 12, 6],
        'recommendation': ['Scale', 'Restrict', 'Scale', 'Monitor', 'Scale']
    })
    # ────────────────────────────────────────────────

    st.subheader("Top 5 Policy Recommendations")
    recs = [
        ("✅", "Increase lending limits for Prime segment",
         "Salaried, Age 30–45, Credit Score 750+. Lowest default rate at 2%."),
        ("⚠️", "Reduce BNPL exposure immediately",
         "BNPL has the highest default rate at 18%. Tighten approval criteria."),
        ("🚫", "Restrict self-employed applicants in high-stress segments",
         "Freelancers and self-employed in Stressed/High-Risk segments show 3x default rate."),
        ("📈", "Expand pre-approved personal loans to low-stress salaried customers",
         "Stable segment has strong repayment history and room for higher limits."),
        ("🔍", "Monitor Tier-2 cities closely",
         "Jaipur, Lucknow, and Kolkata showing rising DPD trends over last 3 months.")
    ]

    for icon, title, detail in recs:
        with st.expander(f"{icon} {title}"):
            st.write(detail)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(city_risk_df, x='city', y='risk_score',
                     color='recommended_action',
                     title='City-Level Risk Ranking',
                     color_discrete_map={
                         'Expand': '#2ecc71',
                         'Monitor': '#f39c12',
                         'Restrict': '#e74c3c'
                     })
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig2 = px.scatter(product_df, x='default_rate', y='yield',
                          color='recommendation', text='product',
                          title='Product Performance Scorecard',
                          color_discrete_map={
                              'Scale': '#2ecc71',
                              'Monitor': '#f39c12',
                              'Restrict': '#e74c3c'
                          })
        fig2.update_traces(textposition='top center')
        st.plotly_chart(fig2, width="stretch")

    st.subheader("Segment Expansion Matrix")
    matrix_df = pd.DataFrame({
        'Segment': ['Prime', 'Stable', 'Stressed', 'High-Risk'],
        'Action': ['📈 Grow', '📊 Maintain', '👁️ Monitor', '🚫 Restrict'],
        'Rationale': [
            'Low risk, high yield potential',
            'Stable repayment, moderate growth',
            'Rising stress signals, watch closely',
            'High default rate, limit new approvals'
        ]
    })
    st.dataframe(matrix_df, width="stretch")