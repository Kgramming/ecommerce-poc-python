"""Database clients + FastAPI lifespan.

Postgres: psycopg3 async pool.  MongoDB: motor.  ES: elasticsearch-py async.
"""
import asyncio
import logging
from contextlib import asynccontextmanager

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Request
from motor.motor_asyncio import AsyncIOMotorClient
from psycopg_pool import AsyncConnectionPool

from app.core.settings import settings
from app.services import sync as sync_service

log = logging.getLogger("ecommerce")


@asynccontextmanager
async def lifespan(app: FastAPI):
    pg = AsyncConnectionPool(settings.postgres_dsn, open=False)
    await pg.open()
    mongo = AsyncIOMotorClient(settings.mongo_dsn)
    es = AsyncElasticsearch(settings.es_url)

    app.state.pg = pg
    app.state.mongo_db = mongo[settings.mongo_db]
    app.state.es = es

    try:
        await sync_service.ensure_index(es, settings.es_index)
    except Exception as e:  # never fail boot because ES is napping
        log.warning("ES index ensure failed at startup: %s", e)

    stop = asyncio.Event()
    worker = None
    if settings.sync_strategy == "polling":
        worker = asyncio.create_task(sync_service.poll_worker(app, stop))
        log.info("polling sync worker started (every %ds)",
                 settings.poll_interval_seconds)

    yield

    stop.set()
    if worker:
        await worker
    await pg.close()
    mongo.close()
    await es.close()


def get_pg(request: Request):
    return request.app.state.pg


def get_mongo(request: Request):
    return request.app.state.mongo_db


def get_es(request: Request):
    return request.app.state.es
