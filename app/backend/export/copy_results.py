"""Copy the four results CSVs the Findings page needs into artifacts/results/ (shipped with the backend).

Run from app/backend:  ../../.venv/bin/python -m export.copy_results
"""

import shutil

from fraudscope import config

FILES = [
    "final_results.csv",
    "novelty/cost_benefit.csv",
    "novelty/qsvm_vs_vqc.csv",
    "novelty/threshold_optimization.csv",
    "novelty/threshold_validation.csv",
]


def main() -> None:
    for rel in FILES:
        dst = config.RESULTS_DIR / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(config.SOURCE_RESULTS_DIR / rel, dst)
        print("copied", rel)


if __name__ == "__main__":
    main()
