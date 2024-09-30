from fastapi import APIRouter, Depends, HTTPException
from src.auth.auth import current_user
from src.client_profile.models import User

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.get("/jwt/check")
async def check_auth(user: User = Depends(current_user)):
    if user is None:
        raise HTTPException(status_code=400, detail="User not found")
    return {"status": "ok"}
