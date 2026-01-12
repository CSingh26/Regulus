from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from regulus_api.api.v1.router import api_router
from regulus_api.core.config import get_settings

settings = get_settings()


def create_app() -> FastAPI:
    app = FastAPI(title="Regulus API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(api_router, prefix="/v1")
    return app


app = create_app()
