"""
Phase 5: Qubit-count scaling study.

Varies the number of Mutual-Information-selected features (= qubits) in
{2, 4, 6, 8} and retrains VQC (ZZFeatureMap + RealAmplitudes, unchanged
otherwise) on a matched "no balancing" subsample for each, evaluating on
the full test set. This isolates the effect of qubit count from balancing
method (Phase 3 already covers balancing variance).

Feasibility: Phase 0 confirmed MI feature ranking is well-behaved up to 8
features (monotonically decreasing scores, no ties/instability). k=4
reproduces the original paper's own feature selection exactly (V10, V12,
V14, V17), which is a useful sanity check on this script's correctness.
"""

import gc
import os
import time
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.feature_selection import SelectKBest, mutual_info_classif
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
)

from qiskit.circuit.library import zz_feature_map, real_amplitudes
from qiskit_machine_learning.algorithms import VQC
from qiskit_machine_learning.optimizers import COBYLA

RANDOM_STATE = 42
MAX_ITER = 30
K_VALUES = [2, 4, 6, 8]
N_FRAUD = 100
N_LEGITIMATE = 900

df = pd.read_csv("data/creditcard.csv").drop_duplicates()
X = df.drop("Class", axis=1)
y = df["Class"]

X_train_full, X_test_full, y_train_full, y_test = train_test_split(
    X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
)

scaler_std = StandardScaler()
X_train_std = pd.DataFrame(
    scaler_std.fit_transform(X_train_full), columns=X_train_full.columns, index=X_train_full.index
)
X_test_std = pd.DataFrame(
    scaler_std.transform(X_test_full), columns=X_test_full.columns, index=X_test_full.index
)

OUT_PATH = "results/novelty/qubit_scaling.csv"

rows = []
done_k = set()
if os.path.exists(OUT_PATH):
    prior = pd.read_csv(OUT_PATH)
    rows = prior.to_dict("records")
    done_k = set(prior["Qubits"].tolist())
    print(f"Resuming: already have results for k={sorted(done_k)}")

for k in K_VALUES:
    if k in done_k:
        print(f"Skipping k={k}, already completed")
        continue

    print("\n" + "=" * 70)
    print(f"k = {k} qubits")
    print("=" * 70)

    selector = SelectKBest(score_func=mutual_info_classif, k=k)
    selector.fit(X_train_std, y_train_full)
    selected = list(X_train_std.columns[selector.get_support()])
    print("Selected features:", selected)

    train_sel = X_train_std[selected].copy()
    train_sel["Class"] = y_train_full.values
    test_sel = X_test_std[selected].values

    fraud_pool = train_sel[train_sel["Class"] == 1]
    legit_pool = train_sel[train_sel["Class"] == 0]
    fraud_sample = fraud_pool.sample(n=N_FRAUD, random_state=RANDOM_STATE)
    legit_sample = legit_pool.sample(n=N_LEGITIMATE, random_state=RANDOM_STATE)
    quantum_train = pd.concat([fraud_sample, legit_sample]).sample(
        frac=1, random_state=RANDOM_STATE
    )

    X_train_raw = quantum_train[selected].values
    y_train = quantum_train["Class"].values

    mm_scaler = MinMaxScaler(feature_range=(-np.pi, np.pi))
    X_train = mm_scaler.fit_transform(X_train_raw)
    X_test = mm_scaler.transform(test_sel)

    feature_map = zz_feature_map(feature_dimension=k, reps=2, entanglement="linear")
    ansatz = real_amplitudes(num_qubits=k, reps=2, entanglement="linear")
    vqc = VQC(feature_map=feature_map, ansatz=ansatz, optimizer=COBYLA(maxiter=MAX_ITER))

    t0 = time.time()
    vqc.fit(X_train, y_train)
    train_time = time.time() - t0

    t1 = time.time()
    y_pred = np.asarray(vqc.predict(X_test)).ravel().astype(int)
    predict_time = time.time() - t1

    try:
        proba = np.asarray(vqc.predict_proba(X_test))
        y_score = proba[:, 1] if proba.ndim == 2 else proba.ravel()
    except Exception:
        y_score = y_pred

    metrics = {
        "Qubits": k,
        "Features": ", ".join(selected),
        "Accuracy": accuracy_score(y_test.values if hasattr(y_test, "values") else y_test, y_pred),
        "Precision": precision_score(y_test, y_pred, zero_division=0),
        "Recall": recall_score(y_test, y_pred, zero_division=0),
        "F1 Score": f1_score(y_test, y_pred, zero_division=0),
        "ROC AUC": roc_auc_score(y_test, y_score),
        "Training Time": train_time,
        "Predict Time": predict_time,
    }
    rows.append(metrics)
    print(f"F1={metrics['F1 Score']:.4f}  ROC-AUC={metrics['ROC AUC']:.4f}  "
          f"train={train_time:.1f}s  predict={predict_time:.1f}s")

    pd.DataFrame(rows).to_csv(OUT_PATH, index=False)

    del vqc, X_train, X_test, X_train_raw, quantum_train, train_sel
    gc.collect()

result_df = pd.DataFrame(rows)
result_df.to_csv(OUT_PATH, index=False)

print("\n" + "=" * 70)
print(result_df.round(4).to_string(index=False))
print("\nSaved results/novelty/qubit_scaling.csv")
