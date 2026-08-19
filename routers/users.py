from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from model import get_db, User
from utils import pwd_context
from jose import jwt
from datetime import datetime, timedelta, timezone
from auth import create_access_token
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter()

class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str

@router.post("/login")
def login(user: OAuth2PasswordRequestForm = Depends(),
    db = Depends(get_db)
):
    db_user = db.query(User).filter(User.email == user.username
                                    ).first()
    if db_user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
            )
    password_correct = pwd_context.verify(
        user.password,
        db_user.password
    )
    if not password_correct:
        raise HTTPException(
        status_code=401,
        detail="Invalid credentials"
        )
    token = create_access_token({
        "user_id": db_user.id
    })
    return {
        "access_token": token,
        "token_type": "bearer"
    }
