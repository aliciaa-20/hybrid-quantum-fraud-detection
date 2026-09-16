"""
Builds the publication-oriented paper document from the Phase 1-6 novelty
results plus the original submission's data. Run with:
    .venv/bin/python build_paper.py
Outputs: Hybrid_Quantum_Fraud_Detection_Paper.docx
"""

from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

style = doc.styles["Normal"]
style.font.name = "Times New Roman"
style.font.size = Pt(11)


def h1(text, num=None):
    p = doc.add_heading(f"{num}. {text}" if num else text, level=1)
    return p


def h2(text):
    return doc.add_heading(text, level=2)


def para(text, italic=False, bold=False, align=None):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.italic = italic
    run.bold = bold
    if align:
        p.alignment = align
    return p


def bullet(text):
    doc.add_paragraph(text, style="List Bullet")


def make_table(headers, rows):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Light Grid Accent 1"
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = h
        for p in hdr[i].paragraphs:
            for r in p.runs:
                r.bold = True
    for row in rows:
        cells = table.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = str(val)
    doc.add_paragraph()


# =====================================================================
# TITLE PAGE
# =====================================================================

title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = title.add_run(
    "A Hybrid Quantum Machine Learning Framework for Credit Card Fraud "
    "Detection: A Comparative Study of Variational and Kernel-Based "
    "Quantum Classifiers under Class Imbalance"
)
run.bold = True
run.font.size = Pt(16)

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
sub.add_run("Alicia Theresa Pereira").bold = True
p2 = doc.add_paragraph()
p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
p2.add_run("B.Tech Computer Science and Engineering (Artificial Intelligence and Machine Learning)")
p3 = doc.add_paragraph()
p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
p3.add_run("GitHub Repository: https://github.com/aliciaa-20/hybrid-quantum-fraud-detection")

doc.add_page_break()

# =====================================================================
# ABSTRACT
# =====================================================================

h2("Abstract")
para(
    "Credit card fraud detection is a severely imbalanced binary classification "
    "problem in which fraudulent transactions represent a small fraction of the "
    "total volume, making naive accuracy an unreliable indicator of model quality. "
    "This paper presents a hybrid quantum machine learning framework that combines "
    "Mutual Information feature selection, SMOTE/ADASYN class balancing, a "
    "four-qubit Variational Quantum Classifier (VQC), and classical baselines "
    "(Logistic Regression, Random Forest, Support Vector Machine) on the ULB "
    "Credit Card Fraud Detection dataset. Building on an initial exploratory "
    "implementation, we extend the study along six axes to establish a "
    "methodologically defensible comparison: (1) decision-threshold optimization, "
    "(2) a quantum-kernel classifier (QSVM) evaluated head-to-head against VQC, "
    "(3) multi-seed robustness analysis, (4) a feature-map/ansatz ablation, "
    "(5) a qubit-count scaling study, and (6) a NISQ-representative noise-model "
    "simulation. Results show that threshold tuning, not balancing strategy alone, "
    "recovers most of classical models' precision-recall trade-off (Random Forest "
    "with ADASYN: F1 improves from 0.064 to 0.764), while VQC's probability outputs "
    "show limited separative power on the full imbalanced test set even under "
    "optimal thresholds. On a class-balanced evaluation subset, however, a quantum "
    "kernel classifier (QSVM) outperforms VQC in every balancing condition "
    "(F1 up to 0.843 vs. 0.675), indicating that quantum kernel methods are better "
    "suited to this feature-selected, low-qubit fraud detection task than "
    "variational circuits. A qubit-scaling study further shows that performance "
    "degrades and training/inference time grows sharply as qubit count increases "
    "under a fixed training budget, consistent with known VQC trainability "
    "limitations. These findings position the framework as a rigorous, "
    "reproducible case study of the current strengths and limitations of "
    "near-term quantum machine learning for imbalanced financial fraud detection."
)
h2("Keywords")
para(
    "Quantum Machine Learning, Variational Quantum Classifier, Quantum Kernel Method, "
    "Credit Card Fraud Detection, Class Imbalance, SMOTE, ADASYN, Qiskit, NISQ"
)

doc.add_page_break()

# =====================================================================
# 1. INTRODUCTION
# =====================================================================

h1("Introduction", 1)
para(
    "Credit card fraud detection is one of the most widely studied imbalanced "
    "classification problems in applied machine learning: fraudulent transactions "
    "typically represent well under 1% of all transactions, so a classifier can "
    "achieve near-perfect accuracy while detecting almost no fraud. Quantum machine "
    "learning (QML) has been proposed as a candidate approach for such problems, "
    "on the premise that quantum feature maps can access exponentially large "
    "Hilbert spaces that may separate classes more effectively than classical "
    "kernels at equivalent computational cost. However, most published QML-for-fraud "
    "studies report a single configuration and a single run, leaving open basic "
    "questions of robustness, architecture sensitivity, and scalability that any "
    "classical machine learning study would be expected to address."
)
para(
    "This paper extends an initial exploratory hybrid quantum machine learning "
    "pipeline -- Mutual Information feature selection, SMOTE/ADASYN balancing, and "
    "a Variational Quantum Classifier compared against classical baselines -- into "
    "a more methodologically complete comparative study. We add decision-threshold "
    "analysis, a second quantum method (a fidelity quantum kernel classifier), "
    "multi-seed statistical robustness, architecture ablations, a qubit-count "
    "scaling study, and a noise-aware simulation, in order to characterize not just "
    "whether the quantum classifier works, but why it performs as it does and under "
    "what conditions a quantum kernel approach might be preferable to a variational "
    "one."
)

# =====================================================================
# 2. LITERATURE REVIEW
# =====================================================================

h1("Literature Review", 2)

h2("2.1 Classical Machine Learning for Fraud Detection")
para(
    "Classical fraud detection has been reviewed extensively; Mardan and Abdulazeez "
    "[1] survey a broad range of classical algorithms and preprocessing strategies "
    "for financial fraud detection, establishing accuracy, precision, recall, "
    "F1-score, and ROC-AUC as the standard evaluation suite under class imbalance -- "
    "the same suite adopted in this study. Lopez Garcia et al. [2] benchmark 52 "
    "classical and quantum-inspired methods on fraud data and find Random Forest to "
    "be the strongest classical performer (F1 = 0.87), while noting that "
    "quantum-inspired circuits underperform (F1 = 0.66) once feature counts are "
    "truncated to fit a small number of qubits -- a cautionary result directly "
    "relevant to this paper's own qubit-count scaling findings (Section 5.5)."
)

h2("2.2 Variational Quantum Classifiers for Fraud and Anomaly Detection")
para(
    "Several recent studies apply Variational Quantum Classifiers (VQC) or "
    "quantum neural networks (QNN) to fraud detection. Reddy et al. [3] combine a "
    "VQC with a Random Forest in an OR-decision hybrid architecture, using PCA and "
    "SMOTE preprocessing, and report 96.9% accuracy on a Kaggle credit card "
    "dataset -- an architecture directly comparable to the VQC-plus-classical-baseline "
    "structure used here, though their hybrid decision rule differs from this "
    "paper's independent-model comparison. Ubale et al. [4] propose a Hybrid "
    "Quantum LSTM implemented in PennyLane for sequential fraud detection, reporting "
    "95.33% accuracy with markedly fast per-epoch training; notably, their "
    "qubit-scaling experiment (10 to 12 qubits, with proportionally larger training "
    "sets) shows accuracy improving with more qubits, which contrasts with this "
    "paper's finding (Section 5.5) that additional qubits hurt performance when the "
    "training budget is held fixed -- suggesting that qubit count and training "
    "data volume must scale together for VQC methods to benefit from larger "
    "circuits. Li et al.'s HQRNN-FD [5] combines a VQC (with data re-uploading "
    "encoding) with an RNN and self-attention mechanism, and is, to our knowledge, "
    "the closest methodological precedent to this paper's novelty extensions: it "
    "independently runs noise-robustness experiments (depolarizing, bit-flip, and "
    "phase-flip noise at multiple severities), a qubit-scaling ablation (2, 4, and 6 "
    "qubits), and a component ablation, reporting F1 = 0.90 and outperforming "
    "plain QNN and QRNN baselines. Our Sections 5.4-5.6 replicate this style of "
    "ablation independently on a simpler VQC architecture and a different dataset, "
    "and arrive at qualitatively consistent conclusions regarding noise sensitivity "
    "and qubit-count trade-offs."
)

h2("2.3 Quantum Kernel Methods, Annealing, and Autoencoders")
para(
    "Beyond variational circuits, quantum kernel and annealing-based methods have "
    "also been applied to fraud detection. Loke et al. [6] use CVQBoost on a "
    "Dirac-3 photonic quantum annealer with heterogeneous weak classifiers "
    "(KNN, LDA, Logistic Regression, XGBoost), reporting an AUC-PR of 0.81 versus "
    "0.74 for a classical baseline on real quantum hardware, demonstrating that "
    "quantum-assisted ensembles can outperform classical counterparts in a "
    "production-realistic setting. Wang et al. [7] formulate an SVM as a QUBO "
    "problem solved via D-Wave quantum annealing, comparing it against twelve "
    "classical methods on two datasets, and find that the quantum approach wins on "
    "highly imbalanced, high-dimensional, time-series data but not on a more "
    "moderately imbalanced dataset -- a nuanced result that motivates this paper's "
    "own decision to test multiple imbalance-handling strategies (SMOTE, ADASYN, "
    "and no balancing) rather than assuming quantum advantage is uniform across "
    "conditions. Huot et al. [8] propose a Quantum Autoencoder for fraud detection "
    "using an encoder-only architecture with a fidelity-threshold classifier, "
    "reporting a G-mean of 0.946 and testing both noiseless and IBM FakeCairo "
    "noise-model conditions alongside a circuit-depth ablation -- a design closely "
    "paralleling this paper's Section 5.4 (architecture ablation) and Section 5.6 "
    "(noise simulation), independently corroborating that noise-aware evaluation "
    "and architecture search are necessary steps for credible QML fraud detection "
    "claims. Orbe et al. [9] evaluate five \"quantum-inspired\" classifiers built on "
    "explicit Hilbert-space feature expansion rather than executed quantum circuits, "
    "with their best model (a quantum-inspired MLP) reaching 99.35% accuracy and "
    "0.97 AUC on SMOTEENN-balanced data, validated with McNemar's statistical test "
    "and an explicit cost-benefit analysis -- a methodological rigor (statistical "
    "significance testing, economic framing) this paper aims to approach through "
    "its multi-seed robustness analysis (Section 5.3)."
)

h2("2.4 Research Gap")
para(
    "Across this literature, quantum approaches to fraud detection are frequently "
    "reported as single-configuration, single-run results, with architecture "
    "ablation, multi-seed robustness, and noise-awareness present in only a "
    "minority of studies (notably [5] and [8]). Comparisons between distinct "
    "quantum paradigms -- variational circuits versus quantum kernel methods -- on "
    "the same dataset and feature set are rarer still. This paper addresses that "
    "gap directly: it extends an initial VQC-only pipeline into a six-part "
    "comparative study spanning threshold optimization, a second quantum method "
    "(QSVM), robustness analysis, architecture ablation, qubit scaling, and noise "
    "simulation, evaluated consistently on the same ULB fraud dataset and feature "
    "set throughout."
)

doc.add_page_break()

# =====================================================================
# 3. METHODOLOGY
# =====================================================================

h1("Methodology", 3)

h2("3.1 Dataset")
para(
    "The study uses the Credit Card Fraud Detection dataset released by the "
    "Machine Learning Group of Universite Libre de Bruxelles (ULB), containing "
    "284,807 transactions with 492 fraudulent cases (0.17%), 30 input features "
    "(V1-V28 from PCA transformation, Time, and Amount), and a binary Class label."
)

h2("3.2 Preprocessing and Feature Selection")
para(
    "Duplicate records were removed prior to a stratified 80/20 train-test split "
    "(random_state=42). Features were standardized (fit on training data only) and "
    "Mutual Information (SelectKBest with mutual_info_classif) was used to select "
    "the four most informative features -- V10, V12, V14, and V17 -- mapping "
    "naturally onto a four-qubit quantum circuit. Section 5.5 extends this to "
    "k in {2, 4, 6, 8} features to study the effect of qubit count."
)

h2("3.3 Class Balancing")
para(
    "Three training conditions were evaluated throughout: no balancing (original "
    "class distribution), SMOTE (Synthetic Minority Oversampling Technique), and "
    "ADASYN (Adaptive Synthetic Sampling). Balancing was applied to training data "
    "only; the test set remained untouched in all experiments."
)

h2("3.4 Classical Baselines")
para(
    "Logistic Regression, Random Forest (100 trees, max depth 10), and Support "
    "Vector Machine (RBF kernel) were trained on the same selected features under "
    "each balancing condition, using scikit-learn with fixed random_state=42."
)

h2("3.5 Variational Quantum Classifier (VQC)")
para(
    "The VQC was implemented in Qiskit and Qiskit Machine Learning, encoding "
    "features via a four-qubit ZZFeatureMap (2 repetitions, linear entanglement) "
    "followed by a RealAmplitudes ansatz (2 repetitions, linear entanglement), "
    "optimized with COBYLA (30 iterations). Features were scaled to [-pi, pi] "
    "prior to encoding. Due to the computational cost of quantum circuit "
    "simulation, VQC training used a fixed 1000-1800 row subsample per balancing "
    "condition (100 fraud + 900 legitimate before balancing) rather than the full "
    "training set, while evaluation used the complete, untouched test set of "
    "56,747 transactions."
)

h2("3.6 Extension 1: Decision-Threshold Optimization")
para(
    "All models' default 0.5 decision threshold was replaced with a systematic "
    "sweep over the probability score range, reporting the threshold that "
    "maximizes F1-score and, separately, the threshold that maximizes Youden's J "
    "statistic (TPR - FPR) from the ROC curve. Classical model probabilities were "
    "regenerated (predict_proba) alongside the VQC's existing probability outputs "
    "to allow a like-for-like comparison. A pandas parsing artefact was identified "
    "and corrected during this step: the string label \"None\" (no balancing) is "
    "silently interpreted as a missing value on CSV read unless "
    "keep_default_na=False is set, which had caused that condition's rows to be "
    "dropped from earlier ad hoc analysis."
)

h2("3.7 Extension 2: Quantum Kernel Classifier (QSVM)")
para(
    "A second quantum method was introduced: a fidelity quantum kernel "
    "(FidelityQuantumKernel over the same ZZFeatureMap) combined with a classical "
    "Support Vector Classifier using a precomputed kernel matrix. Because kernel "
    "evaluation is pairwise (train x test circuit executions, unlike VQC's "
    "per-sample forward pass), a small-scale timing test (60x60 evaluations, "
    "measuring approximately 26.5 evaluations/second for symmetric train-train "
    "kernels and 103 evaluations/second for non-symmetric evaluation kernels) was "
    "run first to establish feasible problem sizes. Based on this, QSVM was "
    "trained on a 120-row subsample (60 fraud, 60 legitimate) per balancing "
    "condition and evaluated on a fixed, class-enriched subset of 250 test "
    "transactions (all 95 fraud cases in the test set plus 155 randomly sampled "
    "legitimate transactions, approximately 38% fraud rate). VQC was retrained and "
    "re-evaluated on this identical subset to enable a fair, matched comparison "
    "between the two quantum methods; these matched-subset numbers are reported "
    "separately from, and are not directly comparable to, the full-test-set "
    "headline VQC results, owing to the deliberate class enrichment."
)

h2("3.8 Extension 3: Multi-Seed Robustness")
para(
    "The original VQC results were each a single run on one fixed random "
    "subsample. To assess robustness, the full pipeline (subsample draw, "
    "SMOTE/ADASYN application, VQC training, and evaluation on the full test set) "
    "was repeated for five random seeds (42, 7, 123, 2024, 99) per balancing "
    "condition, reporting mean and standard deviation for all metrics."
)

h2("3.9 Extension 4: Feature Map and Ansatz Ablation")
para(
    "To isolate which architectural component drives VQC performance, a 2x2 grid "
    "was evaluated: feature maps {ZZFeatureMap, PauliFeatureMap with Z and ZZ "
    "Pauli terms} crossed with ansatze {RealAmplitudes, EfficientSU2}, holding the "
    "SMOTE training condition and COBYLA optimizer fixed, evaluated on the full "
    "test set."
)

h2("3.10 Extension 5: Qubit-Count Scaling Study")
para(
    "Mutual Information feature selection was repeated for k in {2, 4, 6, 8} "
    "features (equivalently, qubits), with k=4 exactly reproducing the original "
    "feature selection (V10, V12, V14, V17) as an internal consistency check. For "
    "each k, VQC was retrained on a matched, unbalanced 1000-row subsample and "
    "evaluated on the full test set, recording both predictive metrics and "
    "wall-clock training/inference time."
)

h2("3.11 Extension 6: Noise-Model Simulation")
para(
    "The best-performing VQC configuration identified in this study "
    "(ZZFeatureMap + RealAmplitudes on SMOTE-balanced data) was retrained and "
    "re-evaluated under an illustrative NISQ-representative noise model using "
    "Qiskit Aer's noisy sampler: 0.1% depolarizing error on single-qubit gates, "
    "1% depolarizing error on two-qubit (CX) gates, and 1% bit-flip readout error "
    "on all qubits. A small-scale timing check (10 optimizer iterations on 60 "
    "samples) confirmed that noisy simulation was computationally tractable at "
    "full problem scale before committing to the full run."
)

doc.add_page_break()

# =====================================================================
# 4. PROOF OF CONCEPT / IMPLEMENTATION
# =====================================================================

h1("Proof of Concept / Implementation", 4)

para(
    "The complete implementation is organized as a reproducible Python pipeline "
    "using Qiskit 2.5.2, Qiskit Machine Learning 0.9.1, Qiskit Aer 0.17.2, "
    "scikit-learn, and imbalanced-learn, structured as follows:"
)

h2("4.1 Repository Structure")
bullet("data/ -- raw and intermediate CSV datasets (excluded from version control due to size)")
bullet("src/ -- original pipeline scripts: preprocessing, balancing, classical_models, "
       "quantum_data, quantum_model/quantum_final, confusion_matrices, final_results")
bullet("src/novelty/ -- the six extension scripts developed in this study: "
       "classical_predictions.py, threshold_optimization.py, qsvm_kernel.py, "
       "vqc_multiseed.py, ablation_featuremap_ansatz.py, qubit_scaling.py, "
       "noise_simulation.py")
bullet("results/ and results/novelty/ -- recorded metrics, predictions, and figures "
       "from the original and extended experiments respectively")
bullet("PHASES.md -- a running implementation log documenting feasibility checks, "
       "design decisions, and findings for each extension, maintained throughout "
       "development for transparency and reproducibility")

h2("4.2 Reproducibility and Feasibility Verification")
para(
    "Each extension was preceded by an explicit feasibility check before committing "
    "compute time to a full-scale run: library API availability was verified for "
    "all required Qiskit/Qiskit Aer classes; VQC and QSVM timing were measured at "
    "small scale to project full-scale runtime before execution; Mutual Information "
    "feature rankings were checked for stability up to eight features; and noisy "
    "sampler integration with VQC was validated on a toy problem before the full "
    "noise-model run. This practice surfaced two notable implementation issues "
    "during development: (i) a pandas CSV-parsing artefact where the string label "
    "\"None\" was silently read as a missing value, corrected via "
    "keep_default_na=False; and (ii) a background process termination during the "
    "qubit-scaling experiment due to transient system-wide memory pressure "
    "unrelated to the script itself, resolved by adding checkpoint/resume support "
    "so completed configurations were not recomputed."
)

doc.add_page_break()

# =====================================================================
# 5. RESULT ANALYSIS AND COMPARATIVE ANALYSIS
# =====================================================================

h1("Result Analysis and Comparative Analysis", 5)

h2("5.1 Baseline Results (Original Configuration)")
para(
    "Table 1 reproduces the original single-run comparison across classical and "
    "quantum models at the default 0.5 decision threshold."
)
make_table(
    ["Model", "Balancing", "Accuracy", "Precision", "Recall", "F1", "ROC-AUC"],
    [
        ["Random Forest", "None", "0.9994", "0.8831", "0.7158", "0.7907", "0.9449"],
        ["SVM", "None", "0.9992", "0.7708", "0.7789", "0.7749", "0.8901"],
        ["Logistic Regression", "None", "0.9990", "0.8475", "0.5263", "0.6494", "0.9260"],
        ["SVM", "SMOTE", "0.9937", "0.1836", "0.8000", "0.2986", "0.9392"],
        ["Random Forest", "SMOTE", "0.9827", "0.0747", "0.8211", "0.1370", "0.9326"],
        ["Logistic Regression", "SMOTE", "0.9772", "0.0583", "0.8316", "0.1090", "0.9259"],
        ["Random Forest", "ADASYN", "0.9589", "0.0334", "0.8421", "0.0642", "0.9348"],
        ["SVM", "ADASYN", "0.9180", "0.0178", "0.8842", "0.0348", "0.9301"],
        ["VQC", "SMOTE", "0.9189", "0.0119", "0.5789", "0.0234", "0.8165"],
        ["Logistic Regression", "ADASYN", "0.8671", "0.0109", "0.8737", "0.0215", "0.9267"],
        ["VQC", "None", "0.9144", "0.0083", "0.4211", "0.0162", "0.7673"],
        ["VQC", "ADASYN", "0.8018", "0.0062", "0.7368", "0.0123", "0.8089"],
    ],
)
para(
    "Random Forest without balancing achieves the strongest overall F1 (0.7907) "
    "and ROC-AUC (0.9449). Balancing sharply increases classical models' recall but "
    "collapses precision under the default threshold, and VQC lags every classical "
    "configuration on this metric."
)

h2("5.2 Threshold Optimization")
para(
    "Table 2 shows that most of the classical models' apparent precision collapse "
    "under balancing is an artefact of the default threshold, not of the balancing "
    "method itself."
)
make_table(
    ["Model", "Balancing", "Default F1", "Best-F1 (threshold)", "Youden-J F1"],
    [
        ["Random Forest", "None", "0.7907", "0.8043 (@0.120)", "0.0886"],
        ["Random Forest", "ADASYN", "0.0642", "0.7636 (@0.988)", "0.1195"],
        ["Random Forest", "SMOTE", "0.1370", "0.7831 (@0.999)", "0.1062"],
        ["Logistic Regression", "ADASYN", "0.0215", "0.6923 (@0.994)", "0.0885"],
        ["SVM", "SMOTE", "0.1382", "0.7243 (@1.000)", "0.0913"],
        ["VQC", "None", "0.0162", "0.0167 (@0.483)", "0.0092"],
        ["VQC", "SMOTE", "0.0234", "0.0395 (@0.889)", "0.0142"],
        ["VQC", "ADASYN", "0.0123", "0.0578 (@0.799)", "0.0164"],
    ],
)
para(
    "Random Forest with ADASYN improves from F1 = 0.0642 to F1 = 0.7636 -- nearly "
    "matching the untuned no-balancing baseline -- purely by choosing a better "
    "threshold. VQC shows a comparatively negligible improvement (best F1 remains "
    "below 0.06 in every condition), indicating that its probability outputs carry "
    "little separative information on the full, extremely imbalanced test set: "
    "this is not primarily a threshold-selection problem for the quantum model, "
    "but a more fundamental limitation of the decision function learned under this "
    "training budget."
)

h2("5.3 Quantum Kernel Classifier (QSVM) vs. VQC")
para(
    "Table 3 compares QSVM and VQC on an identical, class-enriched evaluation "
    "subset (250 transactions, approximately 38% fraud), designed to make the "
    "pairwise quantum kernel computation tractable while retaining enough positive "
    "examples for meaningful precision/recall estimation."
)
make_table(
    ["Model", "Balancing", "Accuracy", "Precision", "Recall", "F1", "ROC-AUC"],
    [
        ["QSVM", "None", "0.876", "0.8636", "0.8000", "0.8306", "0.9169"],
        ["VQC (matched)", "None", "0.788", "0.8088", "0.5789", "0.6748", "0.8368"],
        ["QSVM", "SMOTE", "0.884", "0.8667", "0.8211", "0.8432", "0.9135"],
        ["VQC (matched)", "SMOTE", "0.752", "0.7143", "0.5789", "0.6395", "0.8211"],
        ["QSVM", "ADASYN", "0.656", "0.5455", "0.5684", "0.5567", "0.6893"],
        ["VQC (matched)", "ADASYN", "0.604", "0.4833", "0.6105", "0.5395", "0.6461"],
    ],
)
para(
    "QSVM outperforms VQC on every balancing condition on this matched subset, "
    "with the largest margin under SMOTE (F1 0.8432 vs. 0.6395). This suggests "
    "that, for this feature-selected, low-qubit fraud detection task, a quantum "
    "kernel method captures more useful structure than a variational circuit of "
    "comparable qubit count, at the cost of quadratic (pairwise) evaluation "
    "complexity that limits its scalability to large test sets. Notably, both "
    "quantum methods perform far better on this class-balanced subset than the "
    "full-test-set VQC results in Table 1, reinforcing that extreme class "
    "imbalance -- rather than an inherent limitation of quantum circuits -- was "
    "the dominant driver of the original near-zero F1 scores."
)

h2("5.4 Multi-Seed Robustness")
para(
    "Table 4 reports mean +/- standard deviation across five random seeds for VQC "
    "under each balancing condition, evaluated on the full test set."
)
make_table(
    ["Balancing", "Accuracy", "Precision", "Recall", "F1", "ROC-AUC"],
    [
        ["None", "0.9145 +/- 0.0452", "0.0095 +/- 0.0048", "0.3916 +/- 0.0554",
         "0.0185 +/- 0.0092", "0.7743 +/- 0.0633"],
        ["SMOTE", "0.9196 +/- 0.0291", "0.0124 +/- 0.0047", "0.5368 +/- 0.0505",
         "0.0241 +/- 0.0090", "0.7994 +/- 0.0604"],
        ["ADASYN", "0.5625 +/- 0.2283", "0.0029 +/- 0.0013", "0.6211 +/- 0.0906",
         "0.0057 +/- 0.0026", "0.6472 +/- 0.0760"],
    ],
)
para(
    "SMOTE's mean F1 (0.0241) closely reproduces the original single-run value "
    "(0.0234), indicating that result was reproducible. ADASYN, by contrast, shows "
    "very high variance -- an accuracy standard deviation of 0.2283 against a mean "
    "of 0.5625 -- and the original paper's single ADASYN run (accuracy 0.8018) "
    "sits well above this mean, meaning it was not representative of typical "
    "performance under that balancing method. This result underscores the "
    "importance of multi-seed evaluation before drawing conclusions from any "
    "single VQC run, particularly under ADASYN."
)

h2("5.5 Feature Map and Ansatz Ablation")
make_table(
    ["Feature Map", "Ansatz", "F1", "ROC-AUC", "Train Time (s)"],
    [
        ["ZZFeatureMap", "RealAmplitudes (original)", "0.0288", "0.8344", "101.0"],
        ["ZZFeatureMap", "EfficientSU2", "0.0177", "0.7802", "106.8"],
        ["PauliFeatureMap(Z,ZZ)", "RealAmplitudes", "0.0256", "0.8323", "89.7"],
        ["PauliFeatureMap(Z,ZZ)", "EfficientSU2", "0.0136", "0.7624", "106.0"],
    ],
)
para(
    "Ansatz choice has a larger effect than feature map choice: RealAmplitudes "
    "outperforms EfficientSU2 regardless of feature map (by roughly 1.6x in F1). "
    "The original paper's exact configuration, ZZFeatureMap combined with "
    "RealAmplitudes, is the best-performing of the four combinations tested here, "
    "indicating the original architectural choice was well-founded rather than "
    "arbitrary."
)

h2("5.6 Qubit-Count Scaling")
make_table(
    ["Qubits", "Selected Features", "F1", "ROC-AUC", "Train+Predict Time (s)"],
    [
        ["2", "V14, V17", "0.0822", "0.9227", "56.2"],
        ["4", "V10, V12, V14, V17", "0.0135", "0.7638", "160.0"],
        ["6", "+ V11, V16", "0.0024", "0.3754", "416.0"],
        ["8", "+ V3, V4", "0.0042", "0.5512", "1225.7"],
    ],
)
para(
    "Under a fixed training budget (1000 samples, 30 COBYLA iterations), "
    "performance is best at k=2 qubits and degrades sharply as qubit count "
    "increases -- the 6-qubit configuration performs worse than random guessing "
    "(ROC-AUC 0.3754) -- while combined training and inference time grows more "
    "than 20-fold from k=2 to k=8. This is consistent with known VQC trainability "
    "limitations (e.g. barren plateaus): larger circuits introduce more variational "
    "parameters that cannot be optimized effectively within the same fixed "
    "iteration budget, so adding features/qubits without proportionally increasing "
    "training data and optimizer iterations is counterproductive. This mirrors "
    "the qubit-truncation degradation reported by Lopez Garcia et al. [2], but "
    "contrasts with Ubale et al.'s [4] finding that accuracy improves with more "
    "qubits when training data volume scales alongside qubit count -- together, "
    "these results suggest qubit count and training budget must be scaled jointly."
)

h2("5.7 Noise-Model Simulation")
make_table(
    ["Condition", "F1", "ROC-AUC", "Train Time (s)", "Predict Time (s)"],
    [
        ["Noiseless", "0.0195", "0.8169", "100.3", "98.5"],
        ["Noisy (depolarizing + readout)", "0.0157", "0.7943", "188.9", "335.2"],
    ],
)
para(
    "An illustrative NISQ-representative noise model (0.1%/1% depolarizing error "
    "on single-/two-qubit gates, 1% readout error) produces a modest but "
    "measurable performance degradation (F1 0.0195 to 0.0157, ROC-AUC 0.8169 to "
    "0.7943) alongside a substantial runtime cost from shot-based noisy sampling "
    "relative to exact statevector simulation (training time nearly doubles, "
    "prediction time more than triples). This is consistent with Huot et al.'s [8] "
    "noiseless-versus-noisy comparison and reinforces that current VQC "
    "performance on this task, already limited on the full imbalanced test set, "
    "would likely be further degraded and considerably slower on real NISQ "
    "hardware."
)

h2("5.8 Summary of Findings")
bullet("Decision-threshold optimization, not balancing method choice alone, "
       "recovers most classical models' precision-recall trade-off; VQC does "
       "not benefit comparably, indicating a deeper limitation in its learned "
       "decision function on the full imbalanced test set.")
bullet("On a class-balanced evaluation, a quantum kernel method (QSVM) "
       "consistently outperforms VQC, suggesting kernel-based quantum methods "
       "are better suited to this task at current qubit counts, though at "
       "higher (pairwise) evaluation cost.")
bullet("VQC results are seed-sensitive, especially under ADASYN; single-run "
       "results (including the original study's) should be interpreted with "
       "this variance in mind.")
bullet("The original ZZFeatureMap+RealAmplitudes architecture was validated as "
       "the best of four tested feature-map/ansatz combinations.")
bullet("More qubits does not help without a correspondingly larger training "
       "budget: performance peaked at 2 qubits and degraded sharply at 6-8 "
       "qubits under the same fixed training/optimization budget.")
bullet("A realistic noise model modestly degrades VQC performance and "
       "substantially increases computational cost, reinforcing that current "
       "NISQ-era hardware would not improve on these already-limited results.")
para(
    "Taken together, these results support a measured conclusion: the quantum "
    "methods evaluated here do not outperform well-tuned classical baselines on "
    "this dataset, but the framework developed -- spanning threshold analysis, "
    "a second quantum paradigm, robustness testing, architecture search, "
    "scalability analysis, and noise simulation -- provides a template for "
    "rigorously characterizing quantum machine learning methods on imbalanced "
    "financial fraud detection problems, addressing a gap identified in the "
    "reviewed literature where such multi-faceted evaluation remains uncommon."
)

doc.add_page_break()

# =====================================================================
# 6. REFERENCES
# =====================================================================

h1("References", 6)

references = [
    "Mardan, H. and Abdulazeez, A. \"A Comprehensive Review of Machine Learning "
    "Techniques for Credit Card Fraud Detection.\" International Journal of "
    "Computer Science, 13(3), 2024.",
    "Lopez Garcia, J. et al. \"Benchmarking Classical and Quantum-Inspired "
    "Methods for Credit Card Fraud Detection.\" Preprints.org, 2025 (preprint, "
    "not peer-reviewed).",
    "Reddy, K. et al. \"Hybrid Variational Quantum Classifier and Random Forest "
    "for Credit Card Fraud Detection.\" 2026.",
    "Ubale, A. et al. \"Hybrid Quantum Long Short-Term Memory Networks for "
    "Sequential Fraud Detection.\" arXiv:2505.00137, 2025.",
    "Li, Y. et al. \"HQRNN-FD: A Hybrid Quantum Recurrent Neural Network with "
    "Self-Attention for Fraud Detection.\" Entropy, 27(9), 906, 2025.",
    "Loke, T. et al. \"Improving Credit Card Transaction Fraud Detection Using "
    "CVQBoosting on a Photonic Quantum Annealer.\" 2026.",
    "Wang, H. et al. \"Integrating Machine Learning Algorithms with Quantum "
    "Annealing Solvers for Online Fraud Detection.\" IEEE Access, 2022.",
    "Huot, F. et al. \"Quantum Autoencoder for Enhanced Fraud Detection in "
    "Imbalanced Credit Card Datasets.\" IEEE Access, 2024.",
    "Orbe, D. et al. \"Quantum-Inspired Machine Learning for Credit Card Fraud "
    "Detection.\" Machine Learning: Science and Technology, IOP Publishing, 2025.",
    "Dal Pozzolo, A. et al. \"Credit Card Fraud Detection Dataset.\" Machine "
    "Learning Group, Universite Libre de Bruxelles (ULB). "
    "https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud",
    "Qiskit contributors. \"Qiskit: An Open-Source Framework for Quantum "
    "Computing.\" IBM Quantum, 2024.",
    "Chawla, N. et al. \"SMOTE: Synthetic Minority Over-sampling Technique.\" "
    "Journal of Artificial Intelligence Research, 16, 321-357, 2002.",
    "He, H. et al. \"ADASYN: Adaptive Synthetic Sampling Approach for "
    "Imbalanced Learning.\" IEEE International Joint Conference on Neural "
    "Networks, 2008.",
]

for i, ref in enumerate(references, start=1):
    doc.add_paragraph(f"[{i}] {ref}")

doc.save(
    "/Users/aliciapereira/Downloads/VSC/hybrid-quantum-fraud-detection/"
    "Hybrid_Quantum_Fraud_Detection_Paper.docx"
)
print("Paper saved: Hybrid_Quantum_Fraud_Detection_Paper.docx")
