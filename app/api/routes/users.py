from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.models.audit_log import AuditLog
from app.schemas.user import UserCreate, UserOut, LoginRequest, Token
from app.auth.password import hash_password, verify_password
from app.auth.jwt_handler import create_access_token
from app.auth.rbac import require_admin
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
def login(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account disabled"
        )

    token = create_access_token({
        "sub": str(user.id),
        "role": user.role.value
    })

    user.last_login = datetime.utcnow()
    db.add(AuditLog(
        user_id=user.id,
        user_email=user.email,
        action="USER_LOGIN",
        entity_type="USER",
        entity_id=str(user.id),
        ip_address=request.client.host if request.client else None,
    ))
    db.commit()

    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post(
    "/register",
    response_model=UserOut,
    dependencies=[Depends(require_admin)]
)
def register(
    payload: UserCreate,
    db: Session = Depends(get_db)
):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)