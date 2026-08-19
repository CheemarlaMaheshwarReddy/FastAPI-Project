from fastapi import Depends, HTTPException
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from model import User, get_db
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

SECRET_KEY = "my-secret-key"
ALGORITHM = "HS256"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    token = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return token
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db = Depends(get_db)
):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("user_id")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )
        user = db.query(User).filter(User.id == user_id).first()

        if user is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return user

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
