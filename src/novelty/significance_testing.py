"""
Phase 8 (Part A): Statistical significance testing using EXISTING data
(no VQC/QSVM reruns needed for this part -- see qsvm_kernel.py for the
Part B rerun that adds paired McNemar's test for QSVM vs. VQC).

Two analyses:
1. McNemar's test (exact binomial form) comparing the best classical model's
   best-F1-threshold predictions against VQC's best-F1-threshold predictions,
   per balancing condition, on the full test set. McNemar's test is the
   correct significance test here because both models are evaluated on the
   SAME paired test samples (per-sample correct/incorrect outcomes are not
   independent between models).
2. Paired significance tests (paired t-test and Wilcoxon signed-rank) across
   the 5 seeds from the multi-seed robustness study (Phase 3), comparing
   VQC's F1 and ROC-AUC pairwise across balancing conditions (None vs SMOTE,
   None vs ADASYN, SMOTE vs ADASYN).
"""

import numpy as np
import pandas as pd
from scipy.stats import binomtest, ttest_rel, wilcoxon

# ---------------------------------------------------------------------
# 1. McNemar's test: best classical model vs VQC, per balancing condition
# ---------------------------------------------------------------------

quantum = pd.read_csv("results/quantum_predictions.csv", keep_default_na=False)
quantum["Model"] = "VQC"
classical = pd.read_csv("results/novelty/classical_predictions.csv", keep_default_na=False)
thresholds = pd.read_csv("results/novelty/threshold_optimization.csv", keep_default_na=False)

combined = pd.concat(
    [
        quantum[["Model", "Balancing", "Actual", "Fraud Probability"]],
        classical[["Model", "Balancing", "Actual", "Fraud Probability"]],
    ],
    ignore_index=True,
)

# Best classical model per balancing condition, ranked by original Table 1 F1
# (Random Forest for None/SMOTE/ADASYN all had the top or near-top classical F1)
BEST_CLASSICAL = {"None": "Random Forest", "SMOTE": "Random Forest", "ADASYN": "Random Forest"}

mcnemar_rows = []

for balancing in ["None", "SMOTE", "ADASYN"]:
    classical_model = BEST_CLASSICAL[balancing]

    c_group = combined[(combined["Model"] == classical_model) & (combined["Balancing"] == balancing)]
    q_group = combined[(combined["Model"] == "VQC") & (combined["Balancing"] == balancing)]

    # both groups share the same test set and are already in test-set row order
    y_true = c_group["Actual"].values
    assert np.array_equal(y_true, q_group["Actual"].values), "Test sets must align for McNemar's test"

    c_thresh_row = thresholds[(thresholds["Model"] == classical_model) & (thresholds["Balancing"] == balancing)].iloc[0]
    q_thresh_row = thresholds[(thresholds["Model"] == "VQC") & (thresholds["Balancing"] == balancing)].iloc[0]

    c_pred = (c_group["Fraud Probability"].values >= c_thresh_row["Best-F1 Threshold"]).astype(int)
    q_pred = (q_group["Fraud Probability"].values >= q_thresh_row["Best-F1 Threshold"]).astype(int)

    c_correct = (c_pred == y_true)
    q_correct = (q_pred == y_true)

    # McNemar contingency: b = classical right/quantum wrong, c = classical wrong/quantum right
    b = int(np.sum(c_correct & ~q_correct))
    c = int(np.sum(~c_correct & q_correct))

    n = b + c
    # exact binomial McNemar's test: under H0, b ~ Binomial(n, 0.5)
    if n > 0:
        result = binomtest(min(b, c), n, 0.5, alternative="two-sided")
        p_value = result.pvalue
    else:
        p_value = 1.0

    mcnemar_rows.append({
        "Balancing": balancing,
        "Classical Model": classical_model,
        "Classical-right/VQC-wrong (b)": b,
        "Classical-wrong/VQC-right (c)": c,
        "McNemar p-value": p_value,
        "Significant (alpha=0.05)": "Yes" if p_value < 0.05 else "No",
    })

mcnemar_df = pd.DataFrame(mcnemar_rows)
mcnemar_df.to_csv("results/novelty/mcnemar_classical_vs_vqc.csv", index=False)

print("=" * 80)
print("McNemar's test: best classical model vs. VQC (best-F1 thresholds, full test set)")
print("=" * 80)
print(mcnemar_df.to_string(index=False))

# ---------------------------------------------------------------------
# 2. Paired tests across VQC multi-seed results (balancing condition comparisons)
# ---------------------------------------------------------------------

multiseed = pd.read_csv("results/novelty/vqc_multiseed_raw.csv", keep_default_na=False)

pairs = [("None", "SMOTE"), ("None", "ADASYN"), ("SMOTE", "ADASYN")]
metrics_to_test = ["F1 Score", "ROC AUC"]

paired_rows = []

for metric in metrics_to_test:
    pivot = multiseed.pivot(index="Seed", columns="Balancing", values=metric)
    for a, b in pairs:
        x = pivot[a].values
        y = pivot[b].values

        t_stat, t_p = ttest_rel(x, y)
        try:
            w_stat, w_p = wilcoxon(x, y)
        except ValueError:
            w_stat, w_p = np.nan, np.nan

        paired_rows.append({
            "Metric": metric,
            "Condition A": a,
            "Condition A Mean": np.mean(x),
            "Condition B": b,
            "Condition B Mean": np.mean(y),
            "Paired t-test p-value": t_p,
            "Wilcoxon p-value": w_p,
            "Significant (alpha=0.05, t-test)": "Yes" if t_p < 0.05 else "No",
        })

paired_df = pd.DataFrame(paired_rows)
paired_df.to_csv("results/novelty/paired_tests_multiseed.csv", index=False)

print("\n" + "=" * 80)
print("Paired significance tests across VQC balancing conditions (N=5 seeds)")
print("=" * 80)
print(paired_df.to_string(index=False))

print("\nSaved results/novelty/mcnemar_classical_vs_vqc.csv")
print("Saved results/novelty/paired_tests_multiseed.csv")
