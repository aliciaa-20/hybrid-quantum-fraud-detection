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
False Negatives = 28
True Positives  = 67
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
├── data/
|   └── .gitkeep
|
├── results/
|   ├── classical_results.csv
|   ├── quantum_results.csv
|   ├── quantum_predictions.csv
|   ├── final_results.csv
|   ├── model_comparison.png
|   ├── precision_comparison.png
|   ├── recall_comparison.png
|   ├── roc_auc_comparison.png
|   ├── training_time_comparison.png
|   ├── random_forest_plus_none_confusion_matrix.png
|   ├── svm_plus_none_confusion_matrix.png
|   ├── vqc_none_confusion_matrix.png
|   ├── vqc_smote_confusion_matrix.png
|   └── vqc_adasyn_confusion_matrix.png
|
├── src/
|   ├── balancing.py
|   ├── classical_models.py
|   ├── confusion_matrices.py
|   ├── final_results.py
|   ├── preprocessing.py
|   ├── quantum_data.py
|   ├── quantum_final.py
|   └── quantum_model.py
|
├── eda.py
├── test_dataset.py
├── requirements.txt
├── .gitignore
└── README.md
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
