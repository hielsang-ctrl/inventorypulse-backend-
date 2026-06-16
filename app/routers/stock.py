from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.database import get_db
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.stock_movement import StockMovement, MovementType
from app.schemas.stock import StockInCreate, StockOutCreate, StockMovementResponse
from app.dependencies import get_current_user
from app.models.user import User
from app.services.alert_service import evaluate_alerts

router = APIRouter(prefix="/stock", tags=["stock"])


@router.get("/movements", response_model=List[StockMovementResponse])
def list_movements(
    product_id: Optional[int] = Query(None),
    type: Optional[MovementType] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(StockMovement)
    if product_id:
        q = q.filter(StockMovement.product_id == product_id)
    if type:
        q = q.filter(StockMovement.type == type)
    if from_date:
        q = q.filter(StockMovement.movement_date >= from_date)
    if to_date:
        q = q.filter(StockMovement.movement_date <= to_date)
    return q.order_by(StockMovement.movement_date.desc()).all()


@router.post("/in", response_model=StockMovementResponse, status_code=status.HTTP_201_CREATED)
def stock_in(body: StockInCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == body.product_id, Product.is_active == True).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    supplier = db.query(Supplier).filter(Supplier.id == body.supplier_id, Supplier.is_active == True).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    if body.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")

    movement = StockMovement(
        product_id=body.product_id,
        supplier_id=body.supplier_id,
        type=MovementType.in_,
        quantity=body.quantity,
        unit_cost=body.unit_cost,
        movement_date=body.movement_date,
        created_by=current_user.id,
    )
    product.current_stock += body.quantity
    db.add(movement)
    db.commit()
    db.refresh(movement)
    evaluate_alerts(product, db)
    return movement


@router.post("/out", response_model=StockMovementResponse, status_code=status.HTTP_201_CREATED)
def stock_out(body: StockOutCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == body.product_id, Product.is_active == True).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if body.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")
    if product.current_stock < body.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    movement = StockMovement(
        product_id=body.product_id,
        type=MovementType.out,
        quantity=body.quantity,
        reason=body.reason,
        movement_date=body.movement_date,
        created_by=current_user.id,
    )
    product.current_stock -= body.quantity
    db.add(movement)
    db.commit()
    db.refresh(movement)
    evaluate_alerts(product, db)
    return movement
