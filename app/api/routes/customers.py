from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.customer import Customer
from app.models.audit_log import AuditLog
from app.schemas.customer import CustomerCreate, CustomerOut
from app.utils.csv_parser import parse_csv
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post("/upload-csv")
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files accepted")

    contents = await file.read()
    customers_data, errors = parse_csv(contents, source="CSV")

    db_customers = []
    for c in customers_data:
        db_customer = Customer(**c.model_dump())
        db.add(db_customer)
        db_customers.append(db_customer)

    db.add(AuditLog(
        user_id=current_user.id,
        user_email=current_user.email,
        action="CSV_UPLOAD",
        entity_type="CUSTOMER_BATCH",
        details={
            "filename": file.filename,
            "imported": len(customers_data),
            "errors": len(errors)
        },
    ))
    db.commit()

    return {
        "imported": len(customers_data),
        "errors": len(errors),
        "error_details": errors[:20],
        "customer_ids": [str(c.id) for c in db_customers],
    }


@router.post("", response_model=CustomerOut)
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = Customer(**payload.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return CustomerOut.model_validate(customer)


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(
    customer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = db.query(Customer).filter(
        Customer.id == customer_id
    ).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return CustomerOut.model_validate(customer)


@router.get("", response_model=list[CustomerOut])
def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customers = db.query(Customer).offset(skip).limit(limit).all()
    return [CustomerOut.model_validate(c) for c in customers]