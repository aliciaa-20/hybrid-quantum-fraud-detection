import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC


# =========================================================
# LOAD DATA
# =========================================================

train_df = pd.read_csv("data/train_selected.csv")
test_df = pd.read_csv("data/test_selected.csv")

features = ["V10", "V12", "V14", "V17"]

X_train = train_df[features]
y_train = train_df["Class"]

X_test = test_df[features]
y_test = test_df["Class"]


# =========================================================
# FUNCTION TO CREATE CONFUSION MATRIX
# =========================================================

def create_confusion_matrix(
    model,
    X_train,
    y_train,
    X_test,
    y_test,
    name
):

    print(f"\nGenerating confusion matrix: {name}")

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    cm = confusion_matrix(
        y_test,
        y_pred
    )

    print(cm)

    display = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=["Legitimate", "Fraud"]
    )

    display.plot()

    plt.title(
        f"Confusion Matrix: {name}"
    )

    plt.tight_layout()

    filename = (
        "results/"
        + name.lower()
        .replace(" ", "_")
        .replace("+", "plus")
        + "_confusion_matrix.png"
    )

    plt.savefig(
        filename,
        dpi=300
    )

    plt.close()

    print(f"Saved: {filename}")


# =========================================================
# RANDOM FOREST + NONE
# =========================================================

random_forest = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

create_confusion_matrix(
    random_forest,
    X_train,
    y_train,
    X_test,
    y_test,
    "Random Forest + None"
)


# =========================================================
# SVM + NONE
# =========================================================

svm = SVC(
    kernel="rbf",
    probability=True,
    random_state=42
)

# Use the same manageable subset strategy
train_none = train_df.copy()

legitimate = train_none[
    train_none["Class"] == 0
].sample(
    n=20000,
    random_state=42
)

fraud = train_none[
    train_none["Class"] == 1
]

svm_train = pd.concat(
    [legitimate, fraud]
).sample(
    frac=1,
    random_state=42
)

create_confusion_matrix(
    svm,
    svm_train[features],
    svm_train["Class"],
    X_test,
    y_test,
    "SVM + None"
)


print("\n" + "=" * 70)
print("CONFUSION MATRIX GENERATION COMPLETED")
print("=" * 70)