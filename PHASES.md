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

## Phase 6 — Noise-Model Simulation [x] DONE
- [x] Confirmed in Phase 0 that AerSampler + NoiseModel wires into VQC cleanly on
      qiskit-machine-learning 0.9.1
- [x] Small-scale timing check (n=60, 10 iters) showed noisy sim isn't much slower than
      noiseless at 4 qubits -- confirmed feasible to run at full scale without subsampling
- [x] Ran ZZFeatureMap+RealAmplitudes+SMOTE (best config) noiseless vs. under an illustrative
      NISQ-like noise model (0.1% single-qubit / 1% two-qubit depolarizing + 1% readout error)
- **Key finding**: noise causes a real but modest performance drop (F1 0.0195 -> 0.0157,
  ROC-AUC 0.8169 -> 0.7943) plus a substantial runtime cost from shot-based noisy sampling vs.
  exact statevector calculation (train 100.3s -> 188.9s, predict 98.5s -> 335.2s). Useful,
  honest evidence for a "real NISQ hardware would likely perform somewhat worse and much
  slower" discussion point.
- Results: results/novelty/noise_simulation.csv

## ALL EXPERIMENTAL PHASES (0-6) COMPLETE. Proceeding to Phase 7: paper writing.

## Phase 7 — Paper Writing [x] DONE
- [x] Reviewed all 9 reference papers in qc_miniproj/papers/ via a research fork; discarded
      one (Rosenberger, IJEETR) as an unrelated/mismatched paper, flagged one
      (Lopez Garcia et al., preprints.org) as non-peer-reviewed but still citable as a
      benchmark data point
- [x] Confirmed target format from the IOP Publishing template found alongside the papers:
      numbered sections, numbered bracketed references [1]...[n], Abstract+Keywords block
- [x] Wrote Hybrid_Quantum_Fraud_Detection_Paper.docx (via build_paper.py, python-docx)
      covering: Title/Abstract, Literature Review (4 subsections), Methodology (11
      subsections covering the original pipeline + all 6 extensions), Proof of
      Concept/Implementation, Result Analysis and Comparative Analysis (8 subsections with
      7 data tables, all real numbers from Phases 1-6), References (13 sources)
- Output: Hybrid_Quantum_Fraud_Detection_Paper.docx (repo root)

## Phase 8 — Statistical Significance Testing
- [x] McNemar's test: best classical model (Random Forest, best across balancing conditions)
      vs. VQC (both at best-F1 thresholds from Phase 1), per balancing condition, full test
      set. Used EXISTING per-sample data, no rerun needed.
      **Result**: classical significantly outperforms VQC in ALL THREE conditions
      (None: b=5136,c=4,p~0; SMOTE: b=118,c=8,p=3.16e-26; ADASYN: b=522,c=7,p=2.55e-144) --
      quantifies with a real hypothesis test what Table 1-2 showed descriptively.
- [x] Paired significance tests (paired t-test + Wilcoxon signed-rank, N=5 seeds) across VQC
      balancing conditions on F1/ROC-AUC. Used EXISTING data (vqc_multiseed_raw.csv), no rerun.
      **Result**: None vs SMOTE is NOT significant (p=0.09 F1, p=0.19 ROC-AUC) -- consistent
      with Phase 3's finding that SMOTE's improvement over no-balancing is real but modest.
      None vs ADASYN and SMOTE vs ADASYN ARE significant by paired t-test (p<0.05 for both
      metrics) -- ADASYN is not just noisier (Phase 3), it's significantly WORSE on average.
      Wilcoxon can't reach p<0.05 with only N=5 pairs (min possible p=0.0625) -- noted as a
      limitation of the small seed count, paired t-test is directionally consistent throughout.
- [x] Bug found+fixed: same "None"-read-as-NaN pandas gotcha as Phase 1, this time in
      vqc_multiseed_raw.csv -- fixed with keep_default_na=False.
- [x] McNemar's test: QSVM vs. VQC on the Phase 2 matched subset. Modified
      src/novelty/qsvm_kernel.py to also save per-sample predictions, reran (~13 min).
      **Correctness check result**: QSVM's numbers reproduced EXACTLY (deterministic given
      the precomputed kernel), but VQC's numbers shifted noticeably (e.g. None: F1
      0.6748->0.6235) despite identical settings -- COBYLA's initial point is not seeded by
      our RANDOM_STATE in this qiskit-machine-learning version, so VQC is not perfectly
      reproducible run-to-run even with everything else fixed. This is independent evidence
      reinforcing Phase 3's multi-seed instability finding and is worth stating explicitly in
      the paper's limitations.
      **Significance result**: QSVM significantly outperforms VQC in ALL THREE conditions
      (None: b=43,c=10,p=6e-6; SMOTE: b=40,c=9,p=9e-6; ADASYN: b=83,c=38,p=5.3e-5) --
      confirms Phase 2's descriptive finding with a real hypothesis test.
- [ ] Update paper's Result Analysis section with a new significance-testing subsection
- Results: results/novelty/mcnemar_classical_vs_vqc.csv, paired_tests_multiseed.csv,
  mcnemar_qsvm_vs_vqc.csv, qsvm_vs_vqc_predictions.csv

## Phase 8 COMPLETE (pending paper doc update). Proceeding to Phase 9-11 (user-requested):
## related-work comparison table, cost-benefit framing, real IBM Quantum hardware run.

## Phase 10 — Real IBM Quantum Hardware Run [ABANDONED, documented as a limitation]
- [x] Installed qiskit-ibm-runtime 0.49.0
- [x] Confirmed via a live connection attempt that this qiskit-ibm-runtime version no longer
      supports the legacy no-CRN "ibm_quantum" channel -- only "ibm_cloud" /
      "ibm_quantum_platform", both of which require an explicit instance CRN even for the
      free/open plan
- [x] User's existing IBM account is a university-managed org account ("Uni" / watsonx) with
      no permission to create new instances (admin-only) -- confirmed via screenshot
      ("You do not have permission to create new instances in this account")
- [x] Attempted a personal (non-university) IBM Cloud account instead -- its free/Lite plan
      instance-creation flow requires payment card details for identity verification
- [x] User made an informed decision NOT to enter payment details for a free-tier account --
      a reasonable privacy/financial choice, not a technical failure
- **Decision: real hardware validation is explicitly dropped and documented as a stated
  limitation / future work item in the paper**, with Phase 6's noise-model simulation serving
  as the NISQ-realism evidence instead. Local credential files (~/.ibm_quantum_token,
  ~/.ibm_quantum_instance) were created during troubleshooting and have been deleted -- no
  IBM credentials are retained anywhere in this project.

## ALL 7 PHASES COMPLETE. Phase 8 in progress.

## Housekeeping
- Commit after each phase completes (git commit only, no push — user is not a GitHub
  contributor on this repo and wants it to stay that way).
