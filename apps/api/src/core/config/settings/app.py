from core.config.settings.base import BaseSettings
from core.config.settings.server import ServerSettings


class ApplicationSettings(BaseSettings):
    server: ServerSettings = ServerSettings()
    model_path: str = "src/models/model.joblib"
    CORS_ALLOW_ORIGINS: list[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]


settings = ApplicationSettings()
