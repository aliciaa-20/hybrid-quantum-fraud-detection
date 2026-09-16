# Novelty Implementation Phases — Hybrid QML Fraud Detection Paper

Tracks work added on top of the original submission (VQC + classical baselines) to make the
project publishable. Environment verified: Python venv, qiskit 2.5.2, qiskit-machine-learning
0.9.1, qiskit-aer 0.17.2 — all needed APIs (FidelityQuantumKernel, EfficientSU2,
PauliFeatureMap, NoiseModel) import cleanly.

Reference papers for lit review: `/Users/aliciapereira/Downloads/qc_miniproj/papers/` (9 papers)
+ an IOP Publishing template found alongside them (likely the target journal format).

Ground truth for feasibility: VQC.fit on ~1000-1800 rows takes 52-100s (30 COBYLA iters);
VQC.predict on the full 56,747-row test set already completes in the existing results (it's a
per-sample forward pass, not a pairwise kernel, so it scales linearly). Quantum **kernel**
methods (QSVM) are pairwise (train x test circuit evaluations) and will NOT scale to a
56k-row test set — needs a documented, justified test subsample, same rationale the original
paper already used for VQC training subsets.

Status legend: [ ] pending, [~] in progress, [x] done, [!] blocked/infeasible (reason noted)

## Phase 0 — Setup & Feasibility
- [x] Confirm quantum library versions and required API availability
- [x] Confirm VQC train/predict timing baseline from existing results
- [ ] Skim reference papers for lit review angle + confirm target format from IOP template

## Phase 1 — Threshold Optimization (cheap, high payoff) [x] DONE
- [x] VQC probabilities already existed in results/quantum_predictions.csv — no rerun needed
- [x] Regenerated classical probabilities: src/novelty/classical_predictions.py ->
      results/novelty/classical_predictions.csv
- [x] Threshold sweep (default 0.5 / best-F1 / Youden's J): src/novelty/threshold_optimization.py
      -> results/novelty/threshold_optimization.csv
- [x] Bug found+fixed: pandas reads the literal string "None" (the "no balancing" label) as
      NaN unless `keep_default_na=False` is passed — affected BOTH the original
      quantum_predictions.csv read and the new classical one. Fixed in the novelty script.
- **Key finding**: threshold tuning nearly triples Random Forest+ADASYN's F1 (0.0642 -> 0.7636,
  matching the untuned no-balancing baseline) and lifts Random Forest+None to a new best F1 of
  0.8043 (from 0.7907). VQC barely moves (best F1 0.0578 for ADASYN, up from 0.0123) even under
  optimal threshold — evidence the quantum classifier's probability outputs lack real
  separative power, i.e. this is not merely a threshold-choice problem for VQC.

## Phase 2 — Quantum Kernel Classifier (QSVM) [x] DONE
- [x] Feasibility timing test (60x60 kernel): ~26.5 evals/sec symmetric, ~103 evals/sec
      non-symmetric -> chose train=120 (60 fraud + 60 legit), eval subset=250 (all 95 test
      fraud + 155 random legit, ~38% fraud rate) to keep runtime to ~10 min/condition
- [x] Built src/novelty/qsvm_kernel.py: ZZFeatureMap FidelityQuantumKernel + SVC(precomputed),
      plus VQC retrained/evaluated on the IDENTICAL subset for a fair head-to-head
- [x] Documented clearly: this eval subset is class-enriched vs. the real ~0.17% fraud rate,
      so these numbers are not directly comparable to the full-test-set headline VQC numbers
      -- they exist only to compare QSVM vs. VQC on equal footing
- **Key finding**: QSVM clearly beats VQC on every balancing condition on the matched subset
  (F1: None 0.8306 vs 0.6748, SMOTE 0.8432 vs 0.6395, ADASYN 0.5567 vs 0.5395; ROC-AUC follows
  the same pattern). This gives the paper a genuine second quantum method and a real
  "which quantum approach performs better" comparison, not just VQC-vs-classical.
- Also notable: both quantum methods score far better here than the near-zero F1 VQC got on
  the full imbalanced test set (Phase 1's headline numbers) -- reinforcing that extreme class
  imbalance, not "quantumness" per se, was the dominant driver of the original poor scores.

## Phase 3 — Multi-seed Robustness [x] DONE
- [x] Ran 5 seeds (42, 7, 123, 2024, 99) x 3 balancing conditions, full pipeline
      (resample -> SMOTE/ADASYN -> VQC train -> VQC predict on full test set) each time
- [x] Runtime note: took ~90 min total, notably longer than the ~20-30 min estimated from fit
      time alone -- `predict()` on the full 56,747-row test set turned out to dominate
      wall-clock, not the COBYLA fit. Worth flagging for anyone re-running this.
- **Key finding**: ADASYN is highly unstable across seeds -- accuracy 0.5625 +/- 0.2283,
  F1 0.0057 +/- 0.0026, ROC-AUC 0.6472 +/- 0.0760. The original paper's single ADASYN run
  (accuracy 0.8018, F1 0.0123) sits within this wide spread but is not representative of the
  mean. SMOTE is far more stable (accuracy 0.9196+/-0.0291, F1 0.0241+/-0.0090) and its mean F1
  closely reproduces the original single-run number (0.0234) -- so SMOTE's original result was
  reproducible, but ADASYN's was largely luck of the draw. This is a legitimate, citable
  robustness result for the paper's Result Analysis section.
- Raw per-seed data: results/novelty/vqc_multiseed_raw.csv; summary: vqc_multiseed_summary.csv

## Phase 4 — Feature Map / Ansatz Ablation [x] DONE
- [x] Confirmed in Phase 0 that PauliFeatureMap and EfficientSU2 construct cleanly at 4 qubits
- [x] Ran the full 2x2 grid on the SMOTE training condition (best original VQC config),
      full test set -- directly comparable to the original paper's Table 7
- **Key finding**: RealAmplitudes clearly beats EfficientSU2 regardless of feature map
  (F1 0.0288 vs 0.0177 with ZZFeatureMap; 0.0256 vs 0.0136 with PauliFeatureMap) -- ansatz
  choice matters more than feature map choice here. The ORIGINAL paper's exact configuration
  (ZZFeatureMap + RealAmplitudes) turns out to be the best of all 4 combinations tested, which
  is a reassuring result: the original architecture choice wasn't arbitrary or suboptimal, it
  was already the strongest available option among these alternatives.
- Results: results/novelty/ablation_featuremap_ansatz.csv

## Phase 5 — Qubit-Count Scaling Study [x] DONE
- [x] Confirmed MI ranking supports k up to 8 cleanly (monotonic scores, no ties); k=4 exactly
      reproduces the original paper's own feature selection (V10, V12, V14, V17)
- [x] Ran k in {2,4,6,8} on a matched "no balancing" subsample, full test set evaluation
- Note: this run was killed once by macOS for system-wide low memory (Chrome/Creative Cloud
      contention, not a script issue -- confirmed via vm_stat). Added resume-from-CSV support
      to src/novelty/qubit_scaling.py plus explicit gc.collect() per iteration; user freed RAM
      and the retry completed cleanly.
- **Key finding**: F1/ROC-AUC is BEST at k=2 (F1=0.0822, ROC-AUC=0.9227) and degrades sharply
  with more qubits (k=4: F1=0.0135, ROC-AUC=0.7638; k=6: F1=0.0024, ROC-AUC=0.3754 -- worse than
  random; k=8: F1=0.0042, ROC-AUC=0.5512), while combined train+predict time explodes
  (37s -> 107s -> 252s -> 841s). Likely cause: the training budget (1000 samples, 30 COBYLA
  iterations) is fixed regardless of k, so larger circuits' bigger parameter spaces can't be
  optimized well in the same budget -- a genuine, citable NISQ-era scalability limitation.
- Results: results/novelty/qubit_scaling.csv

## Phase 6 — Noise-Model Simulation
- [ ] Feasibility: confirm AerSimulator + NoiseModel integrates with VQC's sampler in this
      qiskit-machine-learning version (0.9.1) — check API compatibility before full run
- [ ] Run best config (from Phase 1-4) under a realistic depolarizing/readout noise model
- [ ] Compare noiseless vs noisy metrics — feeds NISQ-feasibility discussion

## Phase 7 — Paper Writing
- [ ] Title
- [ ] Literature Review (from qc_miniproj/papers)
- [ ] Methodology (update with Phases 1-6 additions)
- [ ] Proof of Concept / Implementation
- [ ] Result Analysis and Comparative Analysis (new tables/figures from Phases 1-6)
- [ ] References

## Housekeeping
- Commit after each phase completes (git commit only, no push — user is not a GitHub
  contributor on this repo and wants it to stay that way).
