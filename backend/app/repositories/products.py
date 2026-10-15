"""MongoDB product-catalog repository. Products are read from MongoDB ONLY."""
from bson import ObjectId

from app.core.dates import utcnow


def to_product(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "sku": doc["sku"],
        "title": doc["title"],
        "description": doc.get("description", ""),
        "price": float(doc["price"]),
        "category": doc["category"],
        "tags": doc.get("tags", []),
        "attributes": doc.get("attributes", {}),
        "variants": doc.get("variants", []),
        "active": doc.get("active", True),
        "updated_at": doc.get("updated_at") or "",
    }


def _oid(pid: str):
    try:
        return ObjectId(pid)
    except Exception:
        return None


async def list_products(db, category: str | None = None, q: str | None = None):
    filt: dict = {"active": True}
    if category:
        filt["category"] = category
    if q:
        rx = {"$regex": q, "$options": "i"}
        filt["$or"] = [{"title": rx}, {"tags": rx}]
    docs = await db.products.find(filt).sort("title", 1).to_list(length=1000)
    return [to_product(d) for d in docs]


async def get_product(db, pid: str):
    oid = _oid(pid)
    if not oid:
        return None
    doc = await db.products.find_one({"_id": oid})
    return to_product(doc) if doc else None


async def get_many(db, pids: list[str]) -> dict:
    """Bulk fetch for order validation. Returns {str_id: product}."""
    oids = [o for o in (_oid(p) for p in pids) if o]
    if not oids:
        return {}
    docs = await db.products.find({"_id": {"$in": oids}}).to_list(length=1000)
    return {str(d["_id"]): to_product(d) for d in docs}


async def create_product(db, data: dict):
    doc = dict(data)
    doc["updated_at"] = utcnow()
    res = await db.products.insert_one(doc)
    doc["_id"] = res.inserted_id
    return to_product(doc)


async def update_product(db, pid: str, patch: dict):
    oid = _oid(pid)
    if not oid:
        return None
    patch = dict(patch)
    patch["updated_at"] = utcnow()
    doc = await db.products.find_one_and_update(
        {"_id": oid}, {"$set": patch}, return_document=True)
    return to_product(doc) if doc else None
