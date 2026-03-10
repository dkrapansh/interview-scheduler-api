from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def require_recruiter(current_user: User = Depends(get_current_user)):
    if current_user.role != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can access this route")
    return current_user


def require_candidate(current_user: User = Depends(get_current_user)):
    if current_user.role != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can access this route")
    return current_user