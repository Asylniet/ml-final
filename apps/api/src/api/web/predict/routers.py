import logging

<<<<<<< HEAD
from fastapi import APIRouter, Request

from api.web.predict.schemas import (
    FeatureImportanceItem,
    ModelStatsSchema,
    PredictionResponseSchema,
    SecondaryStructureSchema,
    SequenceInputSchema,
)
from core.utils.exc import PredictionException
from core.utils.features import FEATURE_NAMES, extract_features
from core.utils.structure import build_structure_payload
=======
import numpy as np
from fastapi import APIRouter, Request

from api.web.predict.schemas import PredictionResponseSchema, SequenceInputSchema
from core.utils.exc import PredictionException
from core.utils.features import extract_features
>>>>>>> d7a84cde81472fa331c529ee30cf2e30082145da

logger = logging.getLogger(__name__)

router = APIRouter(tags=["predict"])


@router.get("/")
async def health_check():
    return {"message": "ML API is running"}


@router.post("/predict", response_model=PredictionResponseSchema)
async def predict(request: Request, body: SequenceInputSchema):
    sequence = body.sequence
    model = request.app.state.model

<<<<<<< HEAD
    feature_vector = extract_features(sequence)
    features = feature_vector.reshape(1, -1)
=======
    features = extract_features(sequence).reshape(1, -1)
>>>>>>> d7a84cde81472fa331c529ee30cf2e30082145da
    try:
        prediction = int(model.predict(features)[0])
        proba = model.predict_proba(features)[0]
    except Exception as exc:
        raise PredictionException(str(exc)) from exc

    confidence = float(proba[prediction])
    gc_content = (sequence.count("G") + sequence.count("C")) / len(sequence)
<<<<<<< HEAD
    feature_values = {
        name: float(value) for name, value in zip(FEATURE_NAMES, feature_vector, strict=False)
    }
    secondary_structure = build_structure_payload(sequence)
=======
>>>>>>> d7a84cde81472fa331c529ee30cf2e30082145da

    return PredictionResponseSchema(
        prediction="pre-miRNA" if prediction == 1 else "non-miRNA",
        is_mirna=prediction == 1,
        confidence=round(confidence, 4),
        gc_content=round(gc_content, 4),
        length=len(sequence),
        sequence=sequence,
<<<<<<< HEAD
        feature_values=feature_values,
        secondary_structure=SecondaryStructureSchema(**secondary_structure),
    )


@router.get("/features", response_model=list[FeatureImportanceItem])
async def get_feature_importances(request: Request):
    return request.app.state.feature_importances


@router.get("/stats", response_model=ModelStatsSchema)
async def get_model_stats(request: Request):
    return request.app.state.model_stats
=======
    )
>>>>>>> d7a84cde81472fa331c529ee30cf2e30082145da
