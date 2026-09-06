import pandas as pd
from imblearn.over_sampling import SMOTE, ADASYN

RANDOM_STATE = 42

TRAIN_PATH = "data/train_selected.csv"

N_FRAUD = 100
N_LEGITIMATE = 900


print("=" * 70)
print("QUANTUM DATASET PREPARATION")
print("=" * 70)


# ---------------------------------------------------------
# LOAD TRAINING DATA
# ---------------------------------------------------------

df = pd.read_csv(TRAIN_PATH)

fraud = df[df["Class"] == 1]
legitimate = df[df["Class"] == 0]


# ---------------------------------------------------------
# CREATE COMMON IMBALANCED QUANTUM DATASET
# ---------------------------------------------------------

fraud_sample = fraud.sample(
    n=N_FRAUD,
    random_state=RANDOM_STATE
)

legitimate_sample = legitimate.sample(
    n=N_LEGITIMATE,
    random_state=RANDOM_STATE
)

quantum_none = pd.concat(
    [legitimate_sample, fraud_sample]
).sample(
    frac=1,
    random_state=RANDOM_STATE
).reset_index(drop=True)


X_none = quantum_none.drop("Class", axis=1)
y_none = quantum_none["Class"]


print("\nOriginal quantum dataset:")
print(y_none.value_counts())


# ---------------------------------------------------------
# SMOTE
# ---------------------------------------------------------

smote = SMOTE(random_state=RANDOM_STATE)

X_smote, y_smote = smote.fit_resample(
    X_none,
    y_none
)

quantum_smote = pd.DataFrame(
    X_smote,
    columns=X_none.columns
)

quantum_smote["Class"] = y_smote


print("\nSMOTE quantum dataset:")
print(y_smote.value_counts())


# ---------------------------------------------------------
# ADASYN
# ---------------------------------------------------------

adasyn = ADASYN(random_state=RANDOM_STATE)

X_adasyn, y_adasyn = adasyn.fit_resample(
    X_none,
    y_none
)

quantum_adasyn = pd.DataFrame(
    X_adasyn,
    columns=X_none.columns
)

quantum_adasyn["Class"] = y_adasyn


print("\nADASYN quantum dataset:")
print(y_adasyn.value_counts())


# ---------------------------------------------------------
# SAVE DATASETS
# ---------------------------------------------------------

quantum_none.to_csv(
    "data/quantum_none.csv",
    index=False
)

quantum_smote.to_csv(
    "data/quantum_smote.csv",
    index=False
)

quantum_adasyn.to_csv(
    "data/quantum_adasyn.csv",
    index=False
)


print("\n" + "=" * 70)
print("FILES SAVED")
print("=" * 70)

print("data/quantum_none.csv")
print("data/quantum_smote.csv")
print("data/quantum_adasyn.csv")

print("\nQuantum dataset preparation completed.")