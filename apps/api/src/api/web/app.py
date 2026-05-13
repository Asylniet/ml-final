import logging
<<<<<<< HEAD
import json
from pathlib import Path
=======
>>>>>>> d7a84cde81472fa331c529ee30cf2e30082145da
from contextlib import asynccontextmanager

import joblib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.web.predict.routers import router as predict_router
<<<<<<< HEAD
from core.utils.features import FEATURE_NAMES
=======
>>>>>>> d7a84cde81472fa331c529ee30cf2e30082145da
from core.config.logging_setup import setup_logging
from core.config.settings.app import settings
from core.utils.exc import ModelLoadException, PredictionException

setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
<<<<<<< HEAD
        model_path = Path(settings.model_path)
        metrics_path = model_path.with_name("model_metrics.json")

        app.state.model = joblib.load(model_path)
        logger.info("Model loaded from %s", model_path)

        app.state.model_stats = json.loads(metrics_path.read_text())
        logger.info("Model metrics loaded from %s", metrics_path)

        importances = getattr(app.state.model, "feature_importances_", None)
        if importances is None:
            app.state.feature_importances = []
        else:
            pairs = [
                {"name": name, "importance": float(importance)}
                for name, importance in zip(FEATURE_NAMES, importances, strict=False)
            ]
            app.state.feature_importances = sorted(
                pairs, key=lambda item: item["importance"], reverse=True
            )
=======
        app.state.model = joblib.load(settings.model_path)
        logger.info("Model loaded from %s", settings.model_path)
>>>>>>> d7a84cde81472fa331c529ee30cf2e30082145da
    except Exception as exc:
        raise ModelLoadException(f"Failed to load model: {exc}") from exc
    yield


app = FastAPI(lifespan=lifespan)


async def model_load_error_handler(req, exception: ModelLoadException):
    return JSONResponse(content={"detail": str(exception)}, status_code=503)


async def prediction_error_handler(req, exception: PredictionException):
    return JSONResponse(content={"detail": str(exception)}, status_code=500)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict_router)

app.add_exception_handler(ModelLoadException, model_load_error_handler)
app.add_exception_handler(PredictionException, prediction_error_handler)
