# Human pre-miRNA Classifier

Interactive ML project for classifying human pre-miRNA sequences from RNA primary sequence features, with model explainability, dataset stats, and predicted RNA secondary-structure visualization.

## Overview

This project predicts whether an RNA sequence is a real human pre-miRNA or a non-miRNA sequence.

The current version includes:

- a tuned `RandomForestClassifier`
- `90` engineered sequence features
- model metrics exported to JSON
- feature-importance visualizations
- per-sequence feature breakdown
- predicted RNA secondary structure rendered as SVG with `ViennaRNA`

The app is split into:

- `apps/api`: FastAPI backend, feature extraction, model training, inference
- `apps/frontend`: React + TypeScript frontend for prediction and visualization

## Why pre-miRNA matters

MicroRNAs are short non-coding RNAs involved in gene regulation. They are produced from precursor molecules called `pre-miRNAs`, which usually form a stable hairpin secondary structure. Because experimental validation is expensive, computational screening helps identify likely candidates from sequence data.

This project combines composition-based ML features with RNA folding visualization to make predictions more interpretable and more convincing in a course-demo setting.

## Current model

Training uses a tuned Random Forest with `RandomizedSearchCV`.

Latest saved metrics from [model_metrics.json](C:/Users/user/Desktop/ML-final/ml-sis-3/apps/api/src/models/model_metrics.json):

- Accuracy: `0.9115`
- F1: `0.9063`
- Precision: `0.9132`
- Recall: `0.9012`
- Cross-validation F1: `0.8851`
- Samples: `4571`
- Positives: `1815`
- Negatives: `2756`
- Features: `90`

## Feature set

The model uses `90` hand-crafted RNA sequence features from [features.py](C:/Users/user/Desktop/ML-final/ml-sis-3/apps/api/src/core/utils/features.py):

- Sequence length
- GC content
- AU content
- 4 nucleotide frequencies
- 16 dinucleotide frequencies
- 64 trinucleotide frequencies
- Shannon entropy
- Purine/pyrimidine ratio
- GU wobble frequency

## Secondary structure visualization

For every prediction, the backend now also:

- folds the RNA sequence into its minimum-free-energy structure
- returns dot-bracket notation
- returns `MFE` in kcal/mol
- renders the predicted secondary structure as SVG

This is done with `ViennaRNA`, so the UI can show a hairpin-like structure directly in the prediction result.

## Project structure

```text
apps/
  api/
    scripts/
      train.py
    src/
      api/web/
        app.py
        predict/
          routers.py
          schemas.py
      core/utils/
        features.py
        structure.py
      data/
        dataset.csv
      models/
        model.joblib
        model_metrics.json
  frontend/
    src/
      api.ts
      types.ts
      App.tsx
      components/
        SequenceInput.tsx
        PredictionResult.tsx
        StatsPanel.tsx
        FeatureImportanceChart.tsx
        FeatureBreakdown.tsx
        NucleotideSequence.tsx
        SecondaryStructureCard.tsx
Makefile
docker-compose.yml
package.json
pnpm-workspace.yaml
turbo.json
```

## Requirements

- Python tooling: `uv`
- Node.js
- `pnpm` through `corepack` or a direct `pnpm` install
- optional: Docker

## Installation

### Backend

```powershell
cd apps\api
uv sync
```

### Frontend

If `pnpm` is not installed globally, use `corepack`:

```powershell
cd C:\Users\user\Desktop\ML-final\ml-sis-3
$env:COREPACK_HOME='C:\Users\user\Desktop\ML-final\ml-sis-3\.corepack'
cmd /c corepack pnpm install
```

## Training

Run training from the API app directory:

```powershell
cd apps\api
uv run python scripts\train.py
```

Training will:

- extract all `90` features
- run `RandomizedSearchCV` on Random Forest
- compute test metrics
- compute `5-fold` cross-validation F1
- save [model.joblib](C:/Users/user/Desktop/ML-final/ml-sis-3/apps/api/src/models/model.joblib)
- save [model_metrics.json](C:/Users/user/Desktop/ML-final/ml-sis-3/apps/api/src/models/model_metrics.json)
- log the run to MLflow

## Running the backend

```powershell
cd apps\api
uv run python src\main.py
```

Backend URL:

- `http://127.0.0.1:8000`

## Running the frontend

```powershell
cd C:\Users\user\Desktop\ML-final\ml-sis-3
$env:COREPACK_HOME='C:\Users\user\Desktop\ML-final\ml-sis-3\.corepack'
cmd /c corepack pnpm --filter @ml-sis3/frontend dev
```

Frontend URL:

- `http://localhost:5173`

## API endpoints

### `GET /`

Health check:

```json
{
  "message": "ML API is running"
}
```

### `GET /stats`

Returns saved model statistics:

```json
{
  "accuracy": 0.9115,
  "f1": 0.9063,
  "precision": 0.9132,
  "recall": 0.9012,
  "cv_score": 0.8851,
  "n_samples": 4571,
  "n_positive": 1815,
  "n_negative": 2756,
  "n_features": 90,
  "model_type": "Random Forest"
}
```

### `GET /features`

Returns sorted feature importances:

```json
[
  { "name": "UGU_freq", "importance": 0.0412 },
  { "name": "length", "importance": 0.0384 }
]
```

### `POST /predict`

Request:

```json
{
  "sequence": "UGAGGUAGUAGGUUGUAUAGUUUAGGGUCACACCCACCACUGGGAGAUAACUAUACAAUCUACUGUCUUUCCUA"
}
```

Rules:

- `T` is automatically converted to `U`
- allowed symbols: `A`, `U`, `G`, `C`, `T`
- minimum length: `10`

Response:

```json
{
  "prediction": "pre-miRNA",
  "is_mirna": true,
  "confidence": 0.9475,
  "gc_content": 0.4324,
  "length": 95,
  "sequence": "UGAGGUAGUAGGUUGUAUAGUUUAGGGUCACACCCACCACUGGGAGAUAACUAUACAAUCUACUGUCUUUCCUA",
  "feature_values": {
    "length": 95.0,
    "gc_content": 0.4324
  },
  "secondary_structure": {
    "dot_bracket": "....((((....))))....",
    "mfe": -29.5,
    "svg": "<svg ...>...</svg>"
  }
}
```

## Frontend features

The frontend now displays:

- model performance cards
- dataset composition bar
- top feature importances chart
- prediction confidence and sequence summary
- color-coded nucleotide sequence
- per-sequence feature breakdown
- predicted RNA secondary structure image
- dot-bracket notation and `MFE`

## Demo sequences

### Positive example 1

```text
UGAGGUAGUAGGUUGUAUAGUUUAGGGUCACACCCACCACUGGGAGAUAACUAUACAAUCUACUGUCUUUCCUA
```

### Positive example 2

```text
UGUCGGGUAGCUUAUCAGACUGAUGUUGACUGUUGAAUCUCAUGGCAACACCAGUCGAUGGGCUGU
```

### Negative control

```text
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
```

## Quick API checks

### PowerShell

```powershell
Invoke-RestMethod http://127.0.0.1:8000/
Invoke-RestMethod http://127.0.0.1:8000/stats
Invoke-RestMethod http://127.0.0.1:8000/features
```

```powershell
Invoke-RestMethod `
  -Uri http://127.0.0.1:8000/predict `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"sequence":"UGAGGUAGUAGGUUGUAUAGUUUAGGGUCACACCCACCACUGGGAGAUAACUAUACAAUCUACUGUCUUUCCUA"}'
```

## Build checks

### Frontend production build

```powershell
$env:COREPACK_HOME='C:\Users\user\Desktop\ML-final\ml-sis-3\.corepack'
cmd /c corepack pnpm --filter @ml-sis3/frontend build
```

### Backend training check

```powershell
cd apps\api
uv run python scripts\train.py
```

## MLflow

The training script logs runs to MLflow and registers the trained model.

Open MLflow locally with:

```powershell
cd apps\api
uv run mlflow ui --backend-store-uri sqlite:///mlruns/mlflow.db --port 5001
```

MLflow URL:

- `http://localhost:5001`

## Notes

- The model is composition-feature-based, not an end-to-end deep learning model.
- The secondary-structure image is generated at inference time and is meant for interpretation and presentation.
- The frontend currently embeds SVG returned by the backend for RNA structure display.
