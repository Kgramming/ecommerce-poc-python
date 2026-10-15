"""PostgreSQL order repository.

Orders are the source of truth: every write goes through a real DB transaction.
Reads here hit Postgres ONLY (never Elasticsearch) for fulfillment data.
"""
from psycopg_pool import AsyncConnectionPool

_ORDER_SELECT = """SELECT o.id, o.user_id, o.order_date, o.status, o.total_amount,
       o.updated_at, u.name, u.email,
       i.product_id, i.title, i.quantity, i.unit_price
FROM orders o
JOIN users u ON u.id = o.user_id
LEFT JOIN order_items i ON i.order_id = o.id"""


def _group(rows) -> list[dict]:
    orders: dict[int, dict] = {}
    for r in rows:
        oid = r[0]
        if oid not in orders:
            orders[oid] = {
                "id": r[0], "user_id": r[1],
                "order_date": r[2].isoformat(), "status": r[3],
                "total_amount": float(r[4]), "updated_at": r[5].isoformat(),
                "customer": {"id": r[1], "name": r[6], "email": r[7]},
                "items": [],
            }
        if r[8] is not None:
            orders[oid]["items"].append({
                "product_id": r[8], "title": r[9], "quantity": r[10],
                "unit_price": float(r[11]),
            })
    return list(orders.values())


async def get_user(pool: AsyncConnectionPool, user_id: int):
    async with pool.connection() as conn:
        cur = await conn.execute(
            "SELECT id, name, email FROM users WHERE id = %s", (user_id,))
        row = await cur.fetchone()
        return {"id": row[0], "name": row[1], "email": row[2]} if row else None


async def create_order(pool: AsyncConnectionPool, user_id: int,
                       snapshots: list[dict], total: float):
    """Insert one order + N items atomically. All-or-nothing.

    Returns (order_id, order_date, updated_at).
    """
    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(
                """INSERT INTO orders (user_id, order_date, status, total_amount)
                   VALUES (%s, now(), 'PENDING', %s)
                   RETURNING id, order_date, updated_at""",
                (user_id, total))
            order_id, order_date, updated_at = await cur.fetchone()
            for s in snapshots:
                await conn.execute(
                    """INSERT INTO order_items
                           (order_id, product_id, title, quantity, unit_price)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (order_id, s["product_id"], s["title"],
                     s["quantity"], s["unit_price"]))
            return order_id, order_date, updated_at


async def get_order(pool: AsyncConnectionPool, order_id: int):
    async with pool.connection() as conn:
        cur = await conn.execute(
            _ORDER_SELECT + " WHERE o.id = %s ORDER BY i.id", (order_id,))
        grouped = _group(await cur.fetchall())
        return grouped[0] if grouped else None


async def update_order_status(pool: AsyncConnectionPool, order_id: int,
                              status: str):
    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(
                "UPDATE orders SET status = %s, updated_at = now() WHERE id = %s",
                (status, order_id))
            if cur.rowcount == 0:
                return None
    return await get_order(pool, order_id)


async def list_orders_since(pool: AsyncConnectionPool, since):
    """Order ids changed after `since` — feeds the polling sync worker."""
    async with pool.connection() as conn:
        cur = await conn.execute(
            "SELECT id FROM orders WHERE updated_at > %s ORDER BY updated_at",
            (since,))
        return [r[0] for r in await cur.fetchall()]


async def list_all_orders(pool: AsyncConnectionPool):
    async with pool.connection() as conn:
        cur = await conn.execute(_ORDER_SELECT + " ORDER BY o.id, i.id")
        return _group(await cur.fetchall())
