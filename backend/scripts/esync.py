"""Shared ES reindex logic (sync drivers) — used by seed.py and reindex.py."""
import json
import os

import psycopg
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from app.core.settings import settings

SEED_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "seed")


def fetch_orders_with_items():
    """All Postgres orders flattened the way the ES mapping wants them."""
    with psycopg.connect(settings.postgres_dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT o.id, o.order_date, o.status, o.total_amount, o.updated_at,
                          u.id, u.name, u.email
                   FROM orders o JOIN users u ON u.id = o.user_id
                   ORDER BY o.id""")
            orows = cur.fetchall()
            cur.execute(
                """SELECT order_id, product_id, title, quantity, unit_price
                   FROM order_items ORDER BY order_id, id""")
            items: dict[int, list] = {}
            for r in cur.fetchall():
                items.setdefault(r[0], []).append({
                    "product_id": r[1], "title": r[2], "quantity": r[3],
                    "unit_price": float(r[4])})
    docs = []
    for (oid, dt, status, total, upd, uid, name, email) in orows:
        docs.append({
            "order_id": oid, "order_date": dt.isoformat(), "status": status,
            "total_amount": float(total), "updated_at": upd.isoformat(),
            "customer": {"id": uid, "name": name, "email": email},
            "items": items.get(oid, []),
        })
    return docs


def reindex_es() -> int:
    """Drop + recreate the ES index from the mapping, bulk-load every order."""
    es = Elasticsearch(settings.es_url)
    if es.indices.exists(index=settings.es_index):
        es.indices.delete(index=settings.es_index)
    mapping = json.load(open(os.path.join(SEED_DIR, "es-mapping.json")))["mappings"]
    es.indices.create(index=settings.es_index, mappings=mapping)
    docs = fetch_orders_with_items()
    actions = ({"_index": settings.es_index, "_id": str(d["order_id"]),
                "_source": d} for d in docs)
    bulk(es, actions)
    es.indices.refresh(index=settings.es_index)
    return len(docs)
