"""Pydantic schemas — mirrors CONTRACT.md exactly."""
from typing import Any, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------- products ---
class Product(BaseModel):
    id: str
    sku: str
    title: str
    description: str
    price: float
    category: str
    tags: list[str]
    attributes: dict[str, Any]
    variants: list[dict[str, Any]]
    active: bool
    updated_at: str


class ProductCreate(BaseModel):
    sku: str
    title: str
    description: str = ""
    price: float = Field(gt=0)
    category: str
    tags: list[str] = []
    attributes: dict[str, Any] = {}
    variants: list[dict[str, Any]] = []
    active: bool = True


class ProductUpdate(BaseModel):
    sku: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None
    attributes: Optional[dict[str, Any]] = None
    variants: Optional[list[dict[str, Any]]] = None
    active: Optional[bool] = None


class ProductList(BaseModel):
    products: list[Product]
    total: int


# ------------------------------------------------------------------ orders ---
class OrderItemIn(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)


class OrderPlace(BaseModel):
    user_id: int
    items: list[OrderItemIn] = Field(min_length=1)


class OrderItemOut(BaseModel):
    product_id: str
    title: str
    quantity: int
    unit_price: float


class CustomerOut(BaseModel):
    id: int
    name: str
    email: str


class OrderOut(BaseModel):
    id: int
    user_id: int
    customer: CustomerOut
    order_date: str
    status: str
    total_amount: float
    updated_at: str
    items: list[OrderItemOut]


class StatusUpdate(BaseModel):
    status: str


# ------------------------------------------------------------------ search ---
class SearchRequest(BaseModel):
    query: Optional[str] = None
    statuses: Optional[list[str]] = None
    date_from: Optional[str] = None  # YYYY-MM-DD
    date_to: Optional[str] = None    # YYYY-MM-DD
    min_total: Optional[float] = None
    max_total: Optional[float] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=1000)


class SearchOrderHit(BaseModel):
    order_id: int
    order_date: str
    status: str
    total_amount: float
    customer: CustomerOut


class SearchKpis(BaseModel):
    total_revenue: float
    count_by_status: dict[str, int]


class SearchResponse(BaseModel):
    total: int
    orders: list[SearchOrderHit]
    kpis: SearchKpis
