from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import SECRET_KEY, ALGORITHM
from app.models.models import User

# Указываем FastAPI, где брать токен (URL для логина)
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)

async def get_current_user_id(
    token: str = Depends(reusable_oauth2)
) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=403, detail="Could not validate credentials")
        return int(user_id)
    except JWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")