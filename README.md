# Y3L Supply Co. — E-commerce POC (Python / FastAPI)

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![Vue](https://img.shields.io/badge/Vue-3-4FC08D?logo=vue.js&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-8-47A248?logo=mongodb&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Elasticsearch](https://img.shields.io/badge/Elasticsearch-8.15-005571?logo=elasticsearch&logoColor=white)

The **reference implementation** of a polyglot e-commerce order-management POC:
one API contract, one Vue storefront, and a **polyglot persistence** data stack —
MongoDB for the catalog, PostgreSQL for orders, Elasticsearch for search.

This is **stage 1** of the polyglot chain. Sibling ports:

| Stage | Language | Repo |
|---|---|---|
| 1 | Python / FastAPI | this repo |
| 2 | Java / Spring Boot | [`ecommerce-poc-java`](https://github.com/Kgramming/ecommerce-poc-java) |
| 3 | .NET 10 | coming next |
| 4 | Node.js | coming next |

## What this is

A miniature e-commerce system that proves polyglot persistence done right.
Every stage implements the **same frozen API** ([`CONTRACT.md`](CONTRACT.md)),
ships the **same Vue 3 SPA**, and must pass the **same 12/12 black-box
acceptance harness** over HTTP.

```
Vue SPA  →  HTTP  →  FastAPI  →  MongoDB      (product catalog)
                               →  PostgreSQL   (orders — source of truth)
                               →  Elasticsearch (admin search — read model)
```

## Features

- **Storefront** — product catalog with photos, category filters, live search, cart drawer, dark mode
- **Checkout** — order placement with INR pricing and instant confirmation
- **Admin search** — full-text order search across customer names *and* line items, status/date/total faceted filters, revenue KPIs
- **Order management** — order detail view, PENDING → PROCESSING → SHIPPED status flow
- **Catalog admin** — create / edit / deactivate products; edits never rewrite order history (**snapshot semantics**)
- **Two sync strategies** — dual-write *and* 15s polling keep Elasticsearch in line with Postgres (spec: implement at least two)

## API

All endpoints are frozen in [`CONTRACT.md`](CONTRACT.md) — identical across every language port.

| Method & path | Store | Notes |
|---|---|---|
| `GET /api/products` | MongoDB | filters: `category`, `q`, `include_inactive` |
| `GET /api/products/:id` | MongoDB | 404 on unknown id |
| `POST /api/products` | MongoDB | → 201 |
| `PUT /api/products/:id` | MongoDB | 400 on empty patch |
| `POST /api/orders` | PostgreSQL | → 201; validates user + live catalog, snapshots title/price, one transaction |
| `GET /api/orders/:id` | PostgreSQL | source of truth, never the search copy |
| `PATCH /api/orders/:id/status` | PG + ES | refreshes the search doc; ES failure never fails the write |
| `POST /api/search/orders` | Elasticsearch | full-text + facets + KPIs |

## Design notes

- **Snapshot semantics** — at order time the backend copies product `title` + `unit_price`
  into the order. The demo proves it: historical orders still show *"Wireless Mouse"
  @ ₹4,199* after the catalog renames it to *"Wireless Mouse Pro" @ ₹4,999*.
- **One transaction** — order + line items insert atomically (`all-or-nothing`).
- **Dual-write with a safety net** — the ES document is indexed with
  `refresh="wait_for"` so it is searchable the moment the API returns; if ES is
  down the sale still succeeds and the polling worker repairs the copy.
- **The nested-query trap** — `items.title` is a nested ES field; a plain
  `multi_match` silently matches nothing. Admin search wraps it in a `nested` query.

## Getting started

**Prerequisites** — Python 3.12+, Node 18+, and the data stack on localhost:
PostgreSQL `:5435`, MongoDB `:27017`, Elasticsearch `:9200`
(see [`~/ecommerce-poc/docker-compose.yml`](../ecommerce-poc/docker-compose.yml) on the demo Mac).

```bash
# backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
python backend/scripts/seed.py      # schema + users + products + orders + ES reindex
uvicorn app.main:app --app-dir backend --port 8000

# frontend (port 5173, /api proxied to :8000)
cd frontend && npm install && npm run dev

# acceptance — 12/12 on a pristine seed
python tools/acceptance.py
```

Environment overrides live in [`.env.example`](.env.example):
`PGHOST/PGPORT/PGDATABASE/PGUSER/PGPASSWORD`, `MONGOHOST/MONGOPORT/MONGODB`,
`ESHOST/ESPORT/ESINDEX`, `SYNC_STRATEGY` (`dual_write` | `polling`).

## Repo layout

```
backend/            FastAPI app (app/) + seed/reindex/esync scripts (scripts/)
frontend/           Vue 3 + Vite SPA — byte-identical copy in every language repo
seed/               Shared, language-neutral dataset: schema.sql, users.sql,
                    orders.sql, products.json, es-mapping.json
tools/acceptance.py Black-box harness (stdlib only) — 12 checks over HTTP
CONTRACT.md         Frozen API contract — identical across all ports
knowledge-bytes/    Guided code tour in STE100 Simplified Technical English
```

## 📚 Knowledge Bytes

Understand how this backend works internally through guided, code-specific
Knowledge Bytes written in ASD-STE100 Simplified Technical English — each byte
names the real source files and functions, shows actual snippets, and explains
what the code does, why it exists, and how it connects to the rest of the
project.

Read them in order — start with `01_Three_Databases.md`:

**[Explore the Knowledge Bytes →](knowledge-bytes/)**

The prompt that generates bytes in this format lives in
[`knowledge-bytes/knowledge-bytes-prompt.md`](knowledge-bytes/knowledge-bytes-prompt.md).
