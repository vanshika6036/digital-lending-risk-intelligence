import pandas as pd
import random
from faker import Faker

fake = Faker("en_IN")

loans_df = pd.read_csv(
    "data/loans.csv"
)

repayments = []

payment_counter = 1

for _, loan in loans_df.iterrows():

    loan_id = loan["loan_id"]

    customer_id = loan["customer_id"]

    emi_due = loan["emi"]

    tenure = loan["loan_tenure_months"]

    risk_category = loan["risk_category"]

    defaulted = loan["defaulted"]

    loan_start_date = fake.date_between(
        start_date="-2y",
        end_date="-6m"
    )

    previous_delinquency = False

    months_to_generate = min(
        tenure,
        random.randint(12, 24)
    )

    for month in range(
        1,
        months_to_generate + 1
    ):

        payment_id = (
            f"P{payment_counter:07d}"
        )

        payment_counter += 1

        # -------------------------
        # PAYMENT BEHAVIOUR
        # -------------------------

        if defaulted == 1:

            progress = month / months_to_generate

            if progress < 0.5:

                weights = [70, 20, 10]

            elif progress < 0.8:

                weights = [40, 35, 25]

            else:

                weights = [15, 35, 50]

        elif risk_category == "High":

            weights = [65, 20, 15]

        elif risk_category == "Medium":

            weights = [85, 10, 5]

        else:

            weights = [95, 4, 1]

        # Delinquency persistence

        if previous_delinquency and defaulted == 0:

            if risk_category == "High":

                weights = [50, 25, 25]

            elif risk_category == "Medium":

                weights = [70, 15, 15]

            else:

                weights = [90, 5, 5]

        behaviour = random.choices(
            [
                "full",
                "partial",
                "missed"
            ],
            weights=weights,
            k=1
        )[0]

        # -------------------------
        # PAYMENT OUTCOME
        # -------------------------

        if behaviour == "full":

            emi_paid = round(
                emi_due,
                2
            )

            days_late = random.randint(
                0,
                5
            )

            partial_payment_flag = 0

            delinquency_flag = 0

            payment_status = "Paid"

        elif behaviour == "partial":

            emi_paid = round(
                emi_due *
                random.uniform(
                    0.3,
                    0.9
                ),
                2
            )

            days_late = random.randint(
                3,
                20
            )

            partial_payment_flag = 1

            delinquency_flag = (
                1
                if days_late > 15
                else 0
            )

            payment_status = "Partial"

        else:

            emi_paid = 0

            days_late = random.randint(
                30,
                90
            )

            partial_payment_flag = 0

            delinquency_flag = 1

            payment_status = "Missed"

        previous_delinquency = (
            delinquency_flag == 1
        )

        # -------------------------
        # PAYMENT DATE
        # -------------------------

        payment_date = (
            pd.Timestamp(
                loan_start_date
            )
            + pd.DateOffset(
                months=month - 1
            )
        )

        repayments.append({

            "payment_id":
            payment_id,

            "loan_id":
            loan_id,

            "customer_id":
            customer_id,

            "month_number":
            month,

            "emi_due":
            round(emi_due, 2),

            "emi_paid":
            emi_paid,

            "payment_date":
            payment_date.date(),

            "days_late":
            days_late,

            "payment_status":
            payment_status,

            "partial_payment_flag":
            partial_payment_flag,

            "delinquency_flag":
            delinquency_flag
        })

repayments_df = pd.DataFrame(
    repayments
)

repayments_df.to_csv(
    "data/repayments.csv",
    index=False
)

print(
    "repayments.csv generated successfully!"
)

print(
    repayments_df.head()
)

print("\nTotal Records:")
print(
    len(repayments_df)
)

print("\nPayment Status Distribution:")
print(
    repayments_df[
        "payment_status"
    ].value_counts()
)

print("\nDelinquency Rate:")
print(
    repayments_df[
        "delinquency_flag"
    ].value_counts(
        normalize=True
    )
)

print("\nPartial Payment Rate:")
print(
    repayments_df[
        "partial_payment_flag"
    ].value_counts(
        normalize=True
    )
)

print("\nAverage Days Late:")
print(
    round(
        repayments_df[
            "days_late"
        ].mean(),
        2
    )
)
