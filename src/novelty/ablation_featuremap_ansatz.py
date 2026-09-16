"""
Phase 4: Feature map / ansatz ablation for VQC.

The original VQC used exactly one architecture (ZZFeatureMap + RealAmplitudes).
Without varying these components, the paper can't say *why* VQC underperformed
-- was it the encoding, the ansatz, or something more fundamental (as Phase 1's
threshold analysis suggests)? This script grids over
  {ZZFeatureMap, PauliFeatureMap(Z,ZZ)} x {RealAmplitudes, EfficientSU2}
on a single fixed training condition (SMOTE, since it produced the best
original VQC F1/ROC-AUC) and the full test set, matching the original paper's
evaluation protocol so results are directly comparable to Table 7.

Feasibility: confirmed in Phase 0 that all four components construct cleanly
at 4 qubits. 4 configs x ~100s fit (similar to the original SMOTE run) is a
~10 min job.
"""

import time
import numpy as np
import pandas as pd

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
)

from qiskit.circuit.library import zz_feature_map, pauli_feature_map, real_amplitudes, efficient_su2
from qiskit_machine_learning.algorithms import VQC
from qiskit_machine_learning.optimizers import COBYLA

N_QUBITS = 4
FEATURES = ["V10", "V12", "V14", "V17"]
MAX_ITER = 30
TRAIN_PATH = "data/quantum_smote.csv"
TEST_PATH = "data/test_selected.csv"

train_df = pd.read_csv(TRAIN_PATH)
test_df = pd.read_csv(TEST_PATH)

X_train_raw = train_df[FEATURES].values
y_train = train_df["Class"].values
X_test_raw = test_df[FEATURES].values
y_test = test_df["Class"].values

scaler = MinMaxScaler(feature_range=(-np.pi, np.pi))
X_train = scaler.fit_transform(X_train_raw)
X_test = scaler.transform(X_test_raw)

feature_maps = {
    "ZZFeatureMap": lambda: zz_feature_map(feature_dimension=N_QUBITS, reps=2, entanglement="linear"),
    "PauliFeatureMap(Z,ZZ)": lambda: pauli_feature_map(
        feature_dimension=N_QUBITS, reps=2, entanglement="linear", paulis=["Z", "ZZ"]
    ),
}

ansatze = {
    "RealAmplitudes": lambda: real_amplitudes(num_qubits=N_QUBITS, reps=2, entanglement="linear"),
    "EfficientSU2": lambda: efficient_su2(num_qubits=N_QUBITS, reps=2, entanglement="linear"),
}

rows = []

for fm_name, fm_fn in feature_maps.items():
    for an_name, an_fn in ansatze.items():
        print("\n" + "=" * 70)
        print(f"{fm_name} + {an_name}")
        print("=" * 70)

        vqc = VQC(
            feature_map=fm_fn(),
            ansatz=an_fn(),
            optimizer=COBYLA(maxiter=MAX_ITER),
        )

        t0 = time.time()
        vqc.fit(X_train, y_train)
        train_time = time.time() - t0

        y_pred = np.asarray(vqc.predict(X_test)).ravel().astype(int)
        try:
            proba = np.asarray(vqc.predict_proba(X_test))
            y_score = proba[:, 1] if proba.ndim == 2 else proba.ravel()
        except Exception:
            y_score = y_pred

        metrics = {
            "Feature Map": fm_name,
            "Ansatz": an_name,
            "Accuracy": accuracy_score(y_test, y_pred),
            "Precision": precision_score(y_test, y_pred, zero_division=0),
            "Recall": recall_score(y_test, y_pred, zero_division=0),
            "F1 Score": f1_score(y_test, y_pred, zero_division=0),
            "ROC AUC": roc_auc_score(y_test, y_score),
            "Training Time": train_time,
        }
        rows.append(metrics)
        print(f"F1={metrics['F1 Score']:.4f}  ROC-AUC={metrics['ROC AUC']:.4f}  time={train_time:.1f}s")

        pd.DataFrame(rows).to_csv("results/novelty/ablation_featuremap_ansatz.csv", index=False)

result_df = pd.DataFrame(rows)
result_df.to_csv("results/novelty/ablation_featuremap_ansatz.csv", index=False)

print("\n" + "=" * 70)
print(result_df.round(4).to_string(index=False))
print("\nSaved results/novelty/ablation_featuremap_ansatz.csv")
