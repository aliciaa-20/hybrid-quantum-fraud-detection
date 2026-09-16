"""
Phase 3: Multi-seed robustness for VQC.

The original VQC results were each a single run on one fixed 1000-1800 row
training subsample. That is an anecdote, not evidence -- a different random
subsample could easily land on a very different F1/ROC-AUC by chance. This
script repeats the full quantum_data.py -> VQC-train -> VQC-eval pipeline
for N_SEEDS different random subsamples per balancing condition, and reports
mean +/- std for every metric.

Feasibility: single-seed VQC fits took 52-100s in the original run
(results/quantum_results.csv). N_SEEDS=5 x 3 balancing conditions is
therefore ~5 x (52+100+90)s =~ 20 min of fit time, run sequentially to
avoid CPU contention with other quantum-simulation scripts.
"""

import time
import numpy as np
import pandas as pd

from sklearn.preprocessing import MinMaxScaler
from imblearn.over_sampling import SMOTE, ADASYN
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
)

from qiskit.circuit.library import zz_feature_map, real_amplitudes
from qiskit_machine_learning.algorithms import VQC
from qiskit_machine_learning.optimizers import COBYLA

N_QUBITS = 4
FEATURES = ["V10", "V12", "V14", "V17"]
MAX_ITER = 30

N_FRAUD = 100
N_LEGITIMATE = 900

SEEDS = [42, 7, 123, 2024, 99]

train_full = pd.read_csv("data/train_selected.csv")
test_df = pd.read_csv("data/test_selected.csv")

X_test_raw = test_df[FEATURES].values
y_test = test_df["Class"].values

fraud_pool = train_full[train_full["Class"] == 1]
legit_pool = train_full[train_full["Class"] == 0]

rows = []

for seed in SEEDS:
    fraud_sample = fraud_pool.sample(n=N_FRAUD, random_state=seed)
    legit_sample = legit_pool.sample(n=N_LEGITIMATE, random_state=seed)
    base = pd.concat([fraud_sample, legit_sample]).sample(frac=1, random_state=seed)

    X_base = base.drop("Class", axis=1)
    y_base = base["Class"]

    configs = {"None": (X_base, y_base)}

    smote = SMOTE(random_state=seed)
    X_smote, y_smote = smote.fit_resample(X_base, y_base)
    configs["SMOTE"] = (X_smote, y_smote)

    adasyn = ADASYN(random_state=seed)
    X_adasyn, y_adasyn = adasyn.fit_resample(X_base, y_base)
    configs["ADASYN"] = (X_adasyn, y_adasyn)

    for balancing, (X_train_raw, y_train) in configs.items():
        print("\n" + "=" * 70)
        print(f"seed={seed}  VQC + {balancing}  (n_train={len(X_train_raw)})")
        print("=" * 70)

        scaler = MinMaxScaler(feature_range=(-np.pi, np.pi))
        X_train = scaler.fit_transform(np.asarray(X_train_raw))
        X_test = scaler.transform(X_test_raw)

        feature_map = zz_feature_map(feature_dimension=N_QUBITS, reps=2, entanglement="linear")
        ansatz = real_amplitudes(num_qubits=N_QUBITS, reps=2, entanglement="linear")
        vqc = VQC(feature_map=feature_map, ansatz=ansatz, optimizer=COBYLA(maxiter=MAX_ITER))

        t0 = time.time()
        vqc.fit(X_train, np.asarray(y_train))
        train_time = time.time() - t0

        y_pred = np.asarray(vqc.predict(X_test)).ravel().astype(int)
        try:
            proba = np.asarray(vqc.predict_proba(X_test))
            y_score = proba[:, 1] if proba.ndim == 2 else proba.ravel()
        except Exception:
            y_score = y_pred

        metrics = {
            "Seed": seed,
            "Balancing": balancing,
            "Accuracy": accuracy_score(y_test, y_pred),
            "Precision": precision_score(y_test, y_pred, zero_division=0),
            "Recall": recall_score(y_test, y_pred, zero_division=0),
            "F1 Score": f1_score(y_test, y_pred, zero_division=0),
            "ROC AUC": roc_auc_score(y_test, y_score),
            "Training Time": train_time,
        }
        rows.append(metrics)
        print(f"F1={metrics['F1 Score']:.4f}  ROC-AUC={metrics['ROC AUC']:.4f}  time={train_time:.1f}s")

        pd.DataFrame(rows).to_csv("results/novelty/vqc_multiseed_raw.csv", index=False)

result_df = pd.DataFrame(rows)
result_df.to_csv("results/novelty/vqc_multiseed_raw.csv", index=False)

summary = result_df.groupby("Balancing")[
    ["Accuracy", "Precision", "Recall", "F1 Score", "ROC AUC", "Training Time"]
].agg(["mean", "std"])
summary.to_csv("results/novelty/vqc_multiseed_summary.csv")

print("\n" + "=" * 70)
print("SUMMARY (mean +/- std across seeds)")
print("=" * 70)
print(summary.round(4).to_string())
print("\nSaved results/novelty/vqc_multiseed_raw.csv and vqc_multiseed_summary.csv")
