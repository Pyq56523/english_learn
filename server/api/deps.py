"""全局依赖：DB 会话、登录用户、权限"""
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from core.database import SessionLocal
from core.security import decode_token
from crud.user import user_crud
from models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_db():
    """FastAPI 依赖：请求级数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """从 Authorization: Bearer <token> 解码用户身份并返回用户对象"""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
    except (JWTError, TypeError, ValueError):
        raise credentials_exception

    user = user_crud.get(db, user_id)
    if user is None:
        raise credentials_exception
    return user


def get_current_user_id(user: User = Depends(get_current_user)) -> int:
    """仅取当前用户 ID"""
    return user.id
