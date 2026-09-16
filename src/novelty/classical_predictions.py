"""
Phase 1 support script.

Retrains the three classical baselines (Logistic Regression, Random Forest,
SVM) exactly as in src/classical_models.py, but additionally saves the
per-sample predicted fraud probability so a threshold sweep can be run
against them (the original script only saved the default-threshold metrics).
"""

import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

RANDOM_STATE = 42

TRAIN_PATH = "data/train_selected.csv"
SMOTE_PATH = "data/train_smote.csv"
ADASYN_PATH = "data/train_adasyn.csv"
TEST_PATH = "data/test_selected.csv"

SVM_LEGITIMATE_SAMPLES = 20000
SVM_FRAUD_SAMPLES = 20000

train_none = pd.read_csv(TRAIN_PATH)
train_smote = pd.read_csv(SMOTE_PATH)
train_adasyn = pd.read_csv(ADASYN_PATH)
test = pd.read_csv(TEST_PATH)

X_test = test.drop("Class", axis=1)
y_test = test["Class"]

datasets = {
    "None": train_none,
    "SMOTE": train_smote,
    "ADASYN": train_adasyn,
}

rows = []


def create_svm_subset(data, balancing_method):
    legitimate = data[data["Class"] == 0]
    fraud = data[data["Class"] == 1]

    legitimate = legitimate.sample(
        n=min(SVM_LEGITIMATE_SAMPLES, len(legitimate)),
        random_state=RANDOM_STATE,
    )

    if balancing_method == "None":
        fraud = fraud.copy()
    else:
        fraud = fraud.sample(
            n=min(SVM_FRAUD_SAMPLES, len(fraud)),
            random_state=RANDOM_STATE,
        )

    subset = pd.concat([legitimate, fraud])
    return subset.sample(frac=1, random_state=RANDOM_STATE)


for balance_name, train_data in datasets.items():
    X_train = train_data.drop("Class", axis=1)
    y_train = train_data["Class"]

    print(f"Training Logistic Regression + {balance_name} ...")
    lr = LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)
    lr.fit(X_train, y_train)
    proba = lr.predict_proba(X_test)[:, 1]
    for actual, p in zip(y_test.values, proba):
        rows.append({"Model": "Logistic Regression", "Balancing": balance_name,
                      "Actual": int(actual), "Fraud Probability": float(p)})

    print(f"Training Random Forest + {balance_name} ...")
    rf = RandomForestClassifier(n_estimators=100, max_depth=10,
                                 random_state=RANDOM_STATE, n_jobs=-1)
    rf.fit(X_train, y_train)
    proba = rf.predict_proba(X_test)[:, 1]
    for actual, p in zip(y_test.values, proba):
        rows.append({"Model": "Random Forest", "Balancing": balance_name,
                      "Actual": int(actual), "Fraud Probability": float(p)})

    print(f"Training SVM + {balance_name} ...")
    svm_data = create_svm_subset(train_data, balance_name)
    X_svm = svm_data.drop("Class", axis=1)
    y_svm = svm_data["Class"]
    svm = SVC(kernel="rbf", probability=True, random_state=RANDOM_STATE)
    svm.fit(X_svm, y_svm)
    proba = svm.predict_proba(X_test)[:, 1]
    for actual, p in zip(y_test.values, proba):
        rows.append({"Model": "SVM", "Balancing": balance_name,
                      "Actual": int(actual), "Fraud Probability": float(p)})

out = pd.DataFrame(rows)
out.to_csv("results/novelty/classical_predictions.csv", index=False)
print("\nSaved results/novelty/classical_predictions.csv with", len(out), "rows")
