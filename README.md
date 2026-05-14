# Human pre-miRNA Classifier & Mature miRNA Predictor

Interactive ML web application for human microRNA sequence analysis. Given an RNA sequence, the system classifies it as a pre-miRNA or non-miRNA, visualizes its secondary structure, and predicts the active mature miRNA region within it.

## Models

### 1. Pre-miRNA Classifier

Binary classification: is this sequence a genuine human pre-miRNA?

| Metric | Value |
|--------|-------|
| Accuracy | **95.96%** |
| F1 (macro) | 95.76% |
| Precision | 95.97% |
| Recall | 95.56% |
| CV F1 (5-fold) | 96.00% |
| Samples | 4,571 (1,815 pos / 2,756 neg) |
| Features | 94 |
| Model | HistGradientBoostingClassifier |

### 2. Mature miRNA Position Predictor

Sliding-window binary classifier: given a pre-miRNA, locate the 22-nt window most likely to be the active mature miRNA.

| Metric | Value |
|--------|-------|
| Accuracy | 63.2% |
| F1 | 60.4% |
| ROC-AUC | **74.4%** |
| Recall | 86.0% |
| CV F1 (5-fold) | 59.7% |
| Windows | 172,701 (56,507 pos / 116,194 neg) |
| Features | 30 per window |
| Model | Random Forest |

The mature predictor is a harder problem: it learns positional and structural signals from NCBI GenBank annotations. High recall (86%) prioritizes finding the mature region over precision.

## Feature engineering

### Pre-miRNA classifier — 94 features

| Category | Count |
|----------|-------|
| Length, GC content, AU content | 3 |
| Nucleotide frequencies (A/U/G/C) | 4 |
| Dinucleotide frequencies | 16 |
| Trinucleotide frequencies | 64 |
| Shannon entropy | 1 |
| Purine/pyrimidine ratio, GU wobble | 2 |
| **ViennaRNA structure: MFE, paired fraction, AMFE, MFEI** | **4** |

The four structure features (minimum free energy, fraction of paired bases, adjusted MFE per 100 nt, MFE efficiency index) are the strongest discriminators — pre-miRNAs fold into stable hairpins, hard negatives do not.

### Mature miRNA predictor — 30 features per 22-nt window

- Nucleotide + dinucleotide frequencies
- GC/AU content, Shannon entropy, GU wobble
- Positional features (relative position, distance from 5′/3′ ends, distance from center)
- Flanking GC content (5 nt each side)
- **ViennaRNA structure: window MFE, paired fraction, adjusted MFE**

## Architecture

```
apps/
├── api/                          # FastAPI backend
│   ├── scripts/
│   │   ├── download_data.py      # NCBI pre-miRNA download (FASTA)
│   │   ├── download_mirbase.py   # NCBI GenBank download + mature annotation parsing
│   │   ├── train.py              # Pre-miRNA classifier training
│   │   └── train_mature.py       # Mature miRNA predictor training
│   └── src/
│       ├── core/utils/
│       │   ├── features.py       # 94-feature extractor (composition + ViennaRNA)
│       │   ├── mature_features.py # Sliding-window feature extractor (30 features)
│       │   └── structure.py      # ViennaRNA wrapper (dot-bracket, MFE, SVG)
│       ├── api/web/predict/
│       │   ├── routers.py        # /predict, /predict-mature, /features, /stats
│       │   └── schemas.py        # Pydantic request/response models
│       ├── data/
│       │   ├── dataset.csv       # 4,571 labeled pre-miRNA sequences
│       │   └── mirbase_dataset.csv # NCBI GenBank hairpin–mature pairs
│       └── models/
│           ├── model.joblib              # Pre-miRNA classifier
│           ├── model_metrics.json
│           ├── mature_model.joblib       # Mature miRNA predictor
│           └── mature_model_metrics.json
└── frontend/                     # React + TypeScript (Vite)
    └── src/
        ├── components/
        │   ├── SequenceInput.tsx
        │   ├── PredictionResult.tsx
        │   ├── MaturePredictionCard.tsx  # Highlighted sequence + heatmap
        │   ├── SecondaryStructureCard.tsx
        │   ├── StatsPanel.tsx
        │   ├── FeatureImportanceChart.tsx
        │   ├── FeatureBreakdown.tsx
        │   └── NucleotideSequence.tsx
        ├── api.ts
        └── types.ts
```

## Requirements

- Python: [`uv`](https://github.com/astral-sh/uv)
- Node.js + `pnpm`
- [ViennaRNA](https://www.tbi.univie.ac.at/RNA/) (for structure features and SVG rendering)
- Optional: Docker + Docker Compose

## Setup

```bash
make install
```

## Data & training

```bash
# Download pre-miRNA sequences from NCBI (needed for classifier)
make data

# Download GenBank records with mature miRNA annotations (needed for predictor)
make data-mirbase

# Train pre-miRNA classifier
make train

# Train mature miRNA predictor
make train-mature

# Full pipeline (all of the above in order)
make train-all
```

Training compares Random Forest and HistGradientBoostingClassifier via 5-fold CV and saves the best. Runs are logged to MLflow.

## Development

```bash
# Start frontend dev server (Vite, http://localhost:5173)
make dev

# Backend runs separately
cd apps/api && uv run python src/main.py
```

## Docker

Trains locally first, then starts all services via Docker Compose:

```bash
make train          # produce apps/api/src/models/model.joblib
make run            # starts api (8000), frontend (3000), mlflow (5001)
make stop           # stop containers
make down           # remove containers
make logs           # stream logs
```

The models directory is volume-mounted into the API container, so retraining locally is immediately reflected without a rebuild.

## API endpoints

### `POST /predict`

Classify a sequence as pre-miRNA or non-miRNA.

**Request:**
```json
{ "sequence": "UGAGGUAGUAGGUUGUAUAGUUU..." }
```

**Response:**
```json
{
  "prediction": "pre-miRNA",
  "is_mirna": true,
  "confidence": 0.9612,
  "gc_content": 0.4324,
  "length": 72,
  "sequence": "UGAGGUAGUAGGUUGUAUAGUUU...",
  "feature_values": { "mfe": -28.4, "paired_fraction": 0.667, ... },
  "secondary_structure": {
    "dot_bracket": "(((...)))",
    "mfe": -28.4,
    "svg": "<svg>...</svg>"
  }
}
```

Rules: `T` → `U` automatically; only A/U/G/C allowed; minimum 10 nt.

### `POST /predict-mature`

Predict the active mature miRNA position within a pre-miRNA sequence.

**Request:**
```json
{ "sequence": "UGAGGUAGUAGGUUGUAUAGUUU..." }
```

**Response:**
```json
{
  "mature_sequence": "UAGCUUAUCAGACUGAUGUUGA",
  "start": 14,
  "end": 36,
  "confidence": 0.73,
  "window_scores": [0.12, 0.18, ..., 0.73, ...]
}
```

`window_scores` contains a probability per sliding-window position — used by the frontend to render a heatmap over the hairpin sequence.

### `GET /stats`

Returns pre-miRNA classifier metrics (accuracy, F1, sample counts, feature count, model type).

### `GET /features`

Returns feature importances sorted descending.

## MLflow

Training logs all runs. Start the UI locally:

```bash
cd apps/api && uv run mlflow ui --backend-store-uri sqlite:///mlruns/mlflow.db --port 5001
```

Or via Docker: `http://localhost:5001`

## Demo sequences

**Pre-miRNA (positive):**
```
UGAGGUAGUAGGUUGUAUAGUUUAGGGUCACACCCACCACUGGGAGAUAACUAUACAAUCUACUGUCUUUCCUA
```
```
UGUCGGGUAGCUUAUCAGACUGAUGUUGACUGUUGAAUCUCAUGGCAACACCAGUCGAUGGGCUGU
```

**Non-miRNA (negative control):**
```
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
```

## Design choices

- **No deep learning.** Both models use classical ML (Random Forest, HistGradientBoosting) with hand-crafted features. This keeps the approach interpretable and within the scope of a classical Machine Learning course.
- **ViennaRNA structure features.** MFE and paired-fraction are the strongest discriminators for pre-miRNA identity (Zhang et al. 2006). Adding them raised classifier accuracy from ~91% to ~96%.
- **Sliding-window approach for mature prediction.** For each 22-nt window in the hairpin, the model predicts whether that window contains the mature miRNA. Labels come from NCBI GenBank feature annotations (`ncRNA` with `/ncRNA_class="miRNA"`).
- **NCBI as single data source.** Both datasets are fetched from NCBI (FASTA for classifier, GenBank for mature predictor), avoiding dependency on miRBase FTP which is unreliable.
