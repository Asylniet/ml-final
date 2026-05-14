"""Train a Random Forest classifier to predict mature miRNA position within pre-miRNA.

Input:  src/data/mirbase_dataset.csv  (run download_mirbase.py first)
Output: src/models/mature_model.joblib
        src/models/mature_model_metrics.json

Approach: sliding-window binary classification.
  For every 22-nt window in each pre-miRNA hairpin, predict whether that window
  contains the mature miRNA sequence (label=1) or not (label=0).
  Features encode local composition + positional context.
"""

import json
import os
import pathlib
import sys

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import RandomizedSearchCV, cross_val_score, train_test_split

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))

from core.utils.mature_features import (
    MATURE_FEATURE_NAMES,
    WINDOW_SIZE,
    extract_window_features,
)

DATA_DIR = pathlib.Path(__file__).parent.parent / "src" / "data"
MODELS_DIR = pathlib.Path(__file__).parent.parent / "src" / "models"
DATASET_CSV = DATA_DIR / "mirbase_dataset.csv"
MODEL_PATH = MODELS_DIR / "mature_model.joblib"
METRICS_PATH = MODELS_DIR / "mature_model_metrics.json"

EXPERIMENT_NAME = "mature-mirna-predictor"
REGISTERED_MODEL_NAME = "mature-mirna-predictor"


def load_dataset() -> tuple[np.ndarray, np.ndarray]:
    rows = []
    lines = DATASET_CSV.read_text().splitlines()
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split(",")
        if len(parts) < 5:
            continue
        hairpin_id = parts[0]
        hairpin_seq = parts[1]
        mature_start = int(parts[2])
        mature_length = int(parts[3])
        rows.append((hairpin_seq, mature_start, mature_length))

    print(f"Loaded {len(rows)} hairpin–mature pairs")

    X_list, y_list = [], []
    unique_seqs: dict[str, int] = {}  # seq → mature_start for dedup

    for hairpin_seq, mature_start, mature_length in rows:
        # Skip if this hairpin already processed with same or similar mature start
        key = f"{hairpin_seq}:{mature_start}"
        if key in unique_seqs:
            continue
        unique_seqs[key] = mature_start

        max_start = len(hairpin_seq) - WINDOW_SIZE
        if max_start < 0:
            continue

        for w_start in range(max_start + 1):
            features = extract_window_features(hairpin_seq, w_start)
            # Label: 1 if this window overlaps the mature miRNA by at least half
            overlap_start = max(w_start, mature_start)
            overlap_end = min(w_start + WINDOW_SIZE, mature_start + mature_length)
            overlap = max(0, overlap_end - overlap_start)
            label = 1 if overlap >= WINDOW_SIZE // 2 else 0
            X_list.append(features)
            y_list.append(label)

    X = np.array(X_list)
    y = np.array(y_list)
    print(f"Total windows: {len(y)}  (positive={y.sum()}, negative={(y==0).sum()})")
    print(f"Positive rate: {y.mean():.3%}")
    return X, y


def train() -> None:
    if not DATASET_CSV.exists():
        raise FileNotFoundError(
            f"Dataset not found at {DATASET_CSV}. Run scripts/download_mirbase.py first."
        )

    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlruns/mlflow.db")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(EXPERIMENT_NAME)
    print(f"MLflow tracking URI: {tracking_uri}")

    print(f"Loading dataset from {DATASET_CSV} ...")
    X, y = load_dataset()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    candidates: list[tuple[str, RandomizedSearchCV]] = []

    # --- Random Forest ---
    rf_search = RandomizedSearchCV(
        estimator=RandomForestClassifier(
            n_estimators=400, class_weight="balanced", random_state=42
        ),
        param_distributions={
            "max_depth": [10, 15, 20, None],
            "min_samples_leaf": [1, 2, 4],
            "max_features": ["sqrt", "log2", 0.2, 0.3],
        },
        n_iter=20,
        cv=5,
        scoring="f1",
        random_state=42,
        n_jobs=-1,
    )

    # --- HistGradientBoosting ---
    hgbc_search = RandomizedSearchCV(
        estimator=HistGradientBoostingClassifier(
            random_state=42, class_weight="balanced"
        ),
        param_distributions={
            "max_depth": [3, 5, 8, None],
            "learning_rate": [0.05, 0.1, 0.2],
            "max_iter": [200, 300, 400],
            "min_samples_leaf": [10, 20, 40],
            "l2_regularization": [0.0, 0.1, 1.0],
        },
        n_iter=20,
        cv=5,
        scoring="f1",
        random_state=42,
        n_jobs=-1,
    )

    print("Training Random Forest ...")
    rf_search.fit(X_train, y_train)
    candidates.append(("Random Forest", rf_search))

    print("Training HistGradientBoostingClassifier ...")
    hgbc_search.fit(X_train, y_train)
    candidates.append(("HistGradientBoosting", hgbc_search))

    best_name, best_search = max(candidates, key=lambda t: t[1].best_score_)
    model = best_search.best_estimator_
    print(f"\nBest model: {best_name} (CV F1={best_search.best_score_:.4f})")

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, list(model.classes_).index(1)]

    cv_scores = cross_val_score(model, X, y, cv=5, scoring="f1", n_jobs=-1)
    cv_score = float(cv_scores.mean())

    acc = float(accuracy_score(y_test, y_pred))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    auc = float(roc_auc_score(y_test, y_proba))

    with mlflow.start_run(run_name=f"Mature {best_name} Tuned") as run:
        mlflow.log_param("train_size", len(X_train))
        mlflow.log_param("test_size", len(X_test))
        mlflow.log_param("feature_count", len(MATURE_FEATURE_NAMES))
        mlflow.log_params({
            "model_type": best_name,
            "window_size": WINDOW_SIZE,
            "class_weight": "balanced",
        })
        mlflow.log_params({f"best_{k}": v for k, v in best_search.best_params_.items()})
        mlflow.log_metrics({
            "accuracy": acc,
            "f1_score": f1,
            "precision": prec,
            "recall": rec,
            "roc_auc": auc,
            "cv_f1": cv_score,
        })
        mlflow.sklearn.log_model(model, artifact_path="model")

        print(f"CV F1: {cv_score:.4f}")
        print(classification_report(y_test, y_pred, target_names=["non-mature", "mature"]))
        print(f"ROC-AUC: {auc:.4f}")

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
        "roc_auc": auc,
        "cv_score": cv_score,
        "n_windows": int(len(y)),
        "n_positive": int(y.sum()),
        "n_negative": int((y == 0).sum()),
        "n_features": int(X.shape[1]),
        "window_size": WINDOW_SIZE,
        "model_type": f"{best_name} (window classifier)",
        "best_params": search.best_params_,
    }
    METRICS_PATH.write_text(json.dumps(metrics, indent=2))
    print(f"Saved metrics to {METRICS_PATH}")


if __name__ == "__main__":
    train()
