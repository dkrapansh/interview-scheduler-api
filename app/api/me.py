from fastapi import APIRouter, Depends

from app.api.deps import get_current_user

router = APIRouter(prefix="/me", tags=["Me"])

@router.get("/")
def get_me(current_user = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "full_name": current_user.full_name, 
        "email": current_user.email,
        "role": current_user.role
    }