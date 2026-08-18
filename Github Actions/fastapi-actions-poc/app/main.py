"""
Simple FastAPI application used as a POC for demoing GitHub Actions.

Endpoints:
  GET  /            -> health/welcome message
  GET  /health       -> health check (used by CI / uptime checks)
  GET  /items/{id}   -> fetch a fake item by id
  POST /items        -> create a fake item (stored in-memory)
"""

from typing import Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="GitHub Actions POC API",
    description="A tiny FastAPI app used to demo CI/CD with GitHub Actions",
    version="1.0.0",
)

# simple in-memory "database" for demo purposes
items_db: Dict[int, "Item"] = {}


class Item(BaseModel):
    name: str
    price: float
    in_stock: bool = True


@app.get("/")
def read_root():
    """Root endpoint - simple welcome message."""
    return {"message": "Welcome to the GitHub Actions POC API"}


@app.get("/health")
def health_check():
    """Health check endpoint - useful for CI smoke tests and uptime monitors."""
    return {"status": "ok"}


@app.get("/items/{item_id}")
def get_item(item_id: int):
    """Fetch an item by its id. Returns 404 if not found."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]


@app.post("/items", status_code=201)
def create_item(item: Item):
    """Create a new item and store it in memory."""
    new_id = len(items_db) + 1
    items_db[new_id] = item
    return {"id": new_id, **item.model_dump()}
