"""Admin search route — Elasticsearch ONLY (Screen 3)."""
from fastapi import APIRouter, Depends

from app.core.db import get_es
from app.core.settings import settings
from app.models.schemas import SearchRequest, SearchResponse
from app.repositories import search as repo

router = APIRouter()


@router.post("/search/orders", response_model=SearchResponse)
async def search_orders(payload: SearchRequest, es=Depends(get_es)):
    return await repo.search_orders(es, settings.es_index, payload)
