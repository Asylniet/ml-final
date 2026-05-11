import uvicorn

from core.config.settings.app import settings

if __name__ == "__main__":
    uvicorn.run(
        "api.web.app:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=True,
    )
