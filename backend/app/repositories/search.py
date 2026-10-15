"""Elasticsearch order-search repository.

Screen 3 (admin search dashboard) queries Elasticsearch ONLY — never
Postgres or MongoDB. `build_search_body` is pure so it can be unit-tested
without a cluster.
"""
from app.models.schemas import SearchRequest


def build_search_body(req: SearchRequest) -> dict:
    must = []
    if req.query:
        must.append({"multi_match": {
            "query": req.query,
            "fields": ["customer.name^2", "items.title"],
        }})
    filters = []
    if req.statuses:
        filters.append({"terms": {"status": req.statuses}})
    if req.date_from or req.date_to:
        r: dict = {}
        if req.date_from:
            r["gte"] = req.date_from
        if req.date_to:
            r["lte"] = req.date_to
        filters.append({"range": {"order_date": r}})
    if req.min_total is not None or req.max_total is not None:
        r = {}
        if req.min_total is not None:
            r["gte"] = req.min_total
        if req.max_total is not None:
            r["lte"] = req.max_total
        filters.append({"range": {"total_amount": r}})
    return {
        "query": {"bool": {"must": must or [{"match_all": {}}],
                           "filter": filters}},
        "aggs": {
            "by_status": {"terms": {"field": "status"}},
            "revenue": {"sum": {"field": "total_amount"}},
        },
        "sort": [{"order_date": {"order": "desc"}}],
    }


async def search_orders(es, index: str, req: SearchRequest) -> dict:
    body = build_search_body(req)
    resp = await es.search(
        index=index, body=body,
        from_=(req.page - 1) * req.page_size, size=req.page_size)
    total = resp["hits"]["total"]["value"]
    orders = [{
        "order_id": h["_source"]["order_id"],
        "order_date": h["_source"]["order_date"],
        "status": h["_source"]["status"],
        "total_amount": h["_source"]["total_amount"],
        "customer": h["_source"]["customer"],
    } for h in resp["hits"]["hits"]]
    buckets = resp["aggregations"]["by_status"]["buckets"]
    revenue = resp["aggregations"]["revenue"]["value"] or 0.0
    return {
        "total": total,
        "orders": orders,
        "kpis": {
            "total_revenue": revenue,
            "count_by_status": {b["key"]: b["doc_count"] for b in buckets},
        },
    }
