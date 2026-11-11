"""
Phase 11d: VQC on the matched 250-row evaluation subset, seeded, over 5 seeds.

The paper's Table 4 reports the VQC's first run on this subset; a later rerun gave different numbers because
the optimizer's initial point was not seeded. Here the SAME 120-row training subsets and the SAME 250-row
evaluation subset used by src/novelty/qsvm_kernel.py are reused, and only the seed varies, so the spread
shown is purely initial-point variance. QSVM is deterministic and is copied from qsvm_vs_vqc.csv for reference.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from qiskit.circuit.library import zz_feature_map, real_amplitudes
from qiskit_machine_learning.algorithms import VQC
from qiskit_machine_learning.optimizers import COBYLA
from qiskit_machine_learning.utils import algorithm_globals

RANDOM_STATE = 42
N_QUBITS = 4
FEATURES = ["V10", "V12", "V14", "V17"]
TRAIN_N = 120
EVAL_LEGIT_N = 155
SEEDS = [42, 7, 123, 2024, 99]
DATASETS = {"None": "data/quantum_none.csv", "SMOTE": "data/quantum_smote.csv", "ADASYN": "data/quantum_adasyn.csv"}

test_df = pd.read_csv("data/test_selected.csv")
eval_df = pd.concat([
    test_df[test_df["Class"] == 1],
    test_df[test_df["Class"] == 0].sample(n=EVAL_LEGIT_N, random_state=RANDOM_STATE),
]).sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)
X_eval_raw, y_eval = eval_df[FEATURES].values, eval_df["Class"].values

rows = []
for balancing, path in DATASETS.items():
    train_df = pd.read_csv(path)
    fraud_tr, legit_tr = train_df[train_df["Class"] == 1], train_df[train_df["Class"] == 0]
    n_fraud = min(len(fraud_tr), TRAIN_N // 2)
    sub = pd.concat([
        fraud_tr.sample(n=n_fraud, random_state=RANDOM_STATE),
        legit_tr.sample(n=min(TRAIN_N - n_fraud, len(legit_tr)), random_state=RANDOM_STATE),
    ]).sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)
    scaler = MinMaxScaler(feature_range=(-np.pi, np.pi))
    X_train = scaler.fit_transform(sub[FEATURES].values)
    X_eval = scaler.transform(X_eval_raw)

    for seed in SEEDS:
        algorithm_globals.random_seed = seed
        vqc = VQC(
            feature_map=zz_feature_map(feature_dimension=N_QUBITS, reps=2, entanglement="linear"),
            ansatz=real_amplitudes(num_qubits=N_QUBITS, reps=2, entanglement="linear"),
            optimizer=COBYLA(maxiter=30),
        )
        vqc.fit(X_train, sub["Class"].values)
        pred = np.asarray(vqc.predict(X_eval)).ravel().astype(int)
        proba = np.asarray(vqc.predict_proba(X_eval))
        score = proba[:, 1] if proba.ndim == 2 else proba.ravel()
        rows.append({
            "Balancing": balancing, "Seed": seed,
            "Accuracy": accuracy_score(y_eval, pred), "Precision": precision_score(y_eval, pred, zero_division=0),
            "Recall": recall_score(y_eval, pred, zero_division=0), "F1 Score": f1_score(y_eval, pred, zero_division=0),
            "ROC AUC": roc_auc_score(y_eval, score),
        })
        print(f"{balancing:7s} seed={seed:<5d} F1={rows[-1]['F1 Score']:.4f}  AUC={rows[-1]['ROC AUC']:.4f}", flush=True)

raw = pd.DataFrame(rows)
raw.to_csv("results/novelty/vqc_matched_seeded_raw.csv", index=False)

qsvm = pd.read_csv("results/novelty/qsvm_vs_vqc.csv", keep_default_na=False)
qsvm = qsvm[qsvm["Model"] == "QSVM"].set_index("Balancing")
summary = raw.groupby("Balancing")["F1 Score"].agg(["mean", "std", "min", "max"]).rename(
    columns={"mean": "VQC F1 mean", "std": "VQC F1 std", "min": "VQC F1 min", "max": "VQC F1 max"})
summary["QSVM F1 (deterministic)"] = qsvm["F1 Score"].astype(float)
summary = summary.reindex(["None", "SMOTE", "ADASYN"])
summary.to_csv("results/novelty/vqc_matched_seeded_summary.csv")
print("\n" + summary.round(4).to_string())
