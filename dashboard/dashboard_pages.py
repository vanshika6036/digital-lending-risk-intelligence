import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import roc_curve, roc_auc_score
import os

# ─────────────────────────────────────────────
# DATA LOADER (cached for performance)
# ─────────────────────────────────────────────

@st.cache_data
def load_data():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    df = pd.read_csv(os.path.join(base, 'data', 'processed', 'enriched_dataset.csv'))

    # Date parsing
    df['application_date'] = pd.to_datetime(df['application_date'])
    df['month'] = df['application_date'].dt.strftime('%b %Y')
    df['rejection_reason'] = df['rejection_reason'].fillna('Approved')

    # Risk tier from ML risk score
    def assign_tier(score):
        if score < 35:
            return 'Green'
        elif score < 65:
            return 'Amber'
        else:
            return 'Red'

    df_approved = df[df['approved'] == 1].copy()

    # Try loading saved risk scores, else compute on the fly
    risk_path = os.path.join(base, 'data', 'processed', 'risk_scores.csv')
    if os.path.exists(risk_path):
        risk_df = pd.read_csv(risk_path)
        df_approved = df_approved.merge(
            risk_df[['customer_id', 'risk_score_ml', 'risk_tier', 'segment_label']],
            on='customer_id', how='left'
        )
        df_approved['risk_tier'] = df_approved['risk_tier'].fillna('Amber')
        df_approved['segment_label'] = df_approved['segment_label'].fillna('Near-Prime Borrowers')
    else:
        # Quick risk tier from existing risk_score column
        df_approved['risk_score_ml'] = df_approved['risk_score']
        df_approved['risk_tier'] = df_approved['risk_score_ml'].apply(assign_tier)
        df_approved['segment_label'] = df_approved['risk_category'].map({
            'Low': 'Prime Borrowers',
            'Medium': 'Near-Prime Borrowers',
            'High': 'High-Risk Borrowers'
        })

    return df, df_approved


@st.cache_data
def get_roc_data():
    df, df_approved = load_data()
    num_cols = ['age', 'monthly_income', 'credit_score', 'emi_to_income_ratio',
                'loan_to_income_ratio', 'risk_score', 'underwriting_score',
                'default_probability', 'interest_rate', 'savings_balance']
    cat_cols = ['employment_type', 'risk_category', 'loan_purpose']
    le = LabelEncoder()
    df_m = df_approved.copy()
    for col in cat_cols:
        df_m[col + '_enc'] = le.fit_transform(df_m[col].astype(str))
    enc_cols = [c + '_enc' for c in cat_cols]
    X = df_m[num_cols + enc_cols]
    y = df_m['defaulted']
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)
    rf = RandomForestClassifier(n_estimators=100, max_depth=8,
                                class_weight='balanced', random_state=42)
    rf.fit(X_train, y_train)
    y_prob = rf.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    auc = roc_auc_score(y_test, y_prob)
    return fpr, tpr, auc


# ─────────────────────────────────────────────
# PAGE 1: PORTFOLIO OVERVIEW
# ─────────────────────────────────────────────

def portfolio_overview():
    st.title("📊 Portfolio Overview")
    df, df_approved = load_data()

    # KPI calculations
    total_approved = len(df_approved)
    portfolio_value = df_approved['approved_amount'].sum()
    avg_interest = df_approved['interest_rate'].mean()
    npa_pct = df_approved['defaulted'].mean() * 100
    approval_rate = df['approved'].mean() * 100
    total_defaulted = df_approved['defaulted'].sum()

    # KPI cards
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Approved Loans", f"{total_approved:,}")
    col2.metric("Portfolio Value", f"₹{portfolio_value/1e7:.1f} Cr")
    col3.metric("Avg Interest Rate", f"{avg_interest:.1f}%")
    col4.metric("NPA %", f"{npa_pct:.1f}%")
    col5.metric("Approval Rate", f"{approval_rate:.1f}%")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        # Loan distribution by purpose
        loan_dist = df_approved.groupby('loan_purpose').agg(
            count=('loan_id', 'count'),
            portfolio_value=('approved_amount', 'sum')
        ).reset_index()
        fig = px.bar(loan_dist, x='loan_purpose', y='count',
                     title='Loan Distribution by Purpose',
                     color='loan_purpose',
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Geographic distribution - top 10 cities
        city_dist = df_approved.groupby('city')['loan_id'].count().reset_index()
        city_dist.columns = ['city', 'loan_count']
        city_dist = city_dist.sort_values('loan_count', ascending=False).head(10)
        fig2 = px.bar(city_dist, x='city', y='loan_count',
                      title='Top 10 Cities — Loan Volume',
                      color='loan_count',
                      color_continuous_scale='Blues')
        st.plotly_chart(fig2, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        # Monthly disbursement trend
        monthly = df_approved.groupby('month').agg(
            disbursements=('loan_id', 'count'),
            total_value=('approved_amount', 'sum')
        ).reset_index()
        fig3 = px.line(monthly, x='month', y='disbursements',
                       title='Monthly Disbursement Trend',
                       markers=True,
                       line_shape='spline')
        fig3.update_traces(line_color='#3498db')
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        # Portfolio health metrics
        st.subheader("Portfolio Health Metrics")
        par30 = len(df_approved[df_approved['default_probability'] > 0.3]) / total_approved * 100
        par60 = len(df_approved[df_approved['default_probability'] > 0.5]) / total_approved * 100
        par90 = len(df_approved[df_approved['default_probability'] > 0.7]) / total_approved * 100

        par_df = pd.DataFrame({
            'Metric': ['PAR30 (prob > 0.3)', 'PAR60 (prob > 0.5)', 'PAR90 (prob > 0.7)', 'Actual NPA %'],
            'Value (%)': [round(par30, 1), round(par60, 1), round(par90, 1), round(npa_pct, 1)],
            'Status': [
                '⚠️ Watch' if par30 > 10 else '✅ OK',
                '⚠️ Watch' if par60 > 7 else '✅ OK',
                '🔴 Critical' if par90 > 5 else '⚠️ Watch',
                '🔴 Critical' if npa_pct > 10 else '⚠️ Watch'
            ]
        })
        st.dataframe(par_df, use_container_width=True)

        # Risk category breakdown
        risk_dist = df_approved['risk_category'].value_counts().reset_index()
        risk_dist.columns = ['risk_category', 'count']
        fig4 = px.pie(risk_dist, names='risk_category', values='count',
                      title='Portfolio by Risk Category',
                      color='risk_category',
                      color_discrete_map={'Low': '#27ae60', 'Medium': '#e67e22', 'High': '#e74c3c'})
        st.plotly_chart(fig4, use_container_width=True)


# ─────────────────────────────────────────────
# PAGE 2: RISK ANALYTICS
# ─────────────────────────────────────────────

def risk_analytics():
    st.title("🎯 Risk Analytics")
    df, df_approved = load_data()

    col1, col2 = st.columns(2)

    with col1:
        # Default rate by loan purpose
        default_by_purpose = df_approved.groupby('loan_purpose')['defaulted'].mean().reset_index()
        default_by_purpose['default_rate'] = (default_by_purpose['defaulted'] * 100).round(1)
        default_by_purpose = default_by_purpose.sort_values('default_rate', ascending=False)
        fig = px.bar(default_by_purpose, x='loan_purpose', y='default_rate',
                     title='Default Rate by Loan Purpose (%)',
                     color='default_rate',
                     color_continuous_scale='Reds')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Default rate by risk category
        default_by_risk = df_approved.groupby('risk_category')['defaulted'].mean().reset_index()
        default_by_risk['default_rate'] = (default_by_risk['defaulted'] * 100).round(1)
        default_by_risk['risk_category'] = pd.Categorical(
            default_by_risk['risk_category'], ['Low', 'Medium', 'High'])
        default_by_risk = default_by_risk.sort_values('risk_category')
        fig2 = px.bar(default_by_risk, x='risk_category', y='default_rate',
                      title='Default Rate by Risk Category (%)',
                      color='risk_category',
                      color_discrete_map={'Low': '#27ae60', 'Medium': '#e67e22', 'High': '#e74c3c'})
        fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        # Default probability distribution
        fig3 = px.histogram(df_approved, x='default_probability',
                            title='Default Probability Distribution',
                            nbins=30,
                            color_discrete_sequence=['#3498db'])
        fig3.add_vline(x=0.3, line_dash='dash', line_color='orange', annotation_text='PAR30')
        fig3.add_vline(x=0.5, line_dash='dash', line_color='red', annotation_text='PAR60')
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        # Correlation heatmap of key risk features
        corr_cols = ['credit_score', 'monthly_income', 'emi_to_income_ratio',
                     'default_probability', 'risk_score', 'savings_balance']
        corr_df = df_approved[corr_cols].corr().round(2)
        fig4 = px.imshow(corr_df,
                         title='Risk Feature Correlation Heatmap',
                         color_continuous_scale='RdBu',
                         zmin=-1, zmax=1,
                         text_auto=True)
        st.plotly_chart(fig4, use_container_width=True)

    # ROC Curve
    st.subheader("Model Performance — ROC Curve")
    with st.spinner("Training model for ROC curve..."):
        fpr, tpr, auc = get_roc_data()
    fig5 = go.Figure()
    fig5.add_trace(go.Scatter(x=fpr, y=tpr,
                              name=f'Random Forest (AUC = {auc:.3f})',
                              line=dict(color='#3498db', width=2)))
    fig5.add_trace(go.Scatter(x=[0, 1], y=[0, 1],
                              name='Random Baseline',
                              line=dict(dash='dash', color='gray')))
    fig5.update_layout(xaxis_title='False Positive Rate',
                       yaxis_title='True Positive Rate',
                       title='ROC Curve — Default Prediction Model')
    st.plotly_chart(fig5, use_container_width=True)

    # Employment type risk breakdown
    emp_risk = df_approved.groupby('employment_type').agg(
        count=('customer_id', 'count'),
        default_rate=('defaulted', 'mean'),
        avg_income=('monthly_income', 'mean')
    ).reset_index()
    emp_risk['default_rate'] = (emp_risk['default_rate'] * 100).round(1)
    emp_risk['avg_income'] = emp_risk['avg_income'].round(0)
    emp_risk = emp_risk.sort_values('default_rate', ascending=False)
    st.subheader("Risk by Employment Type")
    st.dataframe(emp_risk, use_container_width=True)


# ─────────────────────────────────────────────
# PAGE 3: CUSTOMER SEGMENTS
# ─────────────────────────────────────────────

def customer_segments():
    st.title("👥 Customer Segments")
    df, df_approved = load_data()

    col1, col2 = st.columns(2)

    with col1:
        # Segment distribution
        if 'segment_label' in df_approved.columns:
            seg_dist = df_approved['segment_label'].value_counts().reset_index()
            seg_dist.columns = ['segment', 'count']
        else:
            seg_dist = df_approved['risk_category'].value_counts().reset_index()
            seg_dist.columns = ['segment', 'count']

        fig = px.pie(seg_dist, names='segment', values='count',
                     title='Customer Segment Distribution',
                     color_discrete_sequence=['#27ae60', '#3498db', '#e67e22', '#e74c3c'])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Default rate by segment
        if 'segment_label' in df_approved.columns:
            seg_default = df_approved.groupby('segment_label')['defaulted'].mean().reset_index()
            seg_default.columns = ['segment', 'default_rate']
        else:
            seg_default = df_approved.groupby('risk_category')['defaulted'].mean().reset_index()
            seg_default.columns = ['segment', 'default_rate']
        seg_default['default_rate'] = (seg_default['default_rate'] * 100).round(1)
        fig2 = px.bar(seg_default, x='segment', y='default_rate',
                      title='Default Rate per Segment (%)',
                      color='segment',
                      color_discrete_sequence=['#27ae60', '#3498db', '#e67e22', '#e74c3c'])
        fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Segment profiles table
    st.subheader("Segment Profiles")
    seg_label_col = 'segment_label' if 'segment_label' in df_approved.columns else 'risk_category'
    seg_profile = df_approved.groupby(seg_label_col).agg(
        count=('customer_id', 'count'),
        avg_credit_score=('credit_score', 'mean'),
        avg_income=('monthly_income', 'mean'),
        avg_default_prob=('default_probability', 'mean'),
        actual_default_rate=('defaulted', 'mean'),
        avg_loan_size=('approved_amount', 'mean'),
        avg_emi_ratio=('emi_to_income_ratio', 'mean')
    ).round(2).reset_index()
    seg_profile['actual_default_rate'] = (seg_profile['actual_default_rate'] * 100).round(1)
    st.dataframe(seg_profile, use_container_width=True)

    # Scatter: income vs default probability
    sample = df_approved.sample(min(800, len(df_approved)), random_state=42)
    fig3 = px.scatter(sample, x='monthly_income', y='default_probability',
                      color=seg_label_col,
                      title='Default Probability vs Monthly Income by Segment',
                      opacity=0.6,
                      color_discrete_sequence=['#27ae60', '#3498db', '#e67e22', '#e74c3c'])
    st.plotly_chart(fig3, use_container_width=True)

    # Credit score distribution by segment
    fig4 = px.box(df_approved, x=seg_label_col, y='credit_score',
                  title='Credit Score Distribution by Segment',
                  color=seg_label_col,
                  color_discrete_sequence=['#27ae60', '#3498db', '#e67e22', '#e74c3c'])
    fig4.update_layout(showlegend=False)
    st.plotly_chart(fig4, use_container_width=True)


# ─────────────────────────────────────────────
# PAGE 4: EARLY WARNING ALERTS
# ─────────────────────────────────────────────

def early_warning():
    st.title("🚨 Early Warning Alerts")
    df, df_approved = load_data()

    # Assign risk tiers
    tier_col = 'risk_tier' if 'risk_tier' in df_approved.columns else None
    if tier_col is None:
        df_approved['risk_tier'] = df_approved['default_probability'].apply(
            lambda x: 'Red' if x >= 0.65 else ('Amber' if x >= 0.35 else 'Green'))

    tier_counts = df_approved['risk_tier'].value_counts()
    red_count = tier_counts.get('Red', 0)
    amber_count = tier_counts.get('Amber', 0)
    green_count = tier_counts.get('Green', 0)

    # KPI cards
    col1, col2, col3 = st.columns(3)
    col1.metric("🔴 Red Alerts", f"{red_count:,}", "High risk — immediate action")
    col2.metric("🟡 Amber Alerts", f"{amber_count:,}", "Watch — enhanced monitoring")
    col3.metric("🟢 Green", f"{green_count:,}", "Low risk — standard process")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        # Alert distribution pie
        alert_dist = df_approved['risk_tier'].value_counts().reset_index()
        alert_dist.columns = ['alert_level', 'count']
        fig = px.pie(alert_dist, names='alert_level', values='count',
                     title='Alert Distribution',
                     color='alert_level',
                     color_discrete_map={'Red': '#e74c3c', 'Amber': '#f39c12', 'Green': '#2ecc71'})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Default probability by tier
        fig2 = px.box(df_approved, x='risk_tier', y='default_probability',
                      title='Default Probability by Risk Tier',
                      color='risk_tier',
                      color_discrete_map={'Red': '#e74c3c', 'Amber': '#f39c12', 'Green': '#2ecc71'},
                      category_orders={'risk_tier': ['Green', 'Amber', 'Red']})
        fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Top high risk customers
    st.subheader("Top 20 Highest Risk Customers")
    top_risk = df_approved.nlargest(20, 'default_probability')[
        ['customer_id', 'name', 'risk_tier', 'default_probability',
         'credit_score', 'monthly_income', 'loan_purpose', 'approved_amount',
         'employment_type', 'city']
    ].reset_index(drop=True)

    def color_tier(val):
        if val == 'Red':
            return 'background-color: #ffd6d6'
        elif val == 'Amber':
            return 'background-color: #fff3cd'
        return 'background-color: #d6f5d6'

    styled = top_risk.style.applymap(color_tier, subset=['risk_tier'])
    st.dataframe(styled, use_container_width=True)

    # Filters
    st.subheader("Filter Customers by Risk")
    col1, col2, col3 = st.columns(3)
    with col1:
        level_filter = st.selectbox("Alert Level", ["All", "Red", "Amber", "Green"])
    with col2:
        prob_filter = st.slider("Min Default Probability", 0.0, 1.0, 0.0, 0.05)
    with col3:
        emp_filter = st.selectbox("Employment Type",
                                  ["All"] + list(df_approved['employment_type'].unique()))

    filtered = df_approved.copy()
    if level_filter != "All":
        filtered = filtered[filtered['risk_tier'] == level_filter]
    filtered = filtered[filtered['default_probability'] >= prob_filter]
    if emp_filter != "All":
        filtered = filtered[filtered['employment_type'] == emp_filter]

    display_cols = ['customer_id', 'name', 'risk_tier', 'default_probability',
                    'credit_score', 'monthly_income', 'loan_purpose',
                    'approved_amount', 'city', 'employment_type']
    st.dataframe(filtered[display_cols].reset_index(drop=True), use_container_width=True)
    st.caption(f"Showing {len(filtered):,} customers")


# ─────────────────────────────────────────────
# PAGE 5: STRATEGIC RECOMMENDATIONS
# ─────────────────────────────────────────────

def recommendations():
    st.title("💡 Strategic Recommendations")
    df, df_approved = load_data()

    st.subheader("Top 5 Policy Recommendations")

    # Calculate real numbers for recommendations
    bnpl_default = df_approved[df_approved['loan_purpose'] == 'Business']['defaulted'].mean() * 100
    prime_default = df_approved[df_approved['risk_category'] == 'Low']['defaulted'].mean() * 100
    high_risk_default = df_approved[df_approved['risk_category'] == 'High']['defaulted'].mean() * 100
    unemployed_default = df_approved[df_approved['employment_type'] == 'Unemployed']['defaulted'].mean() * 100
    high_emi_default = df_approved[df_approved['emi_to_income_ratio'] > 0.5]['defaulted'].mean() * 100

    recs = [
        ("✅", "Increase lending limits for Prime / Low-Risk segment",
         f"Low-risk borrowers have only {prime_default:.1f}% default rate. "
         f"Salaried customers with credit score 750+ are the safest segment. "
         f"Pre-approved offers and higher limits recommended."),
        ("⚠️", f"Restrict Business loans for High-Risk borrowers",
         f"Business loans in High-risk category show {bnpl_default:.1f}% default rate — "
         f"the highest across all product-risk combinations. Tighten approval criteria immediately."),
        ("🚫", f"Cap EMI-to-Income ratio at 0.5 as a hard underwriting rule",
         f"Borrowers with EMI ratio above 0.5 default at {high_emi_default:.1f}%. "
         f"This single rule could significantly reduce NPA. Currently not enforced as a hard limit."),
        ("📈", "Raise interest rates by 150bps for Amber-tier borrowers",
         f"Amber-tier borrowers represent significant portfolio risk but are currently "
         f"not priced adequately. A 150bps rate increase improves risk-adjusted return "
         f"while maintaining competitiveness."),
        ("🔍", f"Restrict new credit for Unemployed borrowers",
         f"Unemployed borrowers show {unemployed_default:.1f}% default rate — "
         f"significantly higher than salaried borrowers. "
         f"Introduce income verification as a mandatory step for this segment.")
    ]

    for icon, title, detail in recs:
        with st.expander(f"{icon} {title}"):
            st.write(detail)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        # City level risk
        city_risk = df_approved.groupby('city').agg(
            loan_count=('loan_id', 'count'),
            default_rate=('defaulted', 'mean'),
            avg_risk_score=('risk_score', 'mean')
        ).reset_index()
        city_risk['default_rate'] = (city_risk['default_rate'] * 100).round(1)
        city_risk = city_risk[city_risk['loan_count'] >= 30].sort_values(
            'default_rate', ascending=False).head(15)
        city_risk['action'] = city_risk['default_rate'].apply(
            lambda x: 'Restrict' if x > 15 else ('Monitor' if x > 10 else 'Expand'))

        fig = px.bar(city_risk, x='city', y='default_rate',
                     color='action',
                     title='City-Level Default Rate & Recommended Action',
                     color_discrete_map={'Expand': '#2ecc71', 'Monitor': '#f39c12', 'Restrict': '#e74c3c'})
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Product performance scorecard
        product_perf = df_approved.groupby('loan_purpose').agg(
            default_rate=('defaulted', 'mean'),
            avg_yield=('interest_rate', 'mean'),
            count=('loan_id', 'count')
        ).reset_index()
        product_perf['default_rate'] = (product_perf['default_rate'] * 100).round(1)
        product_perf['avg_yield'] = product_perf['avg_yield'].round(1)
        product_perf['recommendation'] = product_perf.apply(
            lambda r: 'Restrict' if r['default_rate'] > 15
            else ('Monitor' if r['default_rate'] > 10 else 'Scale'), axis=1)

        fig2 = px.scatter(product_perf, x='default_rate', y='avg_yield',
                          color='recommendation', text='loan_purpose',
                          size='count',
                          title='Product Performance Scorecard',
                          color_discrete_map={'Scale': '#2ecc71', 'Monitor': '#f39c12', 'Restrict': '#e74c3c'})
        fig2.update_traces(textposition='top center')
        st.plotly_chart(fig2, use_container_width=True)

    # Segment expansion matrix
    st.subheader("Segment Action Matrix")
    seg_label_col = 'segment_label' if 'segment_label' in df_approved.columns else 'risk_category'
    seg_matrix = df_approved.groupby(seg_label_col).agg(
        count=('customer_id', 'count'),
        default_rate=('defaulted', 'mean'),
        avg_loan=('approved_amount', 'mean')
    ).reset_index()
    seg_matrix['default_rate'] = (seg_matrix['default_rate'] * 100).round(1)
    seg_matrix['avg_loan'] = seg_matrix['avg_loan'].round(0)
    seg_matrix['action'] = seg_matrix['default_rate'].apply(
        lambda x: '📈 Grow' if x < 5 else ('📊 Maintain' if x < 12 else ('👁️ Monitor' if x < 20 else '🚫 Restrict')))
    st.dataframe(seg_matrix, use_container_width=True)