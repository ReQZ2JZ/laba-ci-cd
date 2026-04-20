import json
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel


class Product(BaseModel):
    name: str
    price: float
    description: str
    created_at: str


app = FastAPI(title="E-Shop-CI-CD")

with open(Path(__file__).parent / "shop.json", "r", encoding="utf-8") as f:
    PRODUCTS = json.load(f)

CART = []
ORDERS = []


@app.get("/products")
async def get_products():
    return PRODUCTS


@app.get("/product/{pid}")
async def get_product(pid: int):
    if 0 <= pid < len(PRODUCTS):
        return PRODUCTS[pid]
    raise HTTPException(status_code=404, detail="Not found")


@app.get("/health")
async def health():
    return {"status": "ok", "products": len(PRODUCTS)}


@app.get("/search")
async def search(q: str = Query(..., min_length=1)):
    """Поиск товаров по подстроке в названии (q). Регистр не учитывается."""
    query = q.lower()
    result = [product for product in PRODUCTS if query in product["name"].lower()]
    return result


@app.get("/cart")
async def get_cart():
    """Возвращает содержимое корзины и общую сумму."""
    total = sum(item["price"] * item["qty"] for item in CART)
    return {"items": CART, "total": total}


@app.post("/cart/add")
async def add_cart(pid: int, qty: int = 1):
    """Добавляет товар в корзину по id (pid) и количеству (qty)."""
    if not (0 <= pid < len(PRODUCTS)):
        raise HTTPException(status_code=404, detail="Product not found")

    if qty < 1:
        raise HTTPException(status_code=400, detail="qty must be >= 1")

    product = PRODUCTS[pid]

    cart_item = {
        "pid": pid,
        "name": product["name"],
        "price": product["price"],
        "qty": qty,
    }

    CART.append(cart_item)
    return {"ok": True, "item": cart_item}


@app.delete("/cart")
async def clear_cart():
    """Очищает корзину полностью."""
    CART.clear()
    return {"ok": True}


@app.post("/checkout")
async def checkout():
    """Оформляет заказ: сохраняет текущую корзину в заказы, очищает корзину."""
    if not CART:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total = sum(item["price"] * item["qty"] for item in CART)

    order = {
        "id": len(ORDERS) + 1,
        "items": CART.copy(),
        "total": total,
        "created_at": datetime.now().isoformat(),
    }

    ORDERS.append(order)
    CART.clear()
    return order


@app.get("/orders")
async def get_orders():
    """Возвращает список всех оформленных заказов."""
    return ORDERS