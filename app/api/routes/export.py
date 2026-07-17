"""
VIGIL — CSV/Excel Export
GET /export/alerts → CSV of all customers with alerts
"""
import io
import csv
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.alert import Alert
from app.models.customer import Customer
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/export", tags=["Export"])


@router.get("/alerts")
def export_alerts_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export all alerts with customer info as CSV."""
    alerts = db.query(Alert).order_by(Alert.match_score.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Customer Name", "Customer ID", "PAN", "Nationality",
        "Score", "Risk Level", "Alert Type", "Status",
        "Params Matched", "Created At"
    ])

    for alert in alerts:
        customer = db.query(Customer).filter(
            Customer.id == alert.customer_id
        ).first()

        writer.writerow([
            customer.full_name if customer else "Unknown",
            str(alert.customer_id),
            customer.pan if customer else "",
            customer.nationality if customer else "",
            alert.match_score,
            alert.risk_level.value if alert.risk_level else "",
            alert.alert_type or "",
            alert.status.value if alert.status else "",
            alert.params_matched,
            str(alert.created_at),
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=VIGIL-Alerts-Export.csv"}
    )