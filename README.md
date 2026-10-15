# E-commerce POC — Python (FastAPI) reference implementation

Stage 1 of the polyglot chain: **Python → Java → .NET 10 → Node.js**.
Each stage lives in its own repo; the Vue frontend is identical in each.

## What this is
A miniature e-commerce system proving polyglot persistence done right:
- **MongoDB** — product catalog (flexible documents: variants, attributes, tags)
- **PostgreSQL** — orders, written inside real ACID transactions (source of truth)
- **Elasticsearch** — admin order search: full-text, faceted filters, revenue KPIs

## Repo layout
```
backend/            FastAPI app (app/) + seed/reindex scripts (scripts/)
frontend/           Vue 3 + Vite SPA (identical copy in every language repo)
seed/               Shared, language-neutral seed dataset (do not invent your own)
tools/acceptance.py Black-box harness — any backend must pass it over HTTP
CONTRACT.md         Frozen API contract — identical across all 4 ports
docker-compose.yml  Data stack: Postgres :5432, Mongo :27017, ES :9200 (runs on Mac)
```

## Quickstart (Mac)
```bash
cd ~/ecommerce-poc
docker compose up -d                      # data stack
# in this repo:
python3 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env                       # point hosts at the Mac if needed
python backend/scripts/seed.py             # schema + seed + ES reindex + rename fixture
uvicorn app.main:app --app-dir backend --port 8000
# frontend:
cd frontend && npm install && npm run dev
python tools/acceptance.py --base http://localhost:8000
```

## Build order (this repo)
1. Backend: catalog + order write path (Postgres transactions)
2. Sync strategies: dual-write + 15s polling (ES stays in line with Postgres)
3. Search API (Elasticsearch only)
4. Vue frontend — all 5 screens, expert-grade UI
5. README + NOTES.md (learning milestones) → demo → Sir's understanding test
