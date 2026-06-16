from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.database import get_db
from app.models.alert import Alert
from app.models.product import Product
from app.schemas.alert import AlertResponse
from app.dependencies import get_current_user, require_admin
from app.models.user import User
from datetime import datetime, timezone

router = APIRouter(prefix="/alerts", tags=["alerts"])


def _build_alert_response(alert: Alert) -> dict:
    p: Product = alert.product
    shortage = max(0, p.min_threshold - p.current_stock)
    return {
        "id": alert.id,
        "product_id": p.id,
        "product_name": p.name,
        "product_sku": p.sku,
        "current_stock": p.current_stock,
        "min_threshold": p.min_threshold,
        "shortage": shortage,
        "severity": alert.severity,
        "is_active": alert.is_active,
        "triggered_at": alert.triggered_at,
        "resolved_at": alert.resolved_at,
    }


@router.get("", response_model=List[AlertResponse])
def list_alerts(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    alerts = (
        db.query(Alert)
        .options(joinedload(Alert.product))
        .filter(Alert.is_active == True)
        .order_by(Alert.triggered_at.desc())
        .all()
    )
    return [_build_alert_response(a) for a in alerts]


@router.post("/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(alert_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    alert = db.query(Alert).options(joinedload(Alert.product)).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.is_active = False
    alert.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(alert)
    return _build_alert_response(alert)
