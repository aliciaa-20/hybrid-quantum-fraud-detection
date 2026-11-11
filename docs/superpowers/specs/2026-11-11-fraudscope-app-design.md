# FraudScope: web app for the Hybrid Quantum Fraud Detection project

Status: draft for approval, 2026-11-11

## Intent and why

The honors project so far is a paper plus research scripts. This turns it into a working, publicly reachable web app that examiners can open at a URL and use. It is a demo of the research, not a claim that quantum beats classical. The paper's own finding is the opposite: Random Forest wins on cost-benefit (RF+None at its best-F1 threshold nets about +$8.7k; VQC+ADASYN at the default threshold nets about -$272k; every VQC row in `results/novelty/cost_benefit.csv` is negative), and the app must tell that story honestly.

Primary reader: honors examiners, opening the site cold. Secondary: anyone with a CSV of transactions in the same format.

## Goals

1. A public URL, free to host, that works without setup.
2. Results the user can trust. The one thing that must not happen is the site showing inaccurate results (see "Accuracy requirements").
3. Let a visitor score real transactions with Random Forest, QSVM and VQC and compare them side by side.
4. Present the paper's findings, including the cost-benefit comparison, from the actual results files.

## Non-goals

- Accounts, login, stored uploads, or any live/bank data. Uploads are scored and discarded.
- A manual entry form. The 4 features (`V10, V12, V14, V17`) are anonymized PCA components with no meaning to a human.
- Claiming quantum advantage anywhere in copy or UI.
- Real-time scale. Quantum scoring is deliberately limited (see "Quantum models").

## Anti-goals (a failure even if it technically works)

- Any number on the site that disagrees with the paper or the results files without an explanation.
- A prominent "99.9% accuracy" figure. On 0.17% fraud, accuracy is meaningless; lead with precision, recall, F1, ROC-AUC.
- Faked or hand-typed quantum outputs.
- A site that stalls or times out in front of an examiner.

## What the user decided

- Product shape: analyst-style scoring (browse flagged transactions) plus a scoring API, as a real working product, public URL.
- Real users are supported only through CSV upload with the same 4 columns.
- Stack: React frontend, FastAPI backend.
- Layout: story-first landing page (research question, then three entry points: try a sample transaction, upload a CSV, read the findings).
- Visual style: clean, editorial (white space, strong typography, serious and academic, projector and print safe).
- Quantum handling: hybrid. Sample browser shows precomputed quantum scores instantly, plus a "Run live" button that recomputes on the simulator and falls back to the stored score with a visible note if it is slow. Uploads: RF scores everything; QSVM/VQC run live on small uploads only; larger uploads get RF only with a note explaining why.
- Free hosting. The user will create the accounts.
- Biggest concern: inaccurate results.

## Accuracy requirements

These are requirements, not nice-to-haves.

1. **Reproduction gate.** No model is exported for the app until the retrained model reproduces the paper's numbers on the same test set within a stated tolerance, checked against `results/final_results.csv` and the prediction CSVs in `results/` and `results/novelty/`. A mismatch is investigated and reported to the user, never papered over. Hyperparameters, seeds, feature selection and preprocessing must match the research scripts in `src/` exactly.
2. **Provenance.** Every stored score (especially quantum) records model, balancing config, seed and generation date, and comes from the real model run, not from hand entry.
3. **Results page reads files.** All metrics, cost-benefit figures and charts are generated from the CSVs in `results/`, not typed into the frontend.
4. **Honest metrics.** Show precision, recall, F1, ROC-AUC and the confusion counts. Accuracy may appear but never leads.
5. **Show misses.** The sample browser shows the true label next to each prediction, including false negatives and false positives. The site must not curate only the wins.
6. **Label evaluation scope.** QSVM's headline F1 (~0.843) comes from a matched, class-enriched evaluation subset, not the full test set. It must always carry that label and never sit unlabelled next to full-test-set numbers.
7. **Threshold disclosure.** Best-F1 thresholds in `results/novelty/threshold_optimization.csv` were selected on the evaluated data (builder to confirm how). If so, the Results page says the tuned numbers are optimistic.
8. **Live matches stored.** Seeded simulator; a live quantum recompute must match the stored score within tolerance, or the mismatch is surfaced, not hidden.

## Parts

- **Backend (FastAPI):** loads saved models once at startup. Endpoints roughly: list/get sample transactions with all models' scores; score an uploaded CSV (validates the 4 columns, row-count caps per model); serve results/cost-benefit data. Random Forest is the default model.
- **Frontend (React):** landing page, Explore (sample browser with model comparison and explanation), Upload, Findings (results from files), About/method.
- **Model export step:** one script that retrains RF (and any other needed model), exports it, precomputes QSVM/VQC scores for the sample set, and runs the reproduction gate. Existing predictions in `results/quantum_predictions.csv` and `results/novelty/qsvm_vs_vqc_predictions.csv` should be reused where they cover the sample rows (builder to verify row alignment).
- **Sample set:** a small committed file built from `data/test_selected.csv` (gitignored, 4.4 MB): all known frauds in the test set (95) plus a sample of legitimate transactions. The full CSVs under `data/` stay out of the repo.

## Quantum models

QSVM is a pairwise kernel method, so cost grows with train-set support points times rows scored. VQC inference is per-row. Both run on a simulator (no hardware; Phase 10 is abandoned). Row caps for live uploads are set after measuring actual latency on the chosen host, not guessed. UI labels both "experimental".

## Explanations (my guess, not confirmed)

Each prediction shows a short explanation, for example which of the 4 features pushed the score up. The user has not confirmed this; the builder may propose a simple method and flag it. It must not be misleading: for the quantum models there is no natural per-feature attribution, so explanations apply to RF only unless a sound method is chosen.

## Constraints

- Free hosting: planned Vercel (or Netlify) for the frontend and Render or Hugging Face Spaces for the backend, all my suggestion and not yet confirmed. Free tiers sleep when idle (cold start 30-60 s) and have tight memory; Qiskit plus scikit-learn is heavy. Check current limits before committing.
- The saved RF model might be large (trained on ~18 MB of rows). If it exceeds host or repo limits, options are model-size reduction (only with the user's approval, since it changes results), release assets, or download at build. Do not silently change hyperparameters.
- No secrets in code; `.env` in `.gitignore`. New dependencies need the user's approval first.
- Project conventions from the user's setup: plan in `STAGES.md`, one commit per completed stage, work on a branch not `main`, ask before pushing, README kept current, no new tests unless asked, a stage is done only when it builds/runs and existing tests pass.

## Left to the builder

Folder layout (my call: leave `src/` research code untouched and add `app/backend` and `app/frontend`), frontend tooling (my call: Vite), exact API shape, row caps, tolerance values for the reproduction gate, how to warm the backend before a demo, and the explanation method.

## My calls (not agreed with the user)

- `app/` layout and Vite.
- Render/Hugging Face and Vercel as hosts.
- Explanations as RF-only feature attribution.
- Reusing existing prediction CSVs for precomputed quantum scores.
