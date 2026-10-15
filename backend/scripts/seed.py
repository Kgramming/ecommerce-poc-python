#!/usr/bin/env python3
"""Seed the whole data stack (idempotent: clears and reloads everything).

Order: schema -> users -> products (MongoDB) -> orders -> ES reindex
       -> rename fixture (Wireless Mouse -> Wireless Mouse Pro, MongoDB only).

Run from the repo root:
    python backend/scripts/seed.py
"""
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import psycopg  # noqa: E402
from bson import ObjectId  # noqa: E402
from pymongo import MongoClient  # noqa: E402

from app.core.settings import settings  # noqa: E402
from esync import reindex_es  # noqa: E402

SEED_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "seed")


def run_sql(path: str):
    with open(path) as f:
        sql = f.read()
    with psycopg.connect(settings.postgres_dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()


def truncate_pg():
    """Wipe seed tables so re-runs are clean (idempotent seed)."""
    with psycopg.connect(settings.postgres_dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "TRUNCATE TABLE order_items, orders, users RESTART IDENTITY CASCADE;")
        conn.commit()


def main():
    print("1/6  PostgreSQL schema ...")
    run_sql(os.path.join(SEED_DIR, "schema.sql"))
    print("     clearing any previous seed data ...")
    truncate_pg()

    print("2/6  users ...")
    run_sql(os.path.join(SEED_DIR, "users.sql"))

    print("3/6  products -> MongoDB ...")
    with open(os.path.join(SEED_DIR, "products.json")) as f:
        products = json.load(f)
    col = MongoClient(settings.mongo_dsn)[settings.mongo_db].products
    col.delete_many({})
    for p in products:
        p["_id"] = ObjectId(p["_id"])
    col.insert_many(products)
    print(f"     inserted {len(products)} products")

    print("4/6  orders -> PostgreSQL ...")
    run_sql(os.path.join(SEED_DIR, "orders.sql"))

    print("5/6  Elasticsearch reindex ...")
    n = reindex_es()
    print(f"     indexed {n} orders")

    print("6/6  rename fixture: 'Wireless Mouse' -> 'Wireless Mouse Pro' ...")
    res = col.update_one(
        {"sku": "WM-001"},
        {"$set": {"title": "Wireless Mouse Pro", "price": 4999,
                  "updated_at": datetime.now(timezone.utc).isoformat()
                  .replace("+00:00", "Z")}})
    print(f"     matched {res.matched_count} product "
          f"(historical orders keep the old snapshot)")
    print("seed complete.")


if __name__ == "__main__":
    main()
