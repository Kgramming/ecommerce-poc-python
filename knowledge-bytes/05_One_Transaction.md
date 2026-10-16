# 05 — One Transaction for Order Plus Items

Source files in this byte: `backend/app/repositories/orders.py`

---

### Byte 5: One transaction for order plus items

**Builds on:** 3, 4

**In plain terms:** A *transaction* is a group of writes that succeed or fail together. `create_order` inserts the order row and all its item rows inside one transaction. If any insert fails, the database rolls back everything. There is never an order without items, and never items without an order.

**The code:**
```python
# backend/app/repositories/orders.py — all-or-nothing write
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
```

**What's happening:** The code opens a transaction. It inserts the order and reads back the new id with `RETURNING`. It then inserts each snapshot item with that id. The `async with` block commits at the end, or rolls back on any error.

**Why it matters:** Money data must never be half-written. Without the transaction, a crash could leave an order with no items and a wrong total. The transaction makes the write atomic.

---
