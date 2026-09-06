import time
import pandas as pd
import numpy as np

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_STATE = 42

TRAIN_PATH = "data/train_selected.csv"
SMOTE_PATH = "data/train_smote.csv"
ADASYN_PATH = "data/train_adasyn.csv"

TEST_PATH = "data/test_selected.csv"

# Only used for SVM
SVM_LEGITIMATE_SAMPLES = 20000
SVM_FRAUD_SAMPLES = 20000


# ============================================================
# LOAD DATA
# ============================================================

train_none = pd.read_csv(TRAIN_PATH)
train_smote = pd.read_csv(SMOTE_PATH)
train_adasyn = pd.read_csv(ADASYN_PATH)

test = pd.read_csv(TEST_PATH)


# ============================================================
# TEST DATA
# ============================================================

X_test = test.drop("Class", axis=1)
y_test = test["Class"]


# ============================================================
# TRAINING DATASETS
# ============================================================

datasets = {
    "None": train_none,
    "SMOTE": train_smote,
    "ADASYN": train_adasyn
}


# ============================================================
# RESULTS
# ============================================================

results = []


# ============================================================
# HELPER FUNCTION
# ============================================================

def create_svm_subset(data, balancing_method):

    legitimate = data[
        data["Class"] == 0
    ]

    fraud = data[
        data["Class"] == 1
    ]

    # --------------------------------------------------------
    # No balancing
    # --------------------------------------------------------

    if balancing_method == "None":

        legitimate = legitimate.sample(
            n=min(
                SVM_LEGITIMATE_SAMPLES,
                len(legitimate)
            ),
            random_state=RANDOM_STATE
        )

        # Keep all available fraud samples
        fraud = fraud.copy()

    # --------------------------------------------------------
    # SMOTE / ADASYN
    # --------------------------------------------------------

    else:

        legitimate = legitimate.sample(
            n=min(
                SVM_LEGITIMATE_SAMPLES,
                len(legitimate)
            ),
            random_state=RANDOM_STATE
        )

        fraud = fraud.sample(
            n=min(
                SVM_FRAUD_SAMPLES,
                len(fraud)
            ),
            random_state=RANDOM_STATE
        )

    subset = pd.concat(
        [legitimate, fraud]
    )

    subset = subset.sample(
        frac=1,
        random_state=RANDOM_STATE
    )

    return subset


# ============================================================
# LOGISTIC REGRESSION
# ============================================================

def run_logistic_regression(
    X_train,
    y_train,
    balance_name
):

    print("\n" + "-" * 60)
    print(
        "Logistic Regression +",
        balance_name
    )
    print("-" * 60)

    model = LogisticRegression(
        max_iter=1000,
        random_state=RANDOM_STATE
    )

    start = time.time()

    model.fit(
        X_train,
        y_train
    )

    training_time = time.time() - start

    predictions = model.predict(
        X_test
    )

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    metrics = calculate_metrics(
        predictions,
        probabilities
    )

    print_metrics(
        metrics,
        training_time
    )

    results.append({
        "Model": "Logistic Regression",
        "Balancing": balance_name,
        **metrics,
        "Training Time": training_time
    })


# ============================================================
# RANDOM FOREST
# ============================================================

def run_random_forest(
    X_train,
    y_train,
    balance_name
):

    print("\n" + "-" * 60)
    print(
        "Random Forest +",
        balance_name
    )
    print("-" * 60)

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=RANDOM_STATE,
        n_jobs=-1
    )

    start = time.time()

    model.fit(
        X_train,
        y_train
    )

    training_time = time.time() - start

    predictions = model.predict(
        X_test
    )

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    metrics = calculate_metrics(
        predictions,
        probabilities
    )

    print_metrics(
        metrics,
        training_time
    )

    results.append({
        "Model": "Random Forest",
        "Balancing": balance_name,
        **metrics,
        "Training Time": training_time
    })


# ============================================================
# SVM
# ============================================================

def run_svm(
    train_data,
    balance_name
):

    print("\n" + "-" * 60)
    print(
        "SVM +",
        balance_name
    )
    print("-" * 60)

    # Create manageable subset
    svm_data = create_svm_subset(
        train_data,
        balance_name
    )

    X_train = svm_data.drop(
        "Class",
        axis=1
    )

    y_train = svm_data["Class"]

    print(
        "SVM training samples:",
        len(X_train)
    )

    print(
        "Legitimate:",
        int((y_train == 0).sum())
    )

    print(
        "Fraud:",
        int((y_train == 1).sum())
    )

    model = SVC(
        kernel="rbf",
        probability=True,
        random_state=RANDOM_STATE
    )

    start = time.time()

    model.fit(
        X_train,
        y_train
    )

    training_time = time.time() - start

    predictions = model.predict(
        X_test
    )

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    metrics = calculate_metrics(
        predictions,
        probabilities
    )

    print_metrics(
        metrics,
        training_time
    )

    results.append({
        "Model": "SVM",
        "Balancing": balance_name,
        **metrics,
        "Training Time": training_time
    })


# ============================================================
# METRIC CALCULATION
# ============================================================

def calculate_metrics(
    predictions,
    probabilities
):

    return {
        "Accuracy": accuracy_score(
            y_test,
            predictions
        ),

        "Precision": precision_score(
            y_test,
            predictions,
            zero_division=0
        ),

        "Recall": recall_score(
            y_test,
            predictions,
            zero_division=0
        ),

        "F1 Score": f1_score(
            y_test,
            predictions,
            zero_division=0
        ),

        "ROC AUC": roc_auc_score(
            y_test,
            probabilities
        )
    }


# ============================================================
# PRINT METRICS
# ============================================================

def print_metrics(
    metrics,
    training_time
):

    print(
        f"Accuracy       : {metrics['Accuracy']:.4f}"
    )

    print(
        f"Precision      : {metrics['Precision']:.4f}"
    )

    print(
        f"Recall         : {metrics['Recall']:.4f}"
    )

    print(
        f"F1 Score       : {metrics['F1 Score']:.4f}"
    )

    print(
        f"ROC-AUC        : {metrics['ROC AUC']:.4f}"
    )

    print(
        f"Training Time  : {training_time:.4f} seconds"
    )


# ============================================================
# RUN EXPERIMENTS
# ============================================================

print("=" * 80)
print("CLASSICAL MACHINE LEARNING BASELINES")
print("=" * 80)


for balance_name, train_data in datasets.items():

    print("\n\n")
    print("=" * 80)
    print(
        "BALANCING METHOD:",
        balance_name
    )
    print("=" * 80)

    X_train = train_data.drop(
        "Class",
        axis=1
    )

    y_train = train_data["Class"]

    # Logistic Regression
    run_logistic_regression(
        X_train,
        y_train,
        balance_name
    )

    # Random Forest
    run_random_forest(
        X_train,
        y_train,
        balance_name
    )

    # SVM
    run_svm(
        train_data,
        balance_name
    )


# ============================================================
# FINAL RESULTS
# ============================================================

results_df = pd.DataFrame(
    results
)


print("\n\n")

print("=" * 80)
print("FINAL CLASSICAL MODEL COMPARISON")
print("=" * 80)

print(
    results_df.round(4).to_string(
        index=False
    )
)


# ============================================================
# SORT BY F1
# ============================================================

print("\n\n")

print("=" * 80)
print("MODELS SORTED BY F1 SCORE")
print("=" * 80)

sorted_results = results_df.sort_values(
    by="F1 Score",
    ascending=False
)

print(
    sorted_results.round(4).to_string(
        index=False
    )
)


# ============================================================
# SAVE
# ============================================================

results_df.to_csv(
    "results/classical_results.csv",
    index=False
)

print("\nResults saved to:")
print("results/classical_results.csv")

print("\nClassical experiments completed.")