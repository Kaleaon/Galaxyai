from __future__ import annotations

from fastapi import FastAPI

from app.backend.routers.domains import router as domains_router
from app.backend.routers.falsify import router as falsify_router
from app.backend.routers.ingest import router as ingest_router
from app.backend.routers.map3d import router as map3d_router
from app.backend.routers.query import router as query_router


def create_app() -> FastAPI:
    app = FastAPI(title="GalaxyAI Backend")
    app.include_router(domains_router)
    app.include_router(ingest_router)
    app.include_router(falsify_router)
    app.include_router(query_router)
    app.include_router(map3d_router)
    return app


app = create_app()
