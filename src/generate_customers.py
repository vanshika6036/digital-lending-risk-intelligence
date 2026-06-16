import pandas as pd
from faker import Faker
import random

fake = Faker("en_IN")

customers = []

cities = [
    "Bangalore", "Pune", "Mumbai", "Delhi",
    "Hyderabad", "Kolkata", "Ahmedabad",
    "Indore", "Bhopal", "Chennai",
    "Surat", "Patna", "Ranchi",
    "Jamshedpur", "Bhubaneswar",
    "Srinagar", "Meerut", "Darbhanga",
    "Chapra", "Ballia", "Nagpur"
]

education_levels = [
    "High School",
    "Diploma",
    "Bachelor",
    "Master",
    "PhD"
]

acquisition_channels = [
    "Instagram",
    "Referral",
    "Google Ads",
    "Facebook",
    "YouTube"
]

device_types = [
    "Android",
    "iPhone",
    "Web"
]

for i in range(5000):

    customer_id = f"C{i+1:05d}"
    name = fake.name()

    employment_type = random.choices(
        ["Salaried", "Self-employed", "Student", "Unemployed"],
        weights=[60, 20, 15, 5],
        k=1
    )[0]

    # Age

    if employment_type == "Student":
        age = random.randint(18, 25)

    elif employment_type == "Salaried":
        age = random.randint(22, 60)

    elif employment_type == "Self-employed":
        age = random.randint(25, 65)

    else:
        age = random.randint(18, 60)

    # Occupation

    if employment_type == "Salaried":

        occupation = random.choice([
            "Software Engineer",
            "Teacher",
            "Doctor",
            "Accountant",
            "Sales Executive",
            "Bank Officer",
            "Government Employee"
        ])

    elif employment_type == "Self-employed":

        occupation = random.choice([
            "Shop Owner",
            "Consultant",
            "Freelancer",
            "Contractor",
            "Business Owner"
        ])

    elif employment_type == "Student":

        occupation = "Student"

    else:

        occupation = "Unemployed"

    gender = random.choices(
    ["Male", "Female", "Other"],
    weights=[50, 49, 1],
    k=1
)[0]

    city = random.choice(cities)

    # Marital Status

    if age < 25:

        marital_status = random.choices(
            ["Single", "Married"],
            weights=[90, 10],
            k=1
        )[0]

    elif age < 35:

        marital_status = random.choices(
            ["Single", "Married", "Divorced"],
            weights=[40, 55, 5],
            k=1
        )[0]

    else:

        marital_status = random.choices(
            ["Single", "Married", "Divorced"],
            weights=[20, 70, 10],
            k=1
        )[0]

    # Income

    if employment_type == "Student":

        monthly_income = random.randint(
            5000,
            30000
        )

    elif employment_type == "Salaried":

        monthly_income = random.randint(
            25000,
            150000
        )

    elif employment_type == "Self-employed":

        monthly_income = random.randint(
            30000,
            250000
        )

    else:

        monthly_income = random.randint(
            0,
            15000
        )

    # Expenses

    if employment_type == "Student":
        expense_ratio = random.uniform(0.5, 1.0)

    elif employment_type == "Unemployed":
        expense_ratio = random.uniform(0.6, 1.0)

    else:
        expense_ratio = random.uniform(0.4, 0.8)

    monthly_expense = int(
        monthly_income * expense_ratio
)

    # Existing EMI

    if employment_type == "Unemployed":
        existing_emi = 0

    else:
        existing_emi = int(
            monthly_income *
            random.uniform(0, 0.4)
    )
    

    # Savings
    

    
    # Home Ownership

    home_ownership = random.choices(
        ["Owned", "Rented", "Family Owned"],
        weights=[30, 50, 20],
        k=1
    )[0]

    # Education
     # Savings

    if employment_type == "Unemployed":

        savings_balance = int(
            monthly_income *
            random.uniform(0, 3)
    )

    elif monthly_income < 30000:

        savings_balance = int(
            monthly_income *
            random.uniform(1, 6)
    )

    elif monthly_income < 100000:

        savings_balance = int(
            monthly_income *
            random.uniform(3, 18)
    )

    else:

        savings_balance = int(
            monthly_income *
            random.uniform(6, 36)
    )

    if employment_type == "Student":

        education_level = random.choice([
            "High School",
            "Diploma",
            "Bachelor"
        ])

    else:

        education_level = random.choice(
            education_levels
        )

    # Dependents

    if marital_status == "Single":

        dependents = random.randint(0, 1)

    elif marital_status == "Married":

        dependents = random.randint(1, 4)

    else:

        dependents = random.randint(0, 2)

    # Account Age

    max_account_age = max(
        1,
        (age - 18) * 12
)

    account_age_months = random.randint(
        1,
        min(max_account_age, 120)
)

    # Job Tenure

    # Job Tenure

    if employment_type in [
        "Salaried",
        "Self-employed"
]:

        working_years = max(
            0,
            age - 22
    )

        job_tenure_years = random.randint(
            0,
            min(working_years, 40)
    )

    else:

        job_tenure_years = 0

    # Previous Loans

    max_loans = max(
        0,
        account_age_months // 12
)

    previous_loans = random.randint(
        0,
        min(max_loans, 10)
)
   
   # Digital Activity

    digital_activity_score = random.randint(
        1,
        100
)

    monthly_transactions = int(
        digital_activity_score *
        random.uniform(1.5, 4)
)
    # Base Credit Score

    if employment_type == "Unemployed":
        credit_score = 500

    elif employment_type == "Student":
        credit_score = 620

    elif employment_type == "Self-employed":
        credit_score = 670

    else:
        credit_score = 700
    
    credit_score += account_age_months // 12

    credit_score += previous_loans * 2

    expense_ratio = (
        monthly_expense /
        max(monthly_income, 1)
    )
    # credit score

    if expense_ratio > 0.8:
        credit_score -= 50

    elif expense_ratio > 0.6:
        credit_score -= 20


    if savings_balance > monthly_income * 12:
        credit_score += 20
    
    if job_tenure_years > 10:
        credit_score += 10

    if home_ownership == "Owned":
        credit_score += 10

    if previous_loans >= 5:
        credit_score += 10

    credit_score += random.randint(-30, 30)

    credit_score = max(
        300,
        min(850, credit_score)
    )

    acquisition_channel = random.choice(
        acquisition_channels
    )

    device_type = random.choice(
        device_types
    )

    customers.append({

        "customer_id": customer_id,
        "name": name,
        "age": age,
        "gender": gender,
        "city": city,

        "marital_status": marital_status,

        "employment_type": employment_type,
        "occupation": occupation,

        "monthly_income": monthly_income,
        "monthly_expense": monthly_expense,
        "existing_emi": existing_emi,

        "savings_balance": savings_balance,

        "home_ownership": home_ownership,

        "education_level": education_level,
        "dependents": dependents,

        "credit_score": credit_score,

        "account_age_months": account_age_months,
        "job_tenure_years": job_tenure_years,

        "previous_loans": previous_loans,

        "monthly_transactions":
        monthly_transactions,

        "acquisition_channel":
        acquisition_channel,

        "device_type": device_type,

        "digital_activity_score":
        digital_activity_score
    })

customers_df = pd.DataFrame(customers)

customers_df.to_csv(
    "data/customers.csv",
    index=False
)

print("customers.csv generated successfully!")
print(customers_df.head())
