import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, mutual_info_classif


# ============================================================
# CONFIGURATION
# ============================================================

DATA_PATH = "data/creditcard.csv"

RANDOM_STATE = 42
TEST_SIZE = 0.20
N_FEATURES = 4


# ============================================================
# 1. LOAD DATA
# ============================================================

print("=" * 70)
print("PREPROCESSING AND FEATURE SELECTION")
print("=" * 70)

df = pd.read_csv(DATA_PATH)

print("\nOriginal dataset shape:")
print(df.shape)


# ============================================================
# 2. REMOVE DUPLICATES
# ============================================================

duplicate_count = df.duplicated().sum()

print("\nDuplicate rows found:", duplicate_count)

df = df.drop_duplicates()

print("Shape after removing duplicates:")
print(df.shape)


# ============================================================
# 3. CHECK MISSING VALUES
# ============================================================

missing_values = df.isnull().sum().sum()

print("\nMissing values:", missing_values)

if missing_values > 0:
    df = df.dropna()

    print("Shape after removing missing values:")
    print(df.shape)


# ============================================================
# 4. SEPARATE FEATURES AND TARGET
# ============================================================

X = df.drop("Class", axis=1)
y = df["Class"]

print("\nNumber of input features:", X.shape[1])
print("Target:", "Class")


# ============================================================
# 5. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE,
    stratify=y
)

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))

print("\nTraining class distribution:")
print(y_train.value_counts())

print("\nTesting class distribution:")
print(y_test.value_counts())


# ============================================================
# 6. STANDARDIZATION
# ============================================================

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

X_train_scaled = pd.DataFrame(
    X_train_scaled,
    columns=X_train.columns,
    index=X_train.index
)

X_test_scaled = pd.DataFrame(
    X_test_scaled,
    columns=X_test.columns,
    index=X_test.index
)


# ============================================================
# 7. MUTUAL INFORMATION FEATURE SELECTION
# ============================================================

print("\n" + "=" * 70)
print("MUTUAL INFORMATION FEATURE SELECTION")
print("=" * 70)

selector = SelectKBest(
    score_func=mutual_info_classif,
    k=N_FEATURES
)

X_train_selected = selector.fit_transform(
    X_train_scaled,
    y_train
)

X_test_selected = selector.transform(
    X_test_scaled
)


# ============================================================
# 8. IDENTIFY SELECTED FEATURES
# ============================================================

selected_features = X_train_scaled.columns[
    selector.get_support()
]

print("\nSelected features:")

for i, feature in enumerate(selected_features, start=1):
    print(f"{i}. {feature}")


# ============================================================
# 9. DISPLAY FEATURE SCORES
# ============================================================

feature_scores = pd.DataFrame({
    "Feature": X_train_scaled.columns,
    "Mutual Information Score": selector.scores_
})

feature_scores = feature_scores.sort_values(
    by="Mutual Information Score",
    ascending=False
)

print("\nAll feature scores:")
print(
    feature_scores.to_string(
        index=False
    )
)


# ============================================================
# 10. FINAL SHAPES
# ============================================================

print("\n" + "=" * 70)
print("FINAL PREPROCESSED DATA")
print("=" * 70)

print("\nX_train shape:", X_train_selected.shape)
print("X_test shape :", X_test_selected.shape)

print("\nSelected feature names:")
print(list(selected_features))


# ============================================================
# 11. SAVE SELECTED DATA
# ============================================================

train_selected = pd.DataFrame(
    X_train_selected,
    columns=selected_features
)

train_selected["Class"] = y_train.values

test_selected = pd.DataFrame(
    X_test_selected,
    columns=selected_features
)

test_selected["Class"] = y_test.values


train_selected.to_csv(
    "data/train_selected.csv",
    index=False
)

test_selected.to_csv(
    "data/test_selected.csv",
    index=False
)

print("\nSaved:")
print("data/train_selected.csv")
print("data/test_selected.csv")

print("\nPreprocessing completed successfully.")