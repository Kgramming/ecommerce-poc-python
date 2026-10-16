# 02 — The Product Catalog Lives in MongoDB

Source files in this byte: `backend/app/repositories/products.py`, `seed/products.json`

---

### Byte 2: The product catalog lives in MongoDB

**Builds on:** 1

**In plain terms:** Products are documents. A document is a JSON-like record with flexible fields. MongoDB stores documents. Each product has a SKU, a title, a price, a category, tags, and an `active` flag. The API exposes the MongoDB `_id` as a plain string field named `id`.

**The code:**
```python
# backend/app/repositories/products.py — every product read goes through here
def to_product(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),      # ObjectId -> hex string for the API
        "sku": doc["sku"],
        "title": doc["title"],
        "price": float(doc["price"]),
        "category": doc["category"],
        "active": doc.get("active", True),
        ...
    }
```

**What's happening:** `to_product` converts a raw MongoDB document into the API shape. It turns the `_id` ObjectId into a string. It forces `price` to a float. It defaults `active` to true when the field is absent. Every product endpoint returns this shape.

**Why it matters:** The frontend and the order code both expect string IDs. Without this conversion, the API would leak database internals. One function guarantees one shape everywhere.

---
