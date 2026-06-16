from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.alert import Alert, AlertSeverity
from datetime import datetime, timezone


def evaluate_alerts(product: Product, db: Session):
    """Re-evaluate and upsert alert for a product after stock changes."""
    # Resolve existing active alerts for this product
    existing = db.query(Alert).filter(Alert.product_id == product.id, Alert.is_active == True).first()

    stock = product.current_stock
    threshold = product.min_threshold

    if stock == 0:
        severity = AlertSeverity.out_of_stock
    elif stock <= threshold * 0.5:
        severity = AlertSeverity.critical
    elif stock <= threshold:
        severity = AlertSeverity.low
    else:
        severity = None  # stock is healthy

    if severity is None:
        # resolve any open alert
        if existing:
            existing.is_active = False
            existing.resolved_at = datetime.now(timezone.utc)
    else:
        if existing:
            existing.severity = severity
        else:
            alert = Alert(product_id=product.id, severity=severity)
            db.add(alert)

    db.commit()
