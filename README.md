# Nice Try

### Can quantum machine learning catch credit card fraud better than classical methods?

An honors project that tests it properly, plus a working web app where you can watch the models vote on real transactions. Spoiler: classical wins.

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![Qiskit](https://img.shields.io/badge/Qiskit-6929C4?logo=qiskit&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?logo=scikitlearn&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?logo=react&logoColor=61DAFB)

## What it does

The research compares a classical Random Forest, an SVM and Logistic Regression against two quantum models (a variational classifier, **VQC**, and a quantum kernel classifier, **QSVM**) on a heavily imbalanced fraud dataset, using the same 4 features and the same test set. It then stress-tests the result: threshold tuning, five random seeds, qubit scaling, noise, significance tests and a cost analysis.

The web app turns that into something you can poke at. Pick a real test-set transaction and see all three models score it, upload your own small CSV, or read the findings as an interactive story.

It does not claim quantum advantage. In this project's own results the Random Forest wins.

## Results

Full imbalanced test set (56,746 transactions, 95 of them fraud):

| Model | Training | Precision | Recall | F1 | ROC AUC |
|---|---|---:|---:|---:|---:|
| Random Forest | none | 0.883 | 0.716 | **0.791** | 0.945 |
| SVM | none | 0.771 | 0.779 | 0.775 | 0.890 |
| Logistic Regression | none | 0.847 | 0.526 | 0.649 | 0.926 |
| VQC (quantum) | SMOTE | 0.012 | 0.579 | 0.023 | 0.817 |

- **Cost:** counting fraud value caught minus the cost of investigating alerts, the best Random Forest nets +$8,669. Every VQC setting loses money (best: -$983).
- **QSVM beats VQC** on a small matched subset (F1 0.843 vs 0.62), and the difference is significant (McNemar p < 1e-4). That subset is 38% fraud, so it is not comparable to the table above.
- **More qubits did worse:** F1 0.082 with 2 qubits, 0.013 with 4, 0.004 with 8.

Accuracy is deliberately left out: with 0.17% fraud, flagging nothing scores about 99.8%. The paper has every table and the statistics: `paper/Hybrid_Quantum_Fraud_Detection_Paper.docx`.

## The app

- **Explore:** step through 250 real transactions and see Random Forest, QSVM and VQC side by side, including their misses and false alarms.
- **Upload:** drop in a CSV, or try a built-in sample set. A pre-flight check shows which models will run, and the results show where the models disagree.
- **Findings:** switch models, training setups and cut-offs, and the bars and the explanation change with them.

Random Forest scores everything. The quantum models run on a simulator, so they are limited to small uploads (25 rows for QSVM, 200 for VQC).

## How it works

```
Credit card data -> remove duplicates -> 80/20 train/test split
  -> scale + pick 4 features by mutual information (training data only)
  -> optional balancing: none / SMOTE / ADASYN (training data only)
  -> Random Forest, SVM, Logistic Regression  |  VQC, QSVM (4 qubits)
  -> precision, recall, F1, ROC AUC, cost-benefit
```

The app never ships a model it cannot reproduce. Before a model is exported, a check retrains it and refuses to save unless it matches the paper's numbers.

## Limitations

The quantum models only ran on a simulator; a real-hardware run was attempted and abandoned. QSVM could only be evaluated on a small subset because kernel methods do not scale to the full test set. The "tuned threshold" results picked their cut-off using the test labels, so treat them as an upper bound. VQC training was not seeded in the original runs, so its numbers move between runs (the paper reports the first run; `results/novelty/` holds a rerun). The four features are anonymized components, so individual values have no human meaning.

## Tech stack

| Part | Tools |
|---|---|
| Research | Python, scikit-learn, imbalanced-learn, Qiskit, Qiskit Machine Learning |
| Backend | FastAPI, Uvicorn |
| Frontend | React, TypeScript, Vite, Motion |
| Hosting (planned) | Render (API), Vercel (UI) |

## Getting started

```bash
git clone https://github.com/aliciaa-20/hybrid-quantum-fraud-detection
cd hybrid-quantum-fraud-detection
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt fastapi uvicorn python-multipart

# terminal 1: API
cd app/backend && ../../.venv/bin/uvicorn fraudscope.main:app --port 8000

# terminal 2: UI  ->  http://localhost:5173
cd app/frontend && npm install && npm run dev
```

To reproduce the research, download [`creditcard.csv`](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud) into `data/` and run the scripts in `src/` in the order listed in [`docs/RESEARCH.md`](docs/RESEARCH.md). Rebuilding the app's model files is described in `app/backend/export/`.

## Project structure

```
app/        web app: backend (FastAPI), frontend (React)
src/        research code, with src/novelty/ for the extension experiments
results/    metrics, predictions and figures (results/novelty/ for the extensions)
paper/      the paper and the script that builds it
scripts/    exploration and demo scripts
docs/       research notes and the app's design spec and plan
PHASES.md   research log      STAGES.md   web app build log
```

## Data source

[Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud) from the Machine Learning Group at ULB (Université Libre de Bruxelles). After removing 1,081 duplicate rows it has 283,726 transactions, 473 of them fraud (0.17%).

## Disclaimer

An academic project, not a fraud detection system. The results are experimental and should not be used on real financial data without proper validation.

Built by **Alicia Pereira**, B.Tech CSE (AI and ML).
