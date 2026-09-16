"""
Phase 2: Quantum Kernel classifier (QSVM).

Adds a second quantum method (a ZZFeatureMap fidelity quantum kernel + SVC)
alongside the VQC, so the "hybrid quantum ML framework" compares more than
one quantum approach, not just VQC vs. classical.

Feasibility note (see PHASES.md Phase 0/2): a quantum kernel is pairwise
(train x test circuit evaluations), unlike VQC's per-sample forward pass, so
it cannot be evaluated on the full 56,747-row test set in reasonable time.
A small-scale timing test (60x60) measured ~26.5 evals/sec (train-train,
symmetric) and ~103 evals/sec (test-train). To keep total runtime bounded
(~10 min per balancing condition), this script uses:
  - a 120-row training subsample per balancing condition (from the same
    quantum_none/smote/adasyn.csv files VQC trains on)
  - a fixed 250-row evaluation subset containing ALL 95 fraud cases in the
    test set plus 155 randomly sampled legitimate cases (~38% fraud rate)

This evaluation subset is deliberately class-enriched (real-world fraud
rate is ~0.17%) purely to make kernel computation tractable while still
having enough positive examples to compute meaningful precision/recall.
Because of this, QSVM/VQC numbers on this subset are NOT directly
comparable in absolute terms to the full-test-set VQC numbers reported
elsewhere -- they exist only for a fair, matched QSVM vs. VQC comparison,
evaluated on the identical subset for both.
"""

import time
import numpy as np
import pandas as pd

from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
)

from qiskit.circuit.library import zz_feature_map, real_amplitudes
from qiskit_machine_learning.kernels import FidelityQuantumKernel
from qiskit_machine_learning.algorithms import VQC
from qiskit_machine_learning.optimizers import COBYLA

RANDOM_STATE = 42
N_QUBITS = 4
FEATURES = ["V10", "V12", "V14", "V17"]

TRAIN_N = 120
EVAL_LEGIT_N = 155

DATASETS = {
    "None": "data/quantum_none.csv",
    "SMOTE": "data/quantum_smote.csv",
    "ADASYN": "data/quantum_adasyn.csv",
}

# ------------------------------------------------------------------
# Build the fixed, class-enriched evaluation subset (shared across all
# balancing conditions and across QSVM/VQC so the comparison is fair)
# ------------------------------------------------------------------

test_df = pd.read_csv("data/test_selected.csv")
fraud_eval = test_df[test_df["Class"] == 1]
legit_eval = test_df[test_df["Class"] == 0].sample(
    n=EVAL_LEGIT_N, random_state=RANDOM_STATE
)
eval_df = pd.concat([fraud_eval, legit_eval]).sample(
    frac=1, random_state=RANDOM_STATE
).reset_index(drop=True)

X_eval_raw = eval_df[FEATURES].values
y_eval = eval_df["Class"].values

print("Evaluation subset:", eval_df.shape, "fraud:", int(y_eval.sum()))

rows = []
prediction_rows = []

for balancing, path in DATASETS.items():
    print("\n" + "=" * 70)
    print(f"QSVM + {balancing}")
    print("=" * 70)

    train_df = pd.read_csv(path)
    fraud_tr = train_df[train_df["Class"] == 1]
    legit_tr = train_df[train_df["Class"] == 0]
    n_fraud = min(len(fraud_tr), TRAIN_N // 2)
    n_legit = TRAIN_N - n_fraud
    train_sub = pd.concat([
        fraud_tr.sample(n=n_fraud, random_state=RANDOM_STATE),
        legit_tr.sample(n=min(n_legit, len(legit_tr)), random_state=RANDOM_STATE),
    ]).sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)

    X_train_raw = train_sub[FEATURES].values
    y_train = train_sub["Class"].values

    print("Train subset:", X_train_raw.shape, "fraud:", int(y_train.sum()))

    scaler = MinMaxScaler(feature_range=(-np.pi, np.pi))
    X_train = scaler.fit_transform(X_train_raw)
    X_eval = scaler.transform(X_eval_raw)

    feature_map = zz_feature_map(feature_dimension=N_QUBITS, reps=2, entanglement="linear")
    kernel = FidelityQuantumKernel(feature_map=feature_map)

    # ---------------- QSVM ----------------
    t0 = time.time()
    K_train = kernel.evaluate(x_vec=X_train)
    t1 = time.time()
    K_eval = kernel.evaluate(x_vec=X_eval, y_vec=X_train)
    t2 = time.time()

    print(f"train-train kernel: {t1 - t0:.1f}s | eval-train kernel: {t2 - t1:.1f}s")

    svc = SVC(kernel="precomputed", probability=True, random_state=RANDOM_STATE)
    qsvm_start = time.time()
    svc.fit(K_train, y_train)
    qsvm_train_time = (time.time() - qsvm_start) + (t1 - t0)

    y_pred = svc.predict(K_eval)
    y_score = svc.predict_proba(K_eval)[:, 1]

    rows.append({
        "Model": "QSVM", "Balancing": balancing,
        "Accuracy": accuracy_score(y_eval, y_pred),
        "Precision": precision_score(y_eval, y_pred, zero_division=0),
        "Recall": recall_score(y_eval, y_pred, zero_division=0),
        "F1 Score": f1_score(y_eval, y_pred, zero_division=0),
        "ROC AUC": roc_auc_score(y_eval, y_score),
        "Training Time": qsvm_train_time,
        "Kernel Time (train+eval)": (t1 - t0) + (t2 - t1),
    })

    # ---------------- VQC on the SAME subset, for a fair comparison ----------------
    ansatz = real_amplitudes(num_qubits=N_QUBITS, reps=2, entanglement="linear")
    vqc = VQC(feature_map=feature_map, ansatz=ansatz, optimizer=COBYLA(maxiter=30))

    vqc_start = time.time()
    vqc.fit(X_train, y_train)
    vqc_train_time = time.time() - vqc_start

    y_pred_vqc = np.asarray(vqc.predict(X_eval)).ravel().astype(int)
    try:
        proba = np.asarray(vqc.predict_proba(X_eval))
        y_score_vqc = proba[:, 1] if proba.ndim == 2 else proba.ravel()
    except Exception:
        y_score_vqc = y_pred_vqc

    rows.append({
        "Model": "VQC (matched subset)", "Balancing": balancing,
        "Accuracy": accuracy_score(y_eval, y_pred_vqc),
        "Precision": precision_score(y_eval, y_pred_vqc, zero_division=0),
        "Recall": recall_score(y_eval, y_pred_vqc, zero_division=0),
        "F1 Score": f1_score(y_eval, y_pred_vqc, zero_division=0),
        "ROC AUC": roc_auc_score(y_eval, y_score_vqc),
        "Training Time": vqc_train_time,
        "Kernel Time (train+eval)": np.nan,
    })

    print(f"QSVM  F1={rows[-2]['F1 Score']:.4f}  ROC-AUC={rows[-2]['ROC AUC']:.4f}")
    print(f"VQC   F1={rows[-1]['F1 Score']:.4f}  ROC-AUC={rows[-1]['ROC AUC']:.4f}")

    for actual, qp, vp in zip(y_eval, y_pred, y_pred_vqc):
        prediction_rows.append({
            "Balancing": balancing,
            "Actual": int(actual),
            "QSVM Predicted": int(qp),
            "VQC Predicted": int(vp),
        })

result_df = pd.DataFrame(rows)
result_df.to_csv("results/novelty/qsvm_vs_vqc.csv", index=False)

predictions_df = pd.DataFrame(prediction_rows)
predictions_df.to_csv("results/novelty/qsvm_vs_vqc_predictions.csv", index=False)
print("Saved results/novelty/qsvm_vs_vqc_predictions.csv")

print("\n" + "=" * 70)
print(result_df.round(4).to_string(index=False))
print("\nSaved results/novelty/qsvm_vs_vqc.csv")
