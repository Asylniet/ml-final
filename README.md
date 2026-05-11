# Human pre-miRNA Classifier

Predicts whether a given RNA nucleotide sequence is a genuine human pre-microRNA, using sequence composition features and a Random Forest classifier.

## Background

MicroRNAs (miRNAs) are small non-coding RNA molecules (~22 nt) derived from precursor hairpin structures called **pre-miRNAs** (~60–120 nt). Their secondary structure — how the sequence folds into stems and loops — determines their biological function. Experimental structure determination is slow and expensive, so computational prediction from the primary sequence is valuable.

This model learns to distinguish real human pre-miRNAs from random RNA sequences with identical nucleotide composition, using 23 hand-crafted sequence features (nucleotide frequencies, GC content, dinucleotide frequencies).

## Project Structure

```
apps/
  api/                        # FastAPI Python app (uv)
    scripts/
      download_data.py        # fetch human miRNA sequences from NCBI
      train.py                # feature extraction + model comparison + MLflow logging
    src/
      api/web/predict/        # FastAPI endpoints
      core/utils/
        features.py           # feature extraction logic
        exc.py                # custom exceptions
      models/                 # saved model artifact (model.joblib)
      data/                   # downloaded sequences and dataset CSV
    mlruns/                   # MLflow tracking database (gitignored)
  frontend/                   # React + TypeScript (Vite + pnpm)
    src/
      api.ts                  # API client
      types.ts                # shared TypeScript types
      App.tsx                 # root component
      components/
        SequenceInput.tsx     # sequence textarea + examples
        PredictionResult.tsx  # prediction display
turbo.json                    # Turborepo task graph
docker-compose.yml            # api + mlflow + frontend services
Makefile                      # cross-language task orchestration
```

## Setup

Requires: `uv`, `pnpm`, `docker`

```bash
# Step 1 - install all dependencies
make install

# Step 2 — train all models, log to MLflow, save the best
make train

# Step 3a — run everything with Docker
make run

# Step 3b — or run services individually for development
cd apps/api/src && uv run uvicorn api.web.app:app --reload   # API on :8000
pnpm dev                                                      # frontend on :5173
uv run mlflow ui --backend-store-uri sqlite:///mlruns/mlflow.db --port 5001
```

## Services

| Service | Local | Docker |
|---------|-------|--------|
| API | `http://localhost:8000` | `http://localhost:8000` |
| Frontend | `http://localhost:5173` | `http://localhost:3000` |
| MLflow UI | `http://localhost:5001` | `http://localhost:5001` |

## API

### `GET /`
```json
{"message": "ML API is running"}
```

### `POST /predict`

**Request:**
```json
{"sequence": "UGAGGUAGUAGGUUGUAUAGUUUAGGGUCACACCCACCACUGGGAGAUAACUAUACAAUCUACUGUCUUUCCUA"}
```

Both `T` and `U` are accepted. Only `A`, `U`, `G`, `C` (and `T`) are valid. Minimum length: 10 nt.

**Response:**
```json
{
  "prediction": "pre-miRNA",
  "is_mirna": true,
  "confidence": 0.83,
  "gc_content": 0.42,
  "length": 74,
  "sequence": "UGAGGUAGUAGGUUGUAUAGU..."
}
```

## MLflow

Every `make train` run logs three experiments to MLflow and registers the best model in the Model Registry.

```bash
# Train locally and view results
make train
uv run mlflow ui --backend-store-uri sqlite:///apps/api/mlruns/mlflow.db --port 5001

# Train against the running Docker MLflow server
MLFLOW_TRACKING_URI=http://localhost:5001 make train
```

Open `http://localhost:5001` to:
- **Experiments** — compare all three runs side by side (params, metrics, artifacts)
- **Models** — view registered versions of `human-pre-mirna-classifier`, promote versions through `Staging → Production`

Each run logs:
- **Parameters** — `model_type`, `n_estimators`, train/test split sizes
- **Metrics** — accuracy, F1-score, precision, recall
- **Artifacts** — serialized model file + environment spec

## Model Performance

Trained on 4571 samples (1815 real human pre-miRNAs from NCBI + 2756 negatives):

| Model | Accuracy | F1-score |
|-------|----------|----------|
| Logistic Regression | 86% | 0.85 |
| **Random Forest** (best) | **90%** | **0.89** |
| Gradient Boosting | 90% | 0.89 |

Negatives include dinucleotide-shuffled sequences (same composition, broken structure), poly-nucleotide sequences, low-complexity repeats, and uniformly random sequences — making the classifier robust to out-of-distribution inputs.


### Quick validation commands

```bash
# Known positive — hsa-let-7a-1
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"sequence": "UGAGGUAGUAGGUUGUAUAGUUUAGGGUCACACCCACCACUGGGAGAUAACUAUACAAUCUACUGUCUUUCCUA"}'
# expected: is_mirna=true

# Known positive — hsa-mir-21
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"sequence": "UGUCGGGUAGCUUAUCAGACUGAUGUUGACUGUUGAAUCUCAUGGCAACACCAGUCGAUGGGCUGU"}'
# expected: is_mirna=true

# Negative control — poly-A
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"sequence": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"}'
# expected: is_mirna=false, confidence ~0.97
```
