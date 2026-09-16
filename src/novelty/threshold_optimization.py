"""
Phase 1: Threshold optimization.

The original pipeline always used the default 0.5 decision threshold, which
is a poor choice under ~0.17% class imbalance. This script sweeps thresholds
on the already-computed probability scores (results/quantum_predictions.csv
for VQC, results/novelty/classical_predictions.csv for the classical models)
and reports, per model x balancing condition:
  - default-threshold metrics (reproduces the original results)
  - best-F1 threshold and its metrics
  - Youden's J (TPR - FPR) optimal threshold and its metrics
"""

import numpy as np
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score, roc_curve

quantum = pd.read_csv("results/quantum_predictions.csv", keep_default_na=False)
quantum["Model"] = "VQC"

classical = pd.read_csv("results/novelty/classical_predictions.csv", keep_default_na=False)

combined = pd.concat(
    [
        quantum[["Model", "Balancing", "Actual", "Fraud Probability"]],
        classical[["Model", "Balancing", "Actual", "Fraud Probability"]],
    ],
    ignore_index=True,
)


def metrics_at_threshold(y_true, y_score, threshold):
    y_pred = (y_score >= threshold).astype(int)
    return {
        "Precision": precision_score(y_true, y_pred, zero_division=0),
        "Recall": recall_score(y_true, y_pred, zero_division=0),
        "F1 Score": f1_score(y_true, y_pred, zero_division=0),
    }


def best_f1_threshold(y_true, y_score):
    thresholds = np.unique(y_score)
    thresholds = thresholds[(thresholds > 0) & (thresholds < 1)]
    if len(thresholds) > 2000:
        thresholds = np.quantile(thresholds, np.linspace(0, 1, 2000))
    best_t, best_f1 = 0.5, -1
    for t in thresholds:
        f1 = f1_score(y_true, (y_score >= t).astype(int), zero_division=0)
        if f1 > best_f1:
            best_f1, best_t = f1, t
    return best_t


def youden_j_threshold(y_true, y_score):
    fpr, tpr, thr = roc_curve(y_true, y_score)
    j = tpr - fpr
    return thr[np.argmax(j)]


rows = []
for (model, balancing), group in combined.groupby(["Model", "Balancing"]):
    y_true = group["Actual"].values
    y_score = group["Fraud Probability"].values

    default = metrics_at_threshold(y_true, y_score, 0.5)

    t_f1 = best_f1_threshold(y_true, y_score)
    at_f1 = metrics_at_threshold(y_true, y_score, t_f1)

    t_j = youden_j_threshold(y_true, y_score)
    at_j = metrics_at_threshold(y_true, y_score, t_j)

    rows.append({
        "Model": model,
        "Balancing": balancing,
        "Default Threshold": 0.5,
        "Default Precision": default["Precision"],
        "Default Recall": default["Recall"],
        "Default F1": default["F1 Score"],
        "Best-F1 Threshold": t_f1,
        "Best-F1 Precision": at_f1["Precision"],
        "Best-F1 Recall": at_f1["Recall"],
        "Best-F1 F1": at_f1["F1 Score"],
        "Youden-J Threshold": t_j,
        "Youden-J Precision": at_j["Precision"],
        "Youden-J Recall": at_j["Recall"],
        "Youden-J F1": at_j["F1 Score"],
    })

result_df = pd.DataFrame(rows).sort_values(["Model", "Balancing"])
result_df.to_csv("results/novelty/threshold_optimization.csv", index=False)

pd.set_option("display.width", 160)
print(result_df.round(4).to_string(index=False))
print("\nSaved results/novelty/threshold_optimization.csv")
