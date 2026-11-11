import pandas as pd

df = pd.read_csv("data/creditcard.csv")

print("Dataset shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nClass distribution:")
print(df["Class"].value_counts())

print("\nDataset info:")
print(df.info())