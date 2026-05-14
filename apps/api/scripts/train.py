import json
import os
import pathlib
import sys

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import (
    RandomizedSearchCV,
    cross_val_score,
    train_test_split,
)

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))

from core.utils.features import FEATURE_NAMES, extract_features

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))

DATA_DIR = pathlib.Path(__file__).parent.parent / "src" / "data"
MODELS_DIR = pathlib.Path(__file__).parent.parent / "src" / "models"
DATASET_CSV = DATA_DIR / "dataset.csv"
MODEL_PATH = MODELS_DIR / "model.joblib"
METRICS_PATH = MODELS_DIR / "model_metrics.json"

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
    base_model = RandomForestClassifier(n_estimators=400, random_state=42)
    param_distributions = {
        "max_depth": [5, 10, 15, None],
        "min_samples_leaf": [1, 2, 4],
        "max_features": ["sqrt", "log2", 0.3],
    }

    search = RandomizedSearchCV(
        estimator=base_model,
        param_distributions=param_distributions,
        n_iter=20,
        cv=5,
        scoring="f1_macro",
        random_state=42,
        n_jobs=-1,
    )

    with mlflow.start_run(run_name="Random Forest Tuned") as run:
        mlflow.log_param("train_size", len(X_train))
        mlflow.log_param("test_size", len(X_test))
        mlflow.log_param("feature_count", len(FEATURE_NAMES))
        mlflow.log_params(
            {
                "model_type": "Random Forest",
                "n_estimators": 400,
                "search_n_iter": 20,
                "search_cv": 5,
            }
        )

        print("Running RandomizedSearchCV for Random Forest ...")
        search.fit(X_train, y_train)
        model = search.best_estimator_
        y_pred = model.predict(X_test)

        cv_scores = cross_val_score(model, X, y, cv=5, scoring="f1_macro", n_jobs=-1)
        cv_score = float(cv_scores.mean())

        acc = float(accuracy_score(y_test, y_pred))
        f1 = float(f1_score(y_test, y_pred, average="macro"))
        prec = float(precision_score(y_test, y_pred, average="macro", zero_division=0))
        rec = float(recall_score(y_test, y_pred, average="macro", zero_division=0))

        mlflow.log_params({f"best_{key}": value for key, value in search.best_params_.items()})
        mlflow.log_metrics(
            {
                "accuracy": acc,
                "f1_score": f1,
                "precision": prec,
                "recall": rec,
                "cv_f1_macro": cv_score,
            }
        )
        mlflow.sklearn.log_model(model, artifact_path="model")

        print("\n--- Random Forest Tuned ---")
        print(f"Best params: {search.best_params_}")
        print(f"Cross-val macro F1: {cv_score:.4f}")
        print(classification_report(y_test, y_pred, target_names=["non-miRNA", "pre-miRNA"]))

        model_uri = f"runs:/{run.info.run_id}/model"
        mv = mlflow.register_model(model_uri, REGISTERED_MODEL_NAME)
        print(f"Registered as '{REGISTERED_MODEL_NAME}' version {mv.version}")

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"Saved model to {MODEL_PATH}")

    metrics = {
        "accuracy": acc,
        "f1": f1,
        "precision": prec,
        "recall": rec,
        "cv_score": cv_score,
        "n_samples": int(len(y)),
        "n_positive": int(y.sum()),
        "n_negative": int((y == 0).sum()),
        "n_features": int(X.shape[1]),
        "model_type": "Random Forest",
    }
    METRICS_PATH.write_text(json.dumps(metrics, indent=2))
    print(f"Saved metrics to {METRICS_PATH}")


if __name__ == "__main__":
    train()
