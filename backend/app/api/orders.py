"""Order routes — Postgres is the source of truth (Screens 2 + 4)."""
from fastapi import APIRouter, Depends, HTTPException

from app.core.db import get_es, get_mongo, get_pg
from app.core.settings import settings
from app.models.schemas import OrderOut, OrderPlace, StatusUpdate
from app.repositories import orders as repo
from app.services import sync as sync_service
from app.services.orders import OrderError, place_order

router = APIRouter()

VALID_STATUSES = {"PENDING", "PROCESSING", "SHIPPED"}


@router.post("/orders", response_model=OrderOut, status_code=201)
async def create_order(payload: OrderPlace, pg=Depends(get_pg),
                       mongo=Depends(get_mongo), es=Depends(get_es)):
    try:
        return await place_order(pg, mongo, es, payload.user_id, payload.items)
    except OrderError as e:
        raise HTTPException(400, str(e))


@router.get("/orders/{oid}", response_model=OrderOut)
async def get_order(oid: int, pg=Depends(get_pg)):
    o = await repo.get_order(pg, oid)
    if not o:
        raise HTTPException(404, "order not found")
    return o


@router.patch("/orders/{oid}/status", response_model=OrderOut)
async def patch_status(oid: int, payload: StatusUpdate,
                       pg=Depends(get_pg), es=Depends(get_es)):
    if payload.status not in VALID_STATUSES:
        raise HTTPException(
            422, f"status must be one of {sorted(VALID_STATUSES)}")
    o = await repo.update_order_status(pg, oid, payload.status)
    if not o:
        raise HTTPException(404, "order not found")
    # Keep Screen 3 accurate: refresh the ES doc. If ES is down the write
    # path still succeeded — the polling worker recovers the dashboard.
    try:
        await sync_service.index_order(es, settings.es_index, o)
    except Exception:
        pass
    return o
