from fastapi import Depends, HTTPException, status
from app.dependencies import get_current_user
from app.models.user import User, UserRole


def require_role(*roles: UserRole):
    def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required: {[r.value for r in roles]}",
            )
        return current_user
    return _check


require_admin = require_role(UserRole.ADMIN)
require_analyst = require_role(UserRole.ADMIN, UserRole.ANALYST, UserRole.CO)
require_co = require_role(UserRole.ADMIN, UserRole.CO)