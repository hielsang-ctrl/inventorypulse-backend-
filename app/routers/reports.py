from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import date
import io
import csv
from app.database import get_db
from app.models.product import Product
from app.models.stock_movement import StockMovement, MovementType
from app.models.category import Category
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/inventory-valuation")
def inventory_valuation(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    products = db.query(Product).filter(Product.is_active == True).all()
    rows = [
        {
            "id": p.id,
            "sku": p.sku,
            "name": p.name,
            "current_stock": p.current_stock,
            "unit_cost": float(p.unit_cost),
            "total_value": float(p.unit_cost) * p.current_stock,
        }
        for p in products
    ]
    total = sum(r["total_value"] for r in rows)
    return {"products": rows, "total_value": total}


@router.get("/stock-movement-summary")
def stock_movement_summary(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(
        StockMovement.product_id,
        StockMovement.type,
        func.sum(StockMovement.quantity).label("total_qty"),
    )
    if from_date:
        q = q.filter(StockMovement.movement_date >= from_date)
    if to_date:
        q = q.filter(StockMovement.movement_date <= to_date)
    q = q.group_by(StockMovement.product_id, StockMovement.type)
    rows = q.all()

    summary: dict = {}
    for row in rows:
        if row.product_id not in summary:
            summary[row.product_id] = {"in": 0, "out": 0}
        key = "in" if row.type == MovementType.in_ else "out"
        summary[row.product_id][key] = row.total_qty

    result = []
    for product_id, data in summary.items():
        product = db.query(Product).filter(Product.id == product_id).first()
        result.append({
            "product_id": product_id,
            "product_name": product.name if product else "Unknown",
            "sku": product.sku if product else "",
            "total_in": data["in"],
            "total_out": data["out"],
            "net": data["in"] - data["out"],
        })
    return result


@router.get("/export/csv")
def export_inventory_csv(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    products = (
        db.query(Product, Category.name.label("category_name"))
        .outerjoin(Category, Product.category_id == Category.id)
        .filter(Product.is_active == True)
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "SKU", "Name", "Category", "Unit", "Unit Cost", "Selling Price", "Stock", "Min Threshold"])
    for p, cat_name in products:
        writer.writerow([
            p.id, p.sku, p.name, cat_name or "",
            p.unit_of_measure, float(p.unit_cost), float(p.selling_price),
            p.current_stock, p.min_threshold,
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=inventory.csv"},
    )
