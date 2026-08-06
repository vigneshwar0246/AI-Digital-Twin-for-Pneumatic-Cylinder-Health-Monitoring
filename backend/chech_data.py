import pandas as pd

df = pd.read_csv("datasets/simulated/pneumatic_dataset.csv")

print("Rows    :", len(df))
print("Columns :", len(df.columns))

print("\nColumns:")
print(df.columns)

print("\nFirst 5 Rows:")
print(df.head())

print("\nLast 5 Rows:")
print(df.tail())