import json
from fastapi import FastAPI, HTTPException
from pathlib import Path
from pydantic import BaseModel


class Product(BaseModel):
    name: str
    price: float
    description: str
    created_at: str


app = FastAPI(title="E-Shop-CI-CD")

with open(Path(__file__).parent / "shop.json", "r", encoding="utf-8") as f:
    PRODUCTS = json.load(f)


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