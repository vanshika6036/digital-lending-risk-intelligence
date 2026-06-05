import pandas as pd
import random
from faker import Faker

fake = Faker("en_IN")

customers_df = pd.read_csv(
    "data/customers.csv"
)

loans = []

loan_purposes = [
    "Personal",
    "Education",
    "Medical",
    "Business",
    "Vehicle",
    "Home Renovation"
]

for _, customer in customers_df.iterrows():

    customer_id = customer["customer_id"]

    monthly_income = customer["monthly_income"]
    monthly_expense = customer["monthly_expense"]
    existing_emi = customer["existing_emi"]

    savings_balance = customer["savings_balance"]

    credit_score = customer["credit_score"]

    employment_type = customer["employment_type"]

    dependents = customer["dependents"]

    previous_loans = customer["previous_loans"]

    home_ownership = customer["home_ownership"]

    job_tenure_years = customer["job_tenure_years"]

    loan_id = f"LN{random.randint(100000,999999)}"

    if employment_type == "Student":

        loan_purpose = random.choices(
        [
            "Education",
            "Personal",
            "Medical"
        ],
        weights=[60, 25, 15],
        k=1
    )[0]

    else:

        loan_purpose = random.choice(
        [
            "Personal",
            "Medical",
            "Business",
            "Vehicle",
            "Home Renovation"
        ]
    )

    # ---------------------
    # LOAN ELIGIBILITY
    # ---------------------

    loan_eligibility = (
        monthly_income * 12 * 3
    )
    if credit_score > 800:
        loan_eligibility *= 1.3

    elif credit_score > 750:
        loan_eligibility *= 1.15

    elif credit_score < 550:
        loan_eligibility *= 0.5

    elif credit_score < 650:
        loan_eligibility *= 0.8
   
    if savings_balance > monthly_income * 12:
        loan_eligibility *= 1.2
    if home_ownership == "Owned":
        loan_eligibility *= 1.1

    
    if employment_type == "Student":
        loan_eligibility *= 0.7

    elif employment_type == "Unemployed":
        loan_eligibility *= 0.3

    loan_eligibility = int(
        max(50000, loan_eligibility)
    )

    if loan_purpose == "Medical":
        min_amount = 50000

    elif loan_purpose == "Vehicle":
        min_amount = 200000

    elif loan_purpose == "Business":
        min_amount = 300000

    elif loan_purpose == "Education":
        min_amount = 100000

    else:
        min_amount = 50000



    loan_eligibility = max(
        loan_eligibility,
        min_amount
)

    requested_amount = random.randint(
        min_amount,
        loan_eligibility
)
    approved_amount = int(
        requested_amount *
        random.uniform(0.7, 1.0)
    )
    loan_to_income_ratio = (
        approved_amount /
        max(monthly_income * 12, 1)
)

    # ---------------------
    # TENURE
    # ---------------------

    if loan_purpose == "Personal":

        loan_tenure_months = random.choice(
            [12, 24, 36]
        )

    elif loan_purpose == "Education":

        loan_tenure_months = random.choice(
            [36, 48, 60]
        )

    elif loan_purpose == "Vehicle":

        loan_tenure_months = random.choice(
            [24, 36, 48, 60]
        )

    elif loan_purpose == "Business":

        loan_tenure_months = random.choice(
            [36, 48, 60]
        )

    elif loan_purpose == "Medical":

        loan_tenure_months = random.choice(
            [12, 24, 36]
        )

    else:

        loan_tenure_months = random.choice(
            [48, 60]
        )

    # ---------------------
    # INTEREST RATE
    # ---------------------

    if loan_purpose == "Personal":

        interest_rate = random.uniform(
            12,
            24
        )

    elif loan_purpose == "Medical":

        interest_rate = random.uniform(
            11,
            20
        )

    elif loan_purpose == "Business":

        interest_rate = random.uniform(
            10,
            16
        )

    else:

        interest_rate = random.uniform(
            8,
            12
        )

    if credit_score > 750:
        interest_rate -= 1.5

    elif credit_score < 600:
        interest_rate += 2

    interest_rate = round(
        interest_rate,
        2
    )

    # ---------------------
    # EMI
    # ---------------------

    monthly_rate = (
        interest_rate /
        12 /
        100
    )

    emi = (
        approved_amount *
        monthly_rate *
        (1 + monthly_rate)
        ** loan_tenure_months
    ) / (
        (
            (1 + monthly_rate)
            ** loan_tenure_months
        ) - 1
    )

    emi = round(
        emi,
        2
    )

    emi_to_income_ratio = round(
        emi /
        max(monthly_income, 1),
        2
    )

    # ---------------------
    # RISK SCORE
    # ---------------------

    risk_score = 0
    if loan_to_income_ratio > 4:
        risk_score += 25

    elif loan_to_income_ratio > 3:
        risk_score += 15

    elif loan_to_income_ratio > 2:
        risk_score += 8

    # Credit

    if credit_score < 550:
        risk_score += 35

    elif credit_score < 650:
        risk_score += 20

    elif credit_score < 750:
        risk_score += 10

    # Expense Burden

    expense_ratio = (
        monthly_expense +
        existing_emi
    ) / max(monthly_income, 1)

    if expense_ratio > 0.90:
        risk_score += 25

    elif expense_ratio > 0.75:
        risk_score += 15

    elif expense_ratio > 0.60:
        risk_score += 8

    # New EMI Burden

    total_emi_burden = (
        existing_emi + emi
    )

    burden_ratio = (
        total_emi_burden /
        max(monthly_income, 1)
    )

    if burden_ratio > 0.70:
        risk_score += 25

    elif burden_ratio > 0.50:
        risk_score += 12

    # Savings

    savings_ratio = (
        savings_balance /
        max(monthly_income, 1)
    )

    if savings_ratio < 2:
        risk_score += 15

    elif savings_ratio < 6:
        risk_score += 8

    # Dependents

    if dependents >= 4:
        risk_score += 10

    elif dependents >= 2:
        risk_score += 5

    # Employment

    if employment_type == "Unemployed":
        risk_score += 40

    elif employment_type == "Student":
        risk_score += 15

    # Stability

    if job_tenure_years > 10:
        risk_score -= 5

    # Assets

    if home_ownership == "Owned":
        risk_score -= 5

    # Loan History

    if previous_loans >= 5:
        risk_score -= 5

    risk_score = max(
        0,
        min(risk_score, 100)
    )
    underwriting_score = 100 - risk_score

    # ---------------------
    # RISK CATEGORY
    # ---------------------

    if risk_score < 25:

        risk_category = "Low"

    elif risk_score < 50:

        risk_category = "Medium"

    else:

        risk_category = "High"

    # ---------------------
    # APPROVAL ENGINE
    # ---------------------



    if risk_score > 80:

        approved = 0

        rejection_reason = (
            "High Risk"
    )

    elif burden_ratio > 0.75:

        approved = 0

        rejection_reason = (
            "Insufficient Repayment Capacity"
    )

    elif loan_to_income_ratio > 4:

        approved = 0

        rejection_reason = (
            "Excessive Loan Exposure"
    )

    else:

        approved = 1

        rejection_reason = "N/A"
    # ---------------------
    # DEFAULT PROBABILITY
    # ---------------------

    default_probability = min(
        0.02 + (risk_score / 100) * 0.60,
        0.80
    )
    default_probability = round(
    default_probability,
    3
)

    
    if approved == 0:
        defaulted = 0

    else:
        defaulted = (
            1
            if random.random()
            < default_probability
            else 0
    )

    # ---------------------
    # LOAN STATUS
    # ---------------------

    if approved == 0:

        loan_status = "Rejected"

    elif defaulted == 1:

        loan_status = "Defaulted"

    else:

        loan_status = random.choice(
            [
                "Active",
                "Closed"
            ]
        )

    application_date = fake.date_between(
        start_date="-2y",
        end_date="today"
    )

    loans.append({

        "loan_id": loan_id,
        "customer_id": customer_id,

        "loan_purpose": loan_purpose,

        "requested_amount":
        requested_amount,

        "approved_amount":
        approved_amount,

        "loan_tenure_months":
        loan_tenure_months,

        "interest_rate":
        interest_rate,

        "emi":
        emi,

        "emi_to_income_ratio":
        emi_to_income_ratio,

        "application_date":
        application_date,

        "risk_score":
        risk_score,
        "underwriting_score":
        underwriting_score,

        "default_probability":
        default_probability,

        "risk_category":
        risk_category,

        "approved":
        approved,

        "rejection_reason":
        rejection_reason,

        "loan_to_income_ratio":
         round(loan_to_income_ratio, 2),


        "loan_status":
        loan_status,


        "defaulted":
        defaulted
    })

loans_df = pd.DataFrame(loans)

loans_df.to_csv(
    "data/loans.csv",
    index=False
)

print("loans.csv generated successfully!")
print(loans_df.head())

print("\nRisk Categories:")
print(
    loans_df["risk_category"]
    .value_counts()
)

print("\nLoan Status:")
print(
    loans_df["loan_status"]
    .value_counts()
)
print("\nApproval Rate:")
print(
    loans_df["approved"]
    .value_counts(normalize=True)
)

print("\nDefault Rate:")
print(
    loans_df["defaulted"]
    .value_counts(normalize=True)
)

print("\nAverage Risk Score:")
print(
    round(
        loans_df["risk_score"].mean(),
        2
    )
)