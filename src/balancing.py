import pandas as pd
import numpy as np

from imblearn.over_sampling import SMOTE, ADASYN


# ============================================================
# CONFIGURATION
# ============================================================

TRAIN_PATH = "data/train_selected.csv"

RANDOM_STATE = 42


# ============================================================
# LOAD SELECTED TRAINING DATA
# ============================================================

df = pd.read_csv(TRAIN_PATH)

X = df.drop("Class", axis=1)
y = df["Class"]


print("=" * 70)
print("CLASS IMBALANCE HANDLING")
print("=" * 70)

print("\nOriginal training distribution:")
print(y.value_counts())


# ============================================================
# 1. NO BALANCING
# ============================================================

X_none = X.copy()
y_none = y.copy()

print("\n" + "-" * 70)
print("NO BALANCING")
print("-" * 70)

print(y_none.value_counts())


# ============================================================
# 2. SMOTE
# ============================================================

print("\n" + "-" * 70)
print("SMOTE")
print("-" * 70)

smote = SMOTE(
    random_state=RANDOM_STATE
)

X_smote, y_smote = smote.fit_resample(
    X,
    y
)

print("\nAfter SMOTE:")
print(
    pd.Series(y_smote).value_counts()
)


# ============================================================
# 3. ADASYN
# ============================================================

print("\n" + "-" * 70)
print("ADASYN")
print("-" * 70)

adasyn = ADASYN(
    random_state=RANDOM_STATE
)

X_adasyn, y_adasyn = adasyn.fit_resample(
    X,
    y
)

print("\nAfter ADASYN:")
print(
    pd.Series(y_adasyn).value_counts()
)


# ============================================================
# 4. SAVE BALANCED DATASETS
# ============================================================

smote_df = pd.DataFrame(
    X_smote,
    columns=X.columns
)

smote_df["Class"] = y_smote

adasyn_df = pd.DataFrame(
    X_adasyn,
    columns=X.columns
)

adasyn_df["Class"] = y_adasyn


smote_df.to_csv(
    "data/train_smote.csv",
    index=False
)

adasyn_df.to_csv(
    "data/train_adasyn.csv",
    index=False
)


print("\n" + "=" * 70)
print("FILES SAVED")
print("=" * 70)

print("\ndata/train_smote.csv")
print("data/train_adasyn.csv")

print("\nBalancing completed.")