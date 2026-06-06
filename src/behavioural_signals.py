import pandas as pd
import random

customers_df = pd.read_csv(
    "data/customers.csv"
)

behavioral_data = []

for _, customer in customers_df.iterrows():

    customer_id = customer["customer_id"]

    monthly_income = customer["monthly_income"]

    monthly_expense = customer["monthly_expense"]

    employment_type = customer["employment_type"]

    credit_score = customer["credit_score"]

    base_consistency = random.randint(50, 100)

    if employment_type == "Salaried":
        base_consistency = random.randint(75, 100)

    elif employment_type == "Self-employed":
        base_consistency = random.randint(50, 90)

    elif employment_type == "Student":
        base_consistency = random.randint(40, 80)

    else:
        base_consistency = random.randint(20, 60)

    for month in range(1, 13):

        cash_flow_consistency_score = max(
            0,
            min(
                100,
                base_consistency +
                random.randint(-5, 5)
    )
)

        # ----------------------
        # INFLOW
        # ----------------------

        if employment_type == "Salaried":

            avg_monthly_inflow = int(
                monthly_income *
                random.uniform(
                    0.95,
                    1.05
                )
            )

        elif employment_type == "Self-employed":

            avg_monthly_inflow = int(
                monthly_income *
                random.uniform(
                    0.7,
                    1.3
                )
            )

        elif employment_type == "Student":

            avg_monthly_inflow = int(
                monthly_income *
                random.uniform(
                    0.5,
                    1.2
                )
            )

        else:

            avg_monthly_inflow = int(
                monthly_income *
                random.uniform(
                    0.3,
                    1.0
                )
            )

        # ----------------------
        # OUTFLOW
        # ----------------------

        avg_monthly_outflow = int(
            monthly_expense *
            random.uniform(
                0.8,
                1.2
            )
        )

        # ----------------------
        # CASH FLOW CONSISTENCY
        # ----------------------

        

        # ----------------------
        # BALANCE VOLATILITY
        # ----------------------

        if credit_score > 750:

            balance_volatility = round(
                random.uniform(
                    0.05,
                    0.25
                ),
                2
            )

        elif credit_score > 650:

            balance_volatility = round(
                random.uniform(
                    0.20,
                    0.50
                ),
                2
            )

        else:

            balance_volatility = round(
                random.uniform(
                    0.40,
                    0.90
                ),
                2
            )

        # ----------------------
        # SPENDING SHOCK
        # ----------------------

        shock_probability = 0.05

        if credit_score < 650:
            shock_probability = 0.12

        elif credit_score < 700:
            shock_probability = 0.08

        spending_shock_flag = 0

        if random.random() < shock_probability:

            spending_shock_flag = 1

            avg_monthly_outflow = int(
                avg_monthly_outflow *
                random.uniform(
                    1.5,
                    2.5
        )
    )

            cash_flow_consistency_score = max(
                0,
                cash_flow_consistency_score -
                random.randint(
                    10,
                    30
        )
    )
       
        net_cash_flow = (
            avg_monthly_inflow -
            avg_monthly_outflow
)

        overdraft_flag = (
            1
            if net_cash_flow < 0
            else 0
)

        behavioral_data.append({

            "customer_id":
            customer_id,

            "month":
            month,

            "avg_monthly_inflow":
            avg_monthly_inflow,

            "avg_monthly_outflow":
            avg_monthly_outflow,

            "net_cash_flow":
            net_cash_flow,

            "cash_flow_consistency_score":
            cash_flow_consistency_score,

            "balance_volatility":
            balance_volatility,

            "spending_shock_flag":
            spending_shock_flag,
            "overdraft_flag":
            overdraft_flag
        })

behavior_df = pd.DataFrame(
    behavioral_data
)

behavior_df.to_csv(
    "data/behavioral_signals.csv",
    index=False
)

print(
    "behavioral_signals.csv generated successfully!"
)

print(
    behavior_df.head()
)

print("\nTotal Records:")
print(
    len(behavior_df)
)

print("\nSpending Shock Rate:")
print(
    behavior_df[
        "spending_shock_flag"
    ].value_counts(
        normalize=True
    )
)
print("\nOverdraft Rate:")
print(
    behavior_df[
        "overdraft_flag"
    ].value_counts(
        normalize=True
    )
)
print("\nAverage Cash Flow:")
print(
    round(
        behavior_df[
            "net_cash_flow"
        ].mean(),
        2
    )
)