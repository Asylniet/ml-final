import os
import pathlib
import sys

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))
from core.utils.features import extract_features

DATA_DIR = pathlib.Path(__file__).parent.parent / "src" / "data"
MODELS_DIR = pathlib.Path(__file__).parent.parent / "src" / "models"
DATASET_CSV = DATA_DIR / "dataset.csv"
MODEL_PATH = MODELS_DIR / "model.joblib"

EXPERIMENT_NAME = "human-pre-mirna-classifier"
REGISTERED_MODEL_NAME = "human-pre-mirna-classifier"


def load_dataset() -> tuple[np.ndarray, np.ndarray]:
    sequences, labels = [], []
    lines = DATASET_CSV.read_text().splitlines()
    for line in lines[1:]:
        if not line.strip():
            continue
        seq, label = line.rsplit(",", 1)
        sequences.append(seq.strip())
        labels.append(int(label.strip()))
    X = np.array([extract_features(s) for s in sequences])
    y = np.array(labels)
    return X, y


def train() -> None:
    if not DATASET_CSV.exists():
        raise FileNotFoundError(
            f"Dataset not found at {DATASET_CSV}. Run scripts/download_data.py first."
        )

    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlruns/mlflow.db")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(EXPERIMENT_NAME)
    print(f"MLflow tracking URI: {tracking_uri}")

    print(f"Loading dataset from {DATASET_CSV} ...")
    X, y = load_dataset()
    print(f"Samples: {len(y)}  (positive={y.sum()}, negative={(y == 0).sum()})")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    models: list[tuple[str, object, dict]] = [
        (
            "Logistic Regression",
            Pipeline([("scaler", StandardScaler()), ("clf", LogisticRegression(max_iter=1000))]),
            {"max_iter": 1000, "model_type": "Logistic Regression"},
        ),
        (
            "Random Forest",
            RandomForestClassifier(n_estimators=200, random_state=42),
            {"n_estimators": 200, "random_state": 42, "model_type": "Random Forest"},
        ),
        (
            "Gradient Boosting",
            GradientBoostingClassifier(n_estimators=200, random_state=42),
            {"n_estimators": 200, "random_state": 42, "model_type": "Gradient Boosting"},
        ),
    ]

    best_run_id: str | None = None
    best_name, best_model, best_acc = "", None, 0.0

    for run_name, model, params in models:
        with mlflow.start_run(run_name=run_name) as run:
            mlflow.log_params(params)
            mlflow.log_param("train_size", len(X_train))
            mlflow.log_param("test_size", len(X_test))

            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            acc = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred, average="macro")
            prec = precision_score(y_test, y_pred, average="macro")
            rec = recall_score(y_test, y_pred, average="macro")

            mlflow.log_metrics({"accuracy": acc, "f1_score": f1, "precision": prec, "recall": rec})
            mlflow.sklearn.log_model(model, artifact_path="model")

            print(f"\n--- {run_name} ---")
            print(classification_report(y_test, y_pred, target_names=["non-miRNA", "pre-miRNA"]))

            if acc > best_acc:
                best_acc, best_name, best_model = acc, run_name, model
                best_run_id = run.info.run_id

    print(f"\nBest model: {best_name}  (accuracy={best_acc:.4f})")

    model_uri = f"runs:/{best_run_id}/model"
    mv = mlflow.register_model(model_uri, REGISTERED_MODEL_NAME)
    print(f"Registered as '{REGISTERED_MODEL_NAME}' version {mv.version}")

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, MODEL_PATH)
    print(f"Saved to {MODEL_PATH}")


if __name__ == "__main__":
    train()
