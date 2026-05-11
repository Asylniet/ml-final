import logging
from contextlib import asynccontextmanager

import joblib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.web.predict.routers import router as predict_router
from core.config.logging_setup import setup_logging
from core.config.settings.app import settings
from core.utils.exc import ModelLoadException, PredictionException

setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.model = joblib.load(settings.model_path)
        logger.info("Model loaded from %s", settings.model_path)
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
