import time
import numpy as np
import pandas as pd

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)

from qiskit.circuit.library import zz_feature_map, real_amplitudes
from qiskit_machine_learning.algorithms import VQC
from qiskit_machine_learning.optimizers import COBYLA


# =========================================================
# CONFIGURATION
# =========================================================

RANDOM_STATE = 42
N_QUBITS = 4

TRAIN_PATH = "data/quantum_adasyn.csv"
TEST_PATH = "data/test_selected.csv"

FEATURES = ["V10", "V12", "V14", "V17"]

MAX_ITER = 30


# =========================================================
# LOAD DATA
# =========================================================

print("=" * 70)
print("VQC TRAINING")
print("=" * 70)

train_df = pd.read_csv(TRAIN_PATH)
test_df = pd.read_csv(TEST_PATH)

X_train = train_df[FEATURES].values
y_train = train_df["Class"].values

X_test = test_df[FEATURES].values
y_test = test_df["Class"].values

print("\nTraining data:")
print(X_train.shape)

print("\nTraining class distribution:")
print(pd.Series(y_train).value_counts())

print("\nTest data:")
print(X_test.shape)

print("\nTest class distribution:")
print(pd.Series(y_test).value_counts())


# =========================================================
# SCALE FEATURES
# =========================================================

scaler = MinMaxScaler(
    feature_range=(-np.pi, np.pi)
)

X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)


# =========================================================
# QUANTUM FEATURE MAP
# =========================================================

feature_map = zz_feature_map(
    feature_dimension=N_QUBITS,
    reps=2,
    entanglement="linear"
)


# =========================================================
# VARIATIONAL ANSATZ
# =========================================================

ansatz = real_amplitudes(
    num_qubits=N_QUBITS,
    reps=2,
    entanglement="linear"
)


# =========================================================
# OPTIMIZER
# =========================================================

optimizer = COBYLA(
    maxiter=MAX_ITER
)


# =========================================================
# VQC
# =========================================================

vqc = VQC(
    feature_map=feature_map,
    ansatz=ansatz,
    optimizer=optimizer
)


# =========================================================
# TRAIN
# =========================================================

print("\n" + "=" * 70)
print("STARTING VQC TRAINING")
print("=" * 70)

start_time = time.time()

vqc.fit(X_train, y_train)

training_time = time.time() - start_time

print("\nVQC training completed.")
print(f"Training time: {training_time:.2f} seconds")


# =========================================================
# PREDICTIONS
# =========================================================

print("\n" + "=" * 70)
print("EVALUATING VQC")
print("=" * 70)

y_pred = np.asarray(
    vqc.predict(X_test)
).ravel().astype(int)


# =========================================================
# PROBABILITY / SCORE OUTPUT
# =========================================================

try:

    probabilities = vqc.predict_proba(X_test)

    probabilities = np.asarray(probabilities)

    if probabilities.ndim == 2:
        y_score = probabilities[:, 1]
    else:
        y_score = probabilities.ravel()

    roc_auc = roc_auc_score(
        y_test,
        y_score
    )

except Exception as error:

    print("\nProbability output unavailable.")
    print("Using hard predictions for ROC AUC.")
    print("Reason:", error)

    y_score = y_pred

    roc_auc = roc_auc_score(
        y_test,
        y_score
    )


# =========================================================
# METRICS
# =========================================================

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


# =========================================================
# RESULTS
# =========================================================

print("\n" + "=" * 70)
print("VQC RESULTS")
print("=" * 70)

print(f"Accuracy:       {accuracy:.4f}")
print(f"Precision:      {precision:.4f}")
print(f"Recall:         {recall:.4f}")
print(f"F1 Score:       {f1:.4f}")
print(f"ROC AUC:        {roc_auc:.4f}")
print(f"Training Time:  {training_time:.2f} seconds")

print("\n" + "=" * 70)
print("VQC EXPERIMENT COMPLETED")
print("=" * 70)