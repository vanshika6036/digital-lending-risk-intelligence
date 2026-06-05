import pandas as pd

customers_df = pd.read_csv(
    "data/customers.csv"
)

loans_df = pd.read_csv(
    "data/loans.csv"
)

final_df = customers_df.merge(
    loans_df,
    on="customer_id"
)

final_df.to_csv(
    "data/final_dataset.csv",
    index=False
)

print(final_df.shape)
print(final_df.head())