"""商城 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.models import Product, Order
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import get_db

router = APIRouter(prefix="/api/shop", tags=["shop"])


@router.get("/products")
def list_products(db: Session = Depends(get_db)):
    products = db.query(Product).order_by(Product.category, Product.name).all()
    return {"products": [p_to_dict(p) for p in products]}


@router.get("/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(404, "商品不存在")
    return p_to_dict(p)


@router.post("/orders")
def create_order(data: dict, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == data.get("product_id")).first()
    if not p:
        raise HTTPException(404, "商品不存在")
    quantity = data.get("quantity", 1)
    if quantity > p.stock:
        raise HTTPException(400, "庫存不足")
    order = Order(
        product_id=p.id,
        customer_name=data.get("customer_name", ""),
        quantity=quantity,
        total_price=p.price * quantity,
        status="pending",
    )
    p.stock -= quantity
    db.add(order)
    db.commit()
    db.refresh(order)
    return {
        "id": order.id, "product_name": p.name,
        "quantity": order.quantity, "total_price": order.total_price,
        "status": order.status,
    }


@router.get("/orders")
def list_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).order_by(Order.created_at.desc()).limit(50).all()
    result = []
    for o in orders:
        product = db.query(Product).filter(Product.id == o.product_id).first()
        result.append({
            "id": o.id, "product_name": product.name if product else "",
            "customer_name": o.customer_name, "quantity": o.quantity,
            "total_price": o.total_price, "status": o.status,
            "created_at": o.created_at.isoformat(),
        })
    return {"orders": result}


def p_to_dict(p: Product):
    return {
        "id": p.id, "name": p.name, "description": p.description,
        "price": p.price, "image_url": p.image_url, "stock": p.stock,
        "category": p.category,
    }
