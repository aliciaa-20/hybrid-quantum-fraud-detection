import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ============================================================
# LOAD DATASET
# ============================================================

df = pd.read_csv("data/creditcard.csv")

print("=" * 70)
print("EXPLORATORY DATA ANALYSIS")
print("=" * 70)

# ============================================================
# BASIC INFORMATION
# ============================================================

print("\nDataset Shape:")
print(df.shape)

print("\nMissing Values:")
print(df.isnull().sum().sum())

print("\nDuplicate Rows:")
print(df.duplicated().sum())

print("\nData Types:")
print(df.dtypes)

# ============================================================
# CLASS DISTRIBUTION
# ============================================================

print("\nClass Distribution:")
print(df["Class"].value_counts())

print("\nClass Distribution (%):")
print(
    df["Class"]
    .value_counts(normalize=True)
    .mul(100)
    .round(4)
)

# ============================================================
# CLASS DISTRIBUTION PLOT
# ============================================================

plt.figure(figsize=(7, 5))

sns.countplot(
    data=df,
    x="Class"
)

plt.title("Credit Card Transaction Class Distribution")
plt.xlabel("Class (0 = Legitimate, 1 = Fraud)")
plt.ylabel("Number of Transactions")

plt.tight_layout()
plt.show()

# ============================================================
# TRANSACTION AMOUNT
# ============================================================

print("\nTransaction Amount Statistics:")
print(df["Amount"].describe())

plt.figure(figsize=(8, 5))

plt.hist(
    df["Amount"],
    bins=50
)

plt.title("Transaction Amount Distribution")
plt.xlabel("Transaction Amount")
plt.ylabel("Frequency")

plt.tight_layout()
plt.show()

# ============================================================
# FRAUD VS LEGITIMATE AMOUNT
# ============================================================

plt.figure(figsize=(8, 5))

sns.boxplot(
    data=df,
    x="Class",
    y="Amount"
)

plt.title("Transaction Amount: Fraud vs Legitimate")
plt.xlabel("Class (0 = Legitimate, 1 = Fraud)")
plt.ylabel("Amount")

plt.tight_layout()
plt.show()

# ============================================================
# TRANSACTION TIME
# ============================================================

plt.figure(figsize=(8, 5))

plt.hist(
    df["Time"],
    bins=50
)

plt.title("Transaction Time Distribution")
plt.xlabel("Time")
plt.ylabel("Frequency")

plt.tight_layout()
plt.show()

# ============================================================
# CORRELATION WITH TARGET
# ============================================================

correlations = (
    df.corr(numeric_only=True)["Class"]
    .drop("Class")
    .sort_values()
)

print("\nFeatures with lowest correlation to fraud:")
print(correlations.head(10))

print("\nFeatures with highest correlation to fraud:")
print(correlations.tail(10))

# ============================================================
# CORRELATION PLOT
# ============================================================

plt.figure(figsize=(10, 8))

correlations.plot(
    kind="barh"
)

plt.title("Feature Correlation with Fraud Class")
plt.xlabel("Correlation")

plt.tight_layout()
plt.show()

# ============================================================
# FRAUD TRANSACTION SUMMARY
# ============================================================

fraud = df[df["Class"] == 1]
legitimate = df[df["Class"] == 0]

print("\n" + "=" * 70)
print("FRAUD TRANSACTION SUMMARY")
print("=" * 70)

print("\nNumber of fraud transactions:")
print(len(fraud))

print("\nAverage fraud transaction amount:")
print(round(fraud["Amount"].mean(), 2))

print("\nMaximum fraud transaction amount:")
print(round(fraud["Amount"].max(), 2))

print("\nMinimum fraud transaction amount:")
print(round(fraud["Amount"].min(), 2))

print("\nAverage legitimate transaction amount:")
print(round(legitimate["Amount"].mean(), 2))

print("\nEDA completed.")