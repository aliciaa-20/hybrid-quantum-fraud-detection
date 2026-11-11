# Paper update notes (Phase 11)

Drop-in suggestions. The paper itself is untouched; apply what you agree with.

## 1. Thresholds (replaces test-tuned threshold claims)
Thresholds were previously chosen by best F1 on the test labels, which is optimistic. Re-done with a held-out 20% of
the training set (`results/novelty/threshold_validation.csv`). Test F1 at the validation-chosen threshold vs the old figure:

| Model | None | SMOTE | ADASYN |
|---|---|---|---|
| Logistic Regression | 0.758 (old 0.767) | 0.713 (0.756) | 0.637 (0.692) |
| Random Forest | 0.788 (0.804) | 0.741 (0.783) | 0.708 (0.764) |
| SVM | 0.726 (0.778) | 0.593 (0.724) | 0.190 (0.188) |
| VQC | 0.037 (0.017) | 0.022 (0.039) | 0.028 (0.058) |

Suggested wording: tuned thresholds help balanced models a lot (F1 at 0.5 is 0.02-0.19 after SMOTE/ADASYN), but gains
reported earlier were overstated by about 0.05 on average (up to 0.13 for SVM + SMOTE). Random Forest without balancing
is the most stable choice. VQC net benefit stays negative under every setting.

## 2. Seeded VQC multi-seed (replaces the unseeded multi-seed table)
Five seeds per balancing, seeded and reproducible (`results/novelty/vqc_multiseed_seeded_summary.csv`), mean F1:
None 0.0225 +/- 0.0070, SMOTE 0.0241 +/- 0.0095, ADASYN 0.0055 +/- 0.0020. Recall 0.42-0.57 at about 1% precision.

## 3. Table 4 (QSVM vs VQC, matched subsets)
Seeded over 5 seeds: VQC F1 None 0.678 +/- 0.009, SMOTE 0.648 +/- 0.060, ADASYN 0.502 +/- 0.036 vs QSVM 0.831 / 0.843 / 0.557.
The first-run values (0.6748 / 0.6395 / 0.5395) lie inside the seeded ranges, so the first-run vs rerun mismatch is
run-to-run variance, not an error. Soften "QSVM beats VQC on every balancing" to: clearly under None and SMOTE; under
ADASYN the gap is within VQC seed variance (best VQC seed 0.556 vs QSVM 0.557).

## 4. Limitation to state
VQC validation used 57 fraud rows (rows used to build the VQC training subsets were removed), so its validated
thresholds are noisy.
