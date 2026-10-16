"""E-commerce POC backend (Python/FastAPI) — the reference implementation.

Chain: Python -> Java -> .NET 10 -> Node.js. This repo is stage 1.
The API surface is frozen in CONTRACT.md and must stay identical across ports.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import knowledge_bytes, orders, products, search
from app.core.db import lifespan
from app.core.settings import settings


def create_app() -> FastAPI:
    app = FastAPI(title="E-commerce POC API", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health():
        return {"status": "ok"}

    app.include_router(products.router, prefix="/api")
    app.include_router(orders.router, prefix="/api")
    app.include_router(search.router, prefix="/api")
    app.include_router(knowledge_bytes.router, prefix="/api")
    return app


app = create_app()
