"""Product catalog routes — MongoDB ONLY (Screen 1 + Screen 5)."""
from fastapi import APIRouter, Depends, HTTPException

from app.core.db import get_mongo
from app.models.schemas import Product, ProductCreate, ProductList, ProductUpdate
from app.repositories import products as repo

router = APIRouter()


@router.get("/products", response_model=ProductList)
async def list_products(category: str | None = None, q: str | None = None,
                        mongo=Depends(get_mongo)):
    items = await repo.list_products(mongo, category=category, q=q)
    return {"products": items, "total": len(items)}


@router.get("/products/{pid}", response_model=Product)
async def get_product(pid: str, mongo=Depends(get_mongo)):
    p = await repo.get_product(mongo, pid)
    if not p:
        raise HTTPException(404, "product not found")
    return p


@router.post("/products", response_model=Product, status_code=201)
async def create_product(payload: ProductCreate, mongo=Depends(get_mongo)):
    return await repo.create_product(mongo, payload.model_dump())


@router.put("/products/{pid}", response_model=Product)
async def update_product(pid: str, payload: ProductUpdate,
                         mongo=Depends(get_mongo)):
    patch = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not patch:
        raise HTTPException(400, "empty update")
    p = await repo.update_product(mongo, pid, patch)
    if not p:
        raise HTTPException(404, "product not found")
    return p
