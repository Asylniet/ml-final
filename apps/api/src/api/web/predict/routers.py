import logging

import numpy as np
from fastapi import APIRouter, Request

from api.web.predict.schemas import PredictionResponseSchema, SequenceInputSchema
from core.utils.exc import PredictionException
from core.utils.features import extract_features

logger = logging.getLogger(__name__)

router = APIRouter(tags=["predict"])


@router.get("/")
async def health_check():
    return {"message": "ML API is running"}


@router.post("/predict", response_model=PredictionResponseSchema)
async def predict(request: Request, body: SequenceInputSchema):
    sequence = body.sequence
    model = request.app.state.model

    features = extract_features(sequence).reshape(1, -1)
    try:
        prediction = int(model.predict(features)[0])
        proba = model.predict_proba(features)[0]
    except Exception as exc:
        raise PredictionException(str(exc)) from exc

    confidence = float(proba[prediction])
    gc_content = (sequence.count("G") + sequence.count("C")) / len(sequence)

    return PredictionResponseSchema(
        prediction="pre-miRNA" if prediction == 1 else "non-miRNA",
        is_mirna=prediction == 1,
        confidence=round(confidence, 4),
        gc_content=round(gc_content, 4),
        length=len(sequence),
        sequence=sequence,
    )
