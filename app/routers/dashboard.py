from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.product import Product
from app.models.stock_movement import StockMovement, MovementType
from app.models.alert import Alert
from app.dependencies import get_current_user
from app.models.user import User
from datetime import date, timedelta

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    total_products = db.query(func.count(Product.id)).filter(Product.is_active == True).scalar()
    low_stock = db.query(func.count(Product.id)).filter(
        Product.is_active == True,
        Product.current_stock <= Product.min_threshold,
    ).scalar()
    out_of_stock = db.query(func.count(Product.id)).filter(
        Product.is_active == True,
        Product.current_stock == 0,
    ).scalar()
    active_alerts = db.query(func.count(Alert.id)).filter(Alert.is_active == True).scalar()

    total_value = db.query(
        func.sum(Product.current_stock * Product.unit_cost)
    ).filter(Product.is_active == True).scalar() or 0

    # Last 30 days movement totals
    since = date.today() - timedelta(days=30)
    in_qty = db.query(func.sum(StockMovement.quantity)).filter(
        StockMovement.type == MovementType.in_,
        StockMovement.movement_date >= since,
    ).scalar() or 0
    out_qty = db.query(func.sum(StockMovement.quantity)).filter(
        StockMovement.type == MovementType.out,
        StockMovement.movement_date >= since,
    ).scalar() or 0

    return {
        "total_products": total_products,
        "low_stock_count": low_stock,
        "out_of_stock_count": out_of_stock,
        "active_alerts": active_alerts,
        "total_inventory_value": float(total_value),
        "last_30_days": {
            "stock_in": int(in_qty),
            "stock_out": int(out_qty),
        },
    }
