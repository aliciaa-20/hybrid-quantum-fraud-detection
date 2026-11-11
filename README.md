# Hybrid Quantum Machine Learning Framework for Credit Card Fraud Detection

A hybrid quantum machine learning framework for credit card fraud detection that investigates the effect of feature selection and class balancing techniques on quantum and classical machine learning models.

## Overview

Credit card fraud detection is a highly imbalanced classification problem where fraudulent transactions represent only a very small proportion of all transactions.

This project develops and evaluates a hybrid quantum machine learning pipeline combining:

- Mutual Information based feature selection
- SMOTE and ADASYN data balancing
- Quantum feature encoding
- Variational Quantum Classifier (VQC)
- Classical machine learning baselines
- Accuracy, precision, recall, F1-score, and ROC AUC evaluation

## Problem Statement

Credit card fraud datasets are extremely imbalanced, making fraud detection challenging for conventional machine learning algorithms. A model can achieve very high accuracy while still failing to identify fraudulent transactions.

This project investigates:

1. The effect of feature selection on fraud detection.
2. The effect of SMOTE and ADASYN on model performance.
3. The effectiveness of a Variational Quantum Classifier for fraud detection.
4. The performance difference between quantum and classical approaches.

## Objectives

- Study hybrid quantum machine learning for binary classification.
- Perform feature selection using Mutual Information.
- Investigate class balancing using SMOTE and ADASYN.
- Implement a Variational Quantum Classifier using Qiskit.
- Compare quantum and classical machine learning models.
- Evaluate models using accuracy, precision, recall, F1-score, and ROC AUC.
- Analyze the trade-off between fraud detection recall and false positives.

## Dataset

The project uses the **Credit Card Fraud Detection Dataset** originally released by the Machine Learning Group of ULB.

- 284,807 transactions
- 492 fraudulent transactions
- 30 input features
- Target variable: `Class`
- `Class = 0`: Legitimate transaction
- `Class = 1`: Fraudulent transaction
- Fraudulent transactions represent approximately 0.17% of the original dataset.

### Dataset Download

Download the dataset from Kaggle:

https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud

Place `creditcard.csv` inside:

```text
data/
└── creditcard.csv
```

The dataset is intentionally excluded from this repository because of its large file size.

## Methodology

```text
Credit Card Dataset
        |
        v
Data Cleaning
        |
        v
Remove Duplicate Records
        |
        v
Train/Test Split
        |
        v
Feature Scaling
        |
        v
Mutual Information Feature Selection
        |
        +-------------------+
        |                   |
        v                   v
     No Balancing       SMOTE / ADASYN
        |                   |
        +---------+---------+
                  |
                  v
       Selected Quantum Features
                  |
                  v
        Quantum Feature Mapping
                  |
                  v
      Variational Quantum Classifier
                  |
                  v
        Performance Evaluation
```

## Feature Selection

Mutual Information was used to select the four most informative features from the 30 available input features.

Selected features:

```text
V10
V12
V14
V17
```

The feature selector was fitted only on the training data to avoid test data leakage.

## Data Balancing

Three training configurations were evaluated:

### None

The original imbalanced training distribution was retained.

### SMOTE

Synthetic Minority Oversampling Technique was used to generate synthetic minority-class samples.

### ADASYN

Adaptive Synthetic Sampling was used to generate additional minority-class samples with greater emphasis on difficult examples.

Balancing was performed only on the training data. The test dataset remained untouched.

## Quantum Model

The quantum classifier was implemented using Qiskit and Qiskit Machine Learning.

### Quantum Architecture

- Number of qubits: 4
- Input features: 4
- Feature map: ZZ Feature Map
- Feature map repetitions: 2
- Entanglement: Linear
- Ansatz: Real Amplitudes
- Ansatz repetitions: 2
- Optimizer: COBYLA
- Maximum iterations: 30

The four selected classical features are encoded into a quantum circuit before being processed by the Variational Quantum Classifier.

## Classical Baselines

The quantum model was compared against:

- Logistic Regression
- Random Forest
- Support Vector Machine

The same selected features were used for the classical experiments.

## Evaluation Metrics

Because the dataset is highly imbalanced, accuracy alone is not sufficient.

- **Accuracy:** Overall proportion of correctly classified transactions.
- **Precision:** Proportion of predicted fraud cases that are actually fraudulent.
- **Recall:** Proportion of actual fraud cases that are detected.
- **F1 Score:** Harmonic mean of precision and recall.
- **ROC AUC:** Ability to distinguish fraudulent and legitimate transactions across thresholds.

## Results

### Overall Model Comparison

| Model | Balancing | Accuracy | Precision | Recall | F1 Score | ROC AUC |
|---|---|---:|---:|---:|---:|---:|
| Random Forest | None | 0.9994 | 0.8831 | 0.7158 | **0.7907** | **0.9449** |
| SVM | None | 0.9992 | 0.7708 | 0.7789 | 0.7749 | 0.8901 |
| Logistic Regression | None | 0.9990 | 0.8475 | 0.5263 | 0.6494 | 0.9260 |
| SVM | SMOTE | 0.9937 | 0.1836 | 0.8000 | 0.2986 | 0.9392 |
| Random Forest | SMOTE | 0.9827 | 0.0747 | 0.8211 | 0.1370 | 0.9326 |
| Logistic Regression | SMOTE | 0.9772 | 0.0583 | 0.8316 | 0.1090 | 0.9259 |
| Random Forest | ADASYN | 0.9589 | 0.0334 | 0.8421 | 0.0642 | 0.9348 |
| SVM | ADASYN | 0.9180 | 0.0178 | **0.8842** | 0.0348 | 0.9301 |
| VQC | SMOTE | 0.9189 | 0.0119 | 0.5789 | **0.0234** | **0.8165** |
| Logistic Regression | ADASYN | 0.8671 | 0.0109 | 0.8737 | 0.0215 | 0.9267 |
| VQC | None | 0.9144 | 0.0083 | 0.4211 | 0.0162 | 0.7673 |
| VQC | ADASYN | 0.8018 | 0.0062 | 0.7368 | 0.0123 | 0.8089 |

## Quantum Model Findings

| Configuration | Accuracy | Precision | Recall | F1 Score | ROC AUC |
|---|---:|---:|---:|---:|---:|
| VQC + None | 0.9144 | 0.0083 | 0.4211 | 0.0162 | 0.7673 |
| VQC + SMOTE | 0.9189 | 0.0119 | 0.5789 | **0.0234** | **0.8165** |
| VQC + ADASYN | 0.8018 | 0.0062 | **0.7368** | 0.0123 | 0.8089 |

### Key Observations

- SMOTE produced the best VQC F1-score and ROC AUC.
- ADASYN achieved the highest VQC recall.
- Increasing fraud recall resulted in substantially more false positives.
- VQC performance was lower than the classical baselines in this experiment.
- Class balancing significantly changed the behaviour of the quantum classifier.
- Random Forest without balancing achieved the strongest overall F1-score and ROC AUC.

The project does not claim that the quantum model outperforms classical machine learning. Instead, it investigates the behaviour of a hybrid quantum classifier under different feature selection and class balancing conditions.

## Confusion Matrices

### Random Forest + None

```text
True Negatives  = 56,642
False Positives = 9
False Negatives = 27
True Positives  = 68
```

### SVM + None

```text
True Negatives  = 56,629
False Positives = 22
False Negatives = 21
True Positives  = 74
```

### VQC + None

```text
True Negatives  = 51,846
False Positives = 4,805
False Negatives = 55
True Positives  = 40
```

### VQC + SMOTE

```text
True Negatives  = 52,091
False Positives = 4,560
False Negatives = 40
True Positives  = 55
```

### VQC + ADASYN

```text
True Negatives  = 45,429
False Positives = 11,222
False Negatives = 25
True Positives  = 70
```

## Project Structure

```text
hybrid-quantum-fraud-detection/
|
├── app/                         web app (see "Web app" below)
|   ├── backend/                 FastAPI API
|   |   ├── fraudscope/          API code: config, scoring, uploads, findings, routes
|   |   ├── export/              retrain-and-verify scripts (the reproduction gate)
|   |   └── artifacts/           exported models, sample table, results CSVs, provenance
|   └── frontend/                React + Vite + TypeScript UI
|
├── data/                        processed CSVs (gitignored; creditcard.csv is not included)
├── docs/superpowers/            web app design spec and implementation plan
|
├── results/                     baseline results, figures and predictions
|   └── novelty/                 extension experiments: QSVM, thresholds, significance, cost-benefit
├── src/                         research code
|   └── novelty/                 extension experiments
|
├── Hybrid_Quantum_Fraud_Detection_Paper.docx, QC_Paper.pdf, QC_Presentation.pptx   paper and slides
├── build_paper.py               generates the paper .docx
├── demo.py                      prints a results walkthrough
├── eda.py, test_dataset.py      exploration and dataset check
├── PHASES.md                    research phases and findings log
├── STAGES.md                    web app build stages
├── render.yaml                  backend deployment (Render)
└── requirements.txt
```

## Implementation Workflow

Run the scripts in this order:

### 1. Dataset Verification

```bash
python test_dataset.py
```

### 2. Exploratory Data Analysis

```bash
python eda.py
```

### 3. Preprocessing and Feature Selection

```bash
python src/preprocessing.py
```

### 4. Data Balancing

```bash
python src/balancing.py
```

### 5. Prepare Quantum Training Data

```bash
python src/quantum_data.py
```

### 6. Train Classical Models

```bash
python src/classical_models.py
```

### 7. Train Quantum Models

```bash
python src/quantum_final.py
```

### 8. Generate Confusion Matrices

```bash
python src/confusion_matrices.py
```

### 9. Generate Final Comparisons

```bash
python src/final_results.py
```

## Installation

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Reproducibility

The experiments use fixed random seeds where applicable, primarily:

```text
random_state = 42
```

The classical experiments use the larger available training dataset, while the quantum experiments use controlled subsets to make circuit simulation computationally feasible.

The test set remains fixed and untouched across the experiments.

## Limitations

- Quantum circuit simulation is computationally expensive.
- VQC experiments use controlled training subsets rather than the complete training dataset.
- Classical and quantum models therefore do not have identical computational budgets.
- The dataset contains an extremely small proportion of fraudulent transactions.
- Accuracy can be misleading for this problem.
- The current VQC configuration is exploratory rather than production-ready.
- The results should not be interpreted as evidence that quantum machine learning is superior to classical machine learning for fraud detection.

## Educational Value

This project demonstrates the integration of classical machine learning and quantum machine learning techniques in an imbalanced classification problem.

It provides practical experience with:

- Data preprocessing
- Feature selection
- Imbalanced learning
- SMOTE
- ADASYN
- Classical classification
- Quantum feature maps
- Variational Quantum Classifiers
- Qiskit
- Model evaluation
- Experimental comparison

## Technologies Used

- Python
- NumPy
- Pandas
- Scikit-learn
- Imbalanced-learn
- Matplotlib
- Seaborn
- Qiskit
- Qiskit Aer
- Qiskit Machine Learning

## Disclaimer

This project is developed for academic and educational purposes.

The models and results presented here are experimental and are not intended for deployment in real-world financial fraud detection systems without further validation, optimization, security analysis, and domain-specific testing.

## Author

**Alicia Pereira**

B.Tech Computer Science and Engineering  
Artificial Intelligence and Machine Learning

## License

This project is intended for educational and academic use.

## Web app

**Nice Try** turns the research into a public demo: browse real test-set transactions scored by Random Forest, QSVM and VQC side by side, upload a small CSV, and read the findings as an interactive story. It does not claim quantum advantage; in this project's own results the classical Random Forest wins.

- **Backend** (`app/backend`, FastAPI): loads exported models and a 250-row sample table at startup. Random Forest scores every row; QSVM and VQC run on a simulator and are capped to small uploads.
- **Frontend** (`app/frontend`, React + Vite + TypeScript, `motion` for animation).
- **Where the numbers come from:** the Findings page reads `results/` CSVs (copied to `app/backend/artifacts/results/`); nothing is typed in by hand.

### Run it locally
```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt fastapi uvicorn python-multipart
# terminal 1 (backend)
cd app/backend && ../../.venv/bin/uvicorn fraudscope.main:app --port 8000
# terminal 2 (frontend)
cd app/frontend && npm install && npm run dev      # http://localhost:5173
```

### Rebuilding the model artifacts
Run from `app/backend` (needs `data/*.csv`): `../../.venv/bin/python -m export.export_rf` and `-m export.export_quantum`, then `-m export.copy_results`. Both export scripts refuse to save unless the retrained models reproduce the paper:

- Random Forest probabilities match `results/novelty/classical_predictions.csv` to 1e-6, and its metrics match `results/final_results.csv`.
- QSVM labels on the 250-row matched subset are identical to the stored labels.
- The VQC is a seeded re-run (the paper's weights were never saved and its training was not seeded); its full-test-set F1 and ROC AUC must fall within two standard deviations of the paper's five-seed spread.

### Known accuracy notes
- The sample set is the paper's matched, class-enriched subset (38% fraud), so it is labelled as such in the UI.
- Best-F1 thresholds were tuned on the test labels, so the "tuned" results are optimistic; the app serves Random Forest at the default 0.5 threshold.
- VQC training is not seeded: its matched-subset numbers move between runs (paper first run F1 0.67 / 0.64 / 0.54, rerun 0.62 / 0.62 / 0.51 for none / SMOTE / ADASYN). QSVM is deterministic.

### Deploying (free tier)
- **Backend:** Render free web service from `render.yaml` (512 MB RAM, 0.1 CPU, spins down after about 15 minutes idle; the first request after sleep takes up to a minute). Set `ALLOWED_ORIGINS` to the frontend URL. Quantum row caps in `app/backend/fraudscope/config.py` were measured locally and must be re-measured on the host.
- **Frontend:** Vercel Hobby (personal, non-commercial) with root directory `app/frontend` and env `VITE_API_URL` set to the Render URL. `vercel.json` rewrites client-side routes to `index.html`.
- **Before a demo:** open the site a few minutes early; the landing page wakes the backend.
