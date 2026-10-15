"""Order placement orchestration — the transactional write path.

1. Validate the user exists (Postgres).
2. Validate every line item against the LIVE MongoDB catalog (active products).
3. Snapshot title + unit price at order time (later catalog edits never rewrite history).
4. Insert order + items inside ONE Postgres transaction (all-or-nothing).
5. Fire the ES sync trigger (dual-write now; the polling worker also picks it up).
"""
import logging

from app.core.settings import settings
from app.repositories import orders as orders_repo
from app.repositories import products as products_repo
from app.services import sync as sync_service

log = logging.getLogger("ecommerce.orders")


class OrderError(Exception):
    """A 400-level order problem (bad product, inactive product, unknown user)."""


async def place_order(pg, mongo_db, es, user_id: int, items_in) -> dict:
    user = await orders_repo.get_user(pg, user_id)
    if not user:
        raise OrderError(f"unknown user_id {user_id}")

    wanted = {it.product_id: it.quantity for it in items_in}
    found = await products_repo.get_many(mongo_db, list(wanted))

    snapshots = []
    for pid, qty in wanted.items():
        p = found.get(pid)
        if not p:
            raise OrderError(f"unknown product_id {pid}")
        if not p["active"]:
            raise OrderError(f"product '{p['title']}' is not active")
        snapshots.append({"product_id": pid, "title": p["title"],
                          "quantity": qty, "unit_price": p["price"]})

    total = round(sum(s["unit_price"] * s["quantity"] for s in snapshots), 2)
    order_id, _, _ = await orders_repo.create_order(pg, user_id, snapshots, total)
    order = await orders_repo.get_order(pg, order_id)

    # Sync trigger — strategy A writes through now; strategy B's worker also
    # picks this row up on its next pass, so both stay correct together.
    if settings.sync_strategy == "dual_write":
        try:
            await sync_service.index_order(es, settings.es_index, order)
        except Exception as e:
            # Write path already committed: never fail the order because ES
            # is napping. Logged; polling worker or manual reindex recovers.
            log.error("dual-write to ES failed for order %s: %s", order_id, e)

    return order
