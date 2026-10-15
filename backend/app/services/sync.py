"""Elasticsearch synchronization — keeps the admin dashboard in line with Postgres.

Two strategies (implement at least two per the spec):
  A. dual-write — after the Postgres transaction commits, index the order doc.
     If ES is down, the write path still succeeds; the failure is logged and the
     polling worker / a manual reindex recovers it.
  B. polling — background worker every N seconds bulk-syncs recently changed
     orders (idempotent upserts by order_id, 30s overlap so nothing is missed).

`build_es_doc` is pure so it can be unit-tested without a cluster.
"""
import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

from elasticsearch.helpers import async_bulk

log = logging.getLogger("ecommerce.sync")

SEED_DIR = Path(__file__).resolve().parents[3] / "seed"


def build_es_doc(order: dict) -> dict:
    """Flatten a Postgres order (+ snapshots) into the ES `orders` document."""
    return {
        "order_id": order["id"],
        "order_date": order["order_date"],
        "status": order["status"],
        "total_amount": order["total_amount"],
        "updated_at": order["updated_at"],
        "customer": order["customer"],
        "items": order["items"],
    }


async def ensure_index(es, index: str):
    if not await es.indices.exists(index=index):
        mapping = json.loads((SEED_DIR / "es-mapping.json").read_text())["mappings"]
        await es.indices.create(index=index, mappings=mapping)
        log.info("created ES index %s", index)


async def index_order(es, index: str, order: dict):
    # wait_for refresh: the doc must be searchable the moment the API
    # returns, otherwise "view in dashboard" right after placing an order
    # (or the acceptance poll) can miss it for up to one refresh interval.
    await es.index(index=index, id=str(order["id"]),
                   document=build_es_doc(order), refresh="wait_for")


async def index_orders_bulk(es, index: str, orders: list[dict]):
    if not orders:
        return
    actions = ({"_index": index, "_id": str(o["id"]), "_source": build_es_doc(o)}
               for o in orders)
    await async_bulk(es, actions)


async def reindex_all(pg_pool, es, index: str) -> int:
    from app.repositories import orders as orders_repo
    all_orders = await orders_repo.list_all_orders(pg_pool)
    await index_orders_bulk(es, index, all_orders)
    return len(all_orders)


async def poll_worker(app, stop_event):
    """Strategy B: periodically sync Postgres -> ES."""
    from app.core.settings import settings
    from app.repositories import orders as orders_repo

    es, pg, index = app.state.es, app.state.pg, settings.es_index
    interval = settings.poll_interval_seconds
    watermark = datetime.now(timezone.utc) - timedelta(seconds=60)

    try:  # full reindex on worker start so nothing is ever missed
        n = await reindex_all(pg, es, index)
        log.info("poll worker initial reindex: %d orders", n)
    except Exception as e:
        log.warning("poll worker initial reindex failed: %s", e)

    while not stop_event.is_set():
        try:
            ids = await orders_repo.list_orders_since(
                pg, watermark - timedelta(seconds=30))  # overlap: idempotent
            if ids:
                fresh = []
                for i in ids:
                    o = await orders_repo.get_order(pg, i)
                    if o:
                        fresh.append(o)
                await index_orders_bulk(es, index, fresh)
                log.info("poll worker synced %d orders", len(fresh))
            watermark = datetime.now(timezone.utc)
        except Exception as e:
            log.warning("poll worker iteration failed: %s", e)
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval)
        except asyncio.TimeoutError:
            pass
