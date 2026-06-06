import pandas as pd

# -----------------------
# LOAD FILES
# -----------------------

customers_df = pd.read_csv(
    "data/customers.csv"
)

loans_df = pd.read_csv(
    "data/loans.csv"
)

repayments_df = pd.read_csv(
    "data/repayments.csv"
)

behavior_df = pd.read_csv(
    "data/behavioral_signals.csv"
)

# -----------------------
# REPAYMENT FEATURES
# -----------------------

repayment_features = (
    repayments_df
    .groupby(
        ["customer_id", "loan_id"]
    )
    .agg({

        "days_late": [
            "mean",
            "max"
        ],

        "delinquency_flag":
        "sum",

        "partial_payment_flag":
        "sum"

    })
)

repayment_features.columns = [

    "avg_days_late",
    "max_days_late",

    "delinquency_count",

    "partial_payment_count"
]

repayment_features = (
    repayment_features
    .reset_index()
)

# missed payments

missed_payments = (
    repayments_df[
        repayments_df[
            "payment_status"
        ] == "Missed"
    ]
    .groupby(
        ["customer_id", "loan_id"]
    )
    .size()
    .reset_index(
        name="missed_payment_count"
    )
)

repayment_features = (
    repayment_features
    .merge(
        missed_payments,
        on=[
            "customer_id",
            "loan_id"
        ],
        how="left"
    )
)

repayment_features[
    "missed_payment_count"
] = repayment_features[
    "missed_payment_count"
].fillna(0)

# -----------------------
# BEHAVIORAL FEATURES
# -----------------------

behavior_features = (
    behavior_df
    .groupby(
        "customer_id"
    )
    .agg({

        "net_cash_flow":
        "mean",

        "balance_volatility":
        "mean",

        "cash_flow_consistency_score":
        "mean",

        "spending_shock_flag":
        "sum",

        "overdraft_flag":
        "sum"

    })
)

behavior_features.columns = [

    "avg_net_cash_flow",

    "avg_balance_volatility",

    "avg_cash_flow_consistency",

    "spending_shock_count",

    "overdraft_count"
]

behavior_features = (
    behavior_features
    .reset_index()
)

# -----------------------
# MERGE CUSTOMERS + LOANS
# -----------------------

merged_df = loans_df.merge(

    customers_df,

    on="customer_id",

    how="left"
)

# -----------------------
# MERGE REPAYMENTS
# -----------------------

merged_df = merged_df.merge(

    repayment_features,

    on=[
        "customer_id",
        "loan_id"
    ],

    how="left"
)

# -----------------------
# MERGE BEHAVIOR
# -----------------------

merged_df = merged_df.merge(

    behavior_features,

    on="customer_id",

    how="left"
)

# -----------------------
# FILL NULLS
# -----------------------

merged_df = merged_df.fillna(0)

# -----------------------
# SAVE
# -----------------------

merged_df.to_csv(

    "data/final_dataset.csv",

    index=False
)

print(
    "final_dataset.csv generated successfully!"
)

print(
    merged_df.head()
)

print(
    "\nRows:",
    len(merged_df)
)

print(
    "\nColumns:",
    len(merged_df.columns)
)

print(
    "\nDefault Rate:"
)

print(
    merged_df[
        "defaulted"
    ].value_counts(
        normalize=True
    )
)
drop_cols = [
    "default_probability"
]

approved_df = merged_df[
    merged_df["approved"] == 1
]
drop_cols = [
    "loan_id",
    "customer_id",
    "name",
    "application_date",
    "default_probability",
    "risk_category"
]

print(
    approved_df.corr(
        numeric_only=True
    )["defaulted"]
    .sort_values(
        ascending=False
    )
    .head(20)
)