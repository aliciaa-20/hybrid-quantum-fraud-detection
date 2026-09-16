"""
Phase 8 (Part B): McNemar's test for QSVM vs. VQC on the Phase 2 matched
evaluation subset. Requires results/novelty/qsvm_vs_vqc_predictions.csv,
produced by the updated src/novelty/qsvm_kernel.py (which now also saves
per-sample predictions for both models on the identical 250-row subset).
"""

import numpy as np
import pandas as pd
from scipy.stats import binomtest

preds = pd.read_csv("results/novelty/qsvm_vs_vqc_predictions.csv", keep_default_na=False)

rows = []

for balancing, group in preds.groupby("Balancing"):
    y_true = group["Actual"].values
    q_pred = group["QSVM Predicted"].values
    v_pred = group["VQC Predicted"].values

    q_correct = (q_pred == y_true)
    v_correct = (v_pred == y_true)

    b = int(np.sum(q_correct & ~v_correct))  # QSVM right, VQC wrong
    c = int(np.sum(~q_correct & v_correct))  # QSVM wrong, VQC right

    n = b + c
    if n > 0:
        result = binomtest(min(b, c), n, 0.5, alternative="two-sided")
        p_value = result.pvalue
    else:
        p_value = 1.0

    rows.append({
        "Balancing": balancing,
        "QSVM-right/VQC-wrong (b)": b,
        "QSVM-wrong/VQC-right (c)": c,
        "McNemar p-value": p_value,
        "Significant (alpha=0.05)": "Yes" if p_value < 0.05 else "No",
    })

result_df = pd.DataFrame(rows).sort_values("Balancing")
result_df.to_csv("results/novelty/mcnemar_qsvm_vs_vqc.csv", index=False)

print("=" * 80)
print("McNemar's test: QSVM vs. VQC (matched 250-row evaluation subset)")
print("=" * 80)
print(result_df.to_string(index=False))
print("\nSaved results/novelty/mcnemar_qsvm_vs_vqc.csv")
