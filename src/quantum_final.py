import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    ConfusionMatrixDisplay
)

from qiskit.circuit.library import zz_feature_map, real_amplitudes
from qiskit_machine_learning.algorithms import VQC
from qiskit_machine_learning.optimizers import COBYLA


# =========================================================
# CONFIGURATION
# =========================================================

RANDOM_STATE = 42

N_QUBITS = 4
MAX_ITER = 30

FEATURES = [
    "V10",
    "V12",
    "V14",
    "V17"
]

TEST_PATH = "data/test_selected.csv"

DATASETS = {
    "None": "data/quantum_none.csv",
    "SMOTE": "data/quantum_smote.csv",
    "ADASYN": "data/quantum_adasyn.csv"
}


# =========================================================
# CREATE RESULTS DIRECTORY
# =========================================================

os.makedirs(
    "results",
    exist_ok=True
)


# =========================================================
# LOAD TEST DATA
# =========================================================

test_df = pd.read_csv(
    TEST_PATH
)

X_test_original = test_df[FEATURES].values
y_test = test_df["Class"].values


print("=" * 80)
print("FINAL QUANTUM MODEL EVALUATION")
print("=" * 80)

print("\nTest dataset:")
print(X_test_original.shape)

print("\nTest class distribution:")
print(
    pd.Series(y_test).value_counts()
)


# =========================================================
# STORE RESULTS
# =========================================================

all_results = []
all_predictions = []


# =========================================================
# RUN VQC FOR EACH BALANCING METHOD
# =========================================================

for balancing, train_path in DATASETS.items():

    print("\n")
    print("=" * 80)
    print(f"VQC + {balancing}")
    print("=" * 80)

    # -----------------------------------------------------
    # LOAD TRAINING DATA
    # -----------------------------------------------------

    train_df = pd.read_csv(
        train_path
    )

    X_train_original = train_df[FEATURES].values
    y_train = train_df["Class"].values

    print("\nTraining data:")
    print(X_train_original.shape)

    print("\nTraining class distribution:")
    print(
        pd.Series(y_train).value_counts()
    )


    # -----------------------------------------------------
    # SCALE DATA
    # -----------------------------------------------------

    scaler = MinMaxScaler(
        feature_range=(-np.pi, np.pi)
    )

    X_train = scaler.fit_transform(
        X_train_original
    )

    X_test = scaler.transform(
        X_test_original
    )


    # -----------------------------------------------------
    # QUANTUM FEATURE MAP
    # -----------------------------------------------------

    feature_map = zz_feature_map(
        feature_dimension=N_QUBITS,
        reps=2,
        entanglement="linear"
    )


    # -----------------------------------------------------
    # VARIATIONAL ANSATZ
    # -----------------------------------------------------

    ansatz = real_amplitudes(
        num_qubits=N_QUBITS,
        reps=2,
        entanglement="linear"
    )


    # -----------------------------------------------------
    # OPTIMIZER
    # -----------------------------------------------------

    optimizer = COBYLA(
        maxiter=MAX_ITER
    )


    # -----------------------------------------------------
    # CREATE VQC
    # -----------------------------------------------------

    vqc = VQC(
        feature_map=feature_map,
        ansatz=ansatz,
        optimizer=optimizer
    )


    # -----------------------------------------------------
    # TRAIN
    # -----------------------------------------------------

    print("\nStarting training...")

    start_time = time.time()

    vqc.fit(
        X_train,
        y_train
    )

    training_time = (
        time.time() - start_time
    )

    print(
        f"Training completed in "
        f"{training_time:.2f} seconds"
    )


    # -----------------------------------------------------
    # PREDICTIONS
    # -----------------------------------------------------

    print("\nGenerating predictions...")

    y_pred = np.asarray(
        vqc.predict(X_test)
    ).ravel().astype(int)


    # -----------------------------------------------------
    # PROBABILITIES
    # -----------------------------------------------------

    try:

        probabilities = vqc.predict_proba(
            X_test
        )

        probabilities = np.asarray(
            probabilities
        )

        if probabilities.ndim == 2:

            y_score = probabilities[:, 1]

        else:

            y_score = probabilities.ravel()

        roc_auc = roc_auc_score(
            y_test,
            y_score
        )

    except Exception as error:

        print(
            "\nProbability output unavailable."
        )

        print(
            "Reason:",
            error
        )

        y_score = y_pred

        roc_auc = roc_auc_score(
            y_test,
            y_score
        )


    # -----------------------------------------------------
    # METRICS
    # -----------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    precision = precision_score(
        y_test,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        y_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        y_pred,
        zero_division=0
    )


    # -----------------------------------------------------
    # STORE METRICS
    # -----------------------------------------------------

    all_results.append({

        "Model": "VQC",

        "Balancing": balancing,

        "Accuracy": accuracy,

        "Precision": precision,

        "Recall": recall,

        "F1 Score": f1,

        "ROC AUC": roc_auc,

        "Training Time": training_time

    })


    # -----------------------------------------------------
    # STORE PREDICTIONS
    # -----------------------------------------------------

    prediction_df = pd.DataFrame({

        "Balancing": balancing,

        "Actual": y_test,

        "Predicted": y_pred,

        "Fraud Probability": y_score

    })

    all_predictions.append(
        prediction_df
    )


    # -----------------------------------------------------
    # CONFUSION MATRIX
    # -----------------------------------------------------

    cm = confusion_matrix(
        y_test,
        y_pred
    )

    print("\nConfusion Matrix:")
    print(cm)


    display = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=[
            "Legitimate",
            "Fraud"
        ]
    )

    display.plot()

    plt.title(
        f"Confusion Matrix: VQC + {balancing}"
    )

    plt.tight_layout()


    filename = (
        "results/"
        + f"vqc_{balancing.lower()}"
        + "_confusion_matrix.png"
    )

    plt.savefig(
        filename,
        dpi=300
    )

    plt.close()

    print(
        f"Saved: {filename}"
    )


    # -----------------------------------------------------
    # DISPLAY RESULTS
    # -----------------------------------------------------

    print("\nResults:")
    print(
        f"Accuracy:       {accuracy:.4f}"
    )
    print(
        f"Precision:      {precision:.4f}"
    )
    print(
        f"Recall:         {recall:.4f}"
    )
    print(
        f"F1 Score:       {f1:.4f}"
    )
    print(
        f"ROC AUC:        {roc_auc:.4f}"
    )
    print(
        f"Training Time:  {training_time:.2f} seconds"
    )


# =========================================================
# SAVE QUANTUM RESULTS
# =========================================================

quantum_results = pd.DataFrame(
    all_results
)

quantum_results.to_csv(
    "results/quantum_results.csv",
    index=False
)


# =========================================================
# SAVE ALL PREDICTIONS
# =========================================================

quantum_predictions = pd.concat(
    all_predictions,
    ignore_index=True
)

quantum_predictions.to_csv(
    "results/quantum_predictions.csv",
    index=False
)


# =========================================================
# DISPLAY FINAL QUANTUM RESULTS
# =========================================================

print("\n")
print("=" * 80)
print("FINAL QUANTUM RESULTS")
print("=" * 80)

print(
    quantum_results.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


# =========================================================
# FINAL FILE LIST
# =========================================================

print("\n")
print("=" * 80)
print("FILES GENERATED")
print("=" * 80)

print(
    "results/quantum_results.csv"
)

print(
    "results/quantum_predictions.csv"
)

print(
    "results/vqc_none_confusion_matrix.png"
)

print(
    "results/vqc_smote_confusion_matrix.png"
)

print(
    "results/vqc_adasyn_confusion_matrix.png"
)

print("\n")
print("=" * 80)
print("FINAL QUANTUM EVALUATION COMPLETED")
print("=" * 80)