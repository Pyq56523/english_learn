"""安全工具：JWT 生成/验证 + bcrypt 密码哈希"""
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

from core.config import JWT_ALGORITHM, JWT_EXPIRE_DAYS, JWT_SECRET_KEY

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id, expires_delta: Optional[timedelta] = None) -> str:
    """签发 JWT：sub 为用户 ID，exp 为过期时间"""
    expire = datetime.now() + (expires_delta or timedelta(days=JWT_EXPIRE_DAYS))
    to_encode = {"sub": str(user_id), "exp": expire}
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """校验并解码 JWT（签名错误/过期会抛 JWTError）"""
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
