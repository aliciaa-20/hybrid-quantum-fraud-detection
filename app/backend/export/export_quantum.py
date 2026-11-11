"""Retrain QSVM and VQC (SMOTE data), run the reproduction gates, save artifacts and build samples.json.

Run from app/backend:  ../../.venv/bin/python -m export.export_quantum
Takes roughly 5-15 minutes (kernel evaluation and VQC training/prediction on a simulator).
"""

import json
import time

import joblib
import numpy as np
import pandas as pd
from qiskit.circuit.library import real_amplitudes, zz_feature_map
from qiskit_machine_learning.algorithms import VQC
from qiskit_machine_learning.kernels import FidelityQuantumKernel
from qiskit_machine_learning.optimizers import COBYLA
from qiskit_machine_learning.utils import algorithm_globals
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC

from export import gate
from fraudscope import config

N_QUBITS = 4
QSVM_TRAIN_N = 120  # 60 fraud + 60 legit, as in src/novelty/qsvm_kernel.py
# Gate width for VQC: multiples of the std across the paper's 5 seeds (full test set).
VQC_GATE_STDS = 2.0


def feature_map():
    return zz_feature_map(feature_dimension=N_QUBITS, reps=2, entanglement="linear")


def metrics(y, labels, scores) -> dict:
    return {
        "Precision": precision_score(y, labels, zero_division=0),
        "Recall": recall_score(y, labels, zero_division=0),
        "F1 Score": f1_score(y, labels, zero_division=0),
        "ROC AUC": roc_auc_score(y, scores),
    }


def export_qsvm(subset: pd.DataFrame, stored_preds: pd.DataFrame, qsvm_results: pd.DataFrame) -> dict:
    print("\nQSVM (SMOTE): training subset and kernel ...")
    train = pd.read_csv(config.DATA_DIR / "quantum_smote.csv")
    fraud, legit = train[train["Class"] == 1], train[train["Class"] == 0]
    n_fraud = min(len(fraud), QSVM_TRAIN_N // 2)
    n_legit = QSVM_TRAIN_N - n_fraud
    sub = pd.concat([
        fraud.sample(n=n_fraud, random_state=config.RANDOM_STATE),
        legit.sample(n=min(n_legit, len(legit)), random_state=config.RANDOM_STATE),
    ]).sample(frac=1, random_state=config.RANDOM_STATE).reset_index(drop=True)

    scaler = MinMaxScaler(feature_range=(-np.pi, np.pi))
    X_train = scaler.fit_transform(sub[config.FEATURES].values)
    X_eval = scaler.transform(subset[config.FEATURES].values)

    kernel = FidelityQuantumKernel(feature_map=feature_map())
    t0 = time.time()
    K_train = kernel.evaluate(x_vec=X_train)
    K_eval = kernel.evaluate(x_vec=X_eval, y_vec=X_train)
    print(f"  kernels done in {time.time() - t0:.0f}s")

    svc = SVC(kernel="precomputed", probability=True, random_state=config.RANDOM_STATE)
    svc.fit(K_train, sub["Class"].values)
    labels = svc.predict(K_eval).astype(int)
    scores = svc.predict_proba(K_eval)[:, 1]

    print("Gate (QSVM):")
    stored = stored_preds[stored_preds["Balancing"] == "SMOTE"]["QSVM Predicted"].values
    mismatches = int((labels != stored).sum())
    if mismatches:
        raise gate.GateFailure(f"QSVM labels differ from the paper's stored labels on {mismatches}/250 rows")
    print("  ok  QSVM labels identical to stored labels (250/250)")
    row = qsvm_results[(qsvm_results["Model"] == "QSVM") & (qsvm_results["Balancing"] == "SMOTE")].iloc[0]
    gate.check_metrics_row("QSVM/SMOTE metrics", metrics(subset["Class"].values, labels, scores), row)

    joblib.dump({"scaler": scaler, "train_points": X_train, "svc": svc}, config.ARTIFACT_DIR / "qsvm.joblib", compress=3)
    gate.update_provenance("qsvm", {
        "model": "QSVM (fidelity quantum kernel + SVC)", "balancing": "SMOTE", "seed": config.RANDOM_STATE,
        "train_rows": QSVM_TRAIN_N, "evaluation_scope": "matched 250-row class-enriched subset",
        "gate": "passed", "gate_details": "labels identical to stored; metrics 4dp",
    })
    return {"labels": labels, "scores": scores}


def export_vqc(subset: pd.DataFrame, test: pd.DataFrame) -> None:
    print("\nVQC (SMOTE): training (seeded re-run) ...")
    algorithm_globals.random_seed = config.RANDOM_STATE
    train = pd.read_csv(config.DATA_DIR / "quantum_smote.csv")
    scaler = MinMaxScaler(feature_range=(-np.pi, np.pi))
    X_train = scaler.fit_transform(train[config.FEATURES].values)
    vqc = VQC(
        feature_map=feature_map(),
        ansatz=real_amplitudes(num_qubits=N_QUBITS, reps=2, entanglement="linear"),
        optimizer=COBYLA(maxiter=30),
    )
    t0 = time.time()
    vqc.fit(X_train, train["Class"].values)
    print(f"  trained in {time.time() - t0:.0f}s; predicting full test set ({len(test)} rows) ...")

    t0 = time.time()
    X_test = scaler.transform(test[config.FEATURES].values)
    proba = np.asarray(vqc.predict_proba(X_test))
    scores = proba[:, 1] if proba.ndim == 2 else proba.ravel()
    labels = np.asarray(vqc.predict(X_test)).ravel().astype(int)
    print(f"  predicted in {time.time() - t0:.0f}s")

    print("Gate (VQC, full test set, vs the paper's 5-seed spread):")
    summary = pd.read_csv(config.SOURCE_RESULTS_DIR / "novelty" / "vqc_multiseed_summary.csv",
                          header=[0, 1], index_col=0, skiprows=[2])
    got = metrics(test["Class"].values, labels, scores)
    for key in ("F1 Score", "ROC AUC"):
        mean, std = (float(summary.loc["SMOTE", (key, s)]) for s in ("mean", "std"))
        lo, hi = mean - VQC_GATE_STDS * std, mean + VQC_GATE_STDS * std
        if not (lo <= got[key] <= hi):
            raise gate.GateFailure(f"VQC {key} {got[key]:.4f} outside paper range [{lo:.4f}, {hi:.4f}]")
        print(f"  ok  VQC {key} {got[key]:.4f} within [{lo:.4f}, {hi:.4f}] (mean {mean:.4f} ± {VQC_GATE_STDS}×{std:.4f})")

    vqc.save(str(config.ARTIFACT_DIR / "vqc.model"))
    joblib.dump(scaler, config.ARTIFACT_DIR / "vqc_scaler.joblib")
    gate.update_provenance("vqc_live", {
        "model": "VQC (ZZFeatureMap + RealAmplitudes, COBYLA 30 iters)", "balancing": "SMOTE",
        "seed": config.RANDOM_STATE, "evaluation_scope": "full test set (56,746 rows)",
        "full_test_metrics": {k: float(v) for k, v in got.items()},
        "gate": "passed", "gate_details": f"F1 and ROC AUC within mean ± {VQC_GATE_STDS} std of the paper's 5 seeds",
        "note": "Live model is a seeded re-run; stored sample scores are from the paper's run.",
    })


def build_samples(subset: pd.DataFrame, test: pd.DataFrame, qsvm_out: dict) -> None:
    print("\nBuilding samples.json ...")
    qp = gate.read_results_csv(config.SOURCE_RESULTS_DIR / "quantum_predictions.csv")
    gate.check_alignment(test, qp, "SMOTE")
    paper = qp[qp["Balancing"] == "SMOTE"].reset_index(drop=True)

    records = []
    for i, row in subset.iterrows():
        ti = int(row["test_index"])
        records.append({
            "id": int(i),
            "test_index": ti,
            "features": {f: float(row[f]) for f in config.FEATURES},
            "actual": int(row["Class"]),
            "qsvm": {"label": int(qsvm_out["labels"][i]), "score": float(qsvm_out["scores"][i])},
            "vqc_paper": {"label": int(paper.loc[ti, "Predicted"]), "score": float(paper.loc[ti, "Fraud Probability"])},
        })
    frauds = sum(r["actual"] for r in records)
    if len(records) != 250 or frauds != 95:
        raise gate.GateFailure(f"samples: {len(records)} rows / {frauds} frauds (want 250 / 95)")
    (config.ARTIFACT_DIR / "samples.json").write_text(json.dumps(records))
    print(f"  saved samples.json: 250 rows, {frauds} frauds")


def main() -> None:
    config.ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    test = gate.load_test()
    stored = gate.read_results_csv(config.SOURCE_RESULTS_DIR / "novelty" / "qsvm_vs_vqc_predictions.csv")
    results = gate.read_results_csv(config.SOURCE_RESULTS_DIR / "novelty" / "qsvm_vs_vqc.csv")

    print("Gate (evaluation subset):")
    subset = gate.build_eval_subset(test)
    gate.check_eval_subset(subset, stored)

    qsvm_out = export_qsvm(subset, stored, results)
    export_vqc(subset, test)
    build_samples(subset, test, qsvm_out)
    print("\nDone.")


if __name__ == "__main__":
    main()
