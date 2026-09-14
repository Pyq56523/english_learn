"""用户 / 认证相关 Schema"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """登录请求：支持用户名或邮箱 + 密码"""
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)


class UserCreate(BaseModel):
    """注册请求"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    captcha_id: Optional[str] = Field(None, description="验证码 id（GET /captcha 返回）")
    captcha_code: Optional[str] = Field(None, description="用户输入的验证码")


class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    username: str = Field(..., min_length=1, max_length=50)
    email: str = Field(..., description="用户邮箱")
    new_password: str = Field(..., min_length=6, max_length=128)
    captcha_id: Optional[str] = Field(None, description="验证码 id（GET /captcha 返回）")
    captcha_code: Optional[str] = Field(None, description="用户输入的验证码")


class RefreshRequest(BaseModel):
    """刷新令牌请求"""
    token: str


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    email: str
    avatar: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdateRequest(BaseModel):
    """更新个人信息（部分字段，不传则不修改）"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    avatar: Optional[str] = None
    age: Optional[int] = Field(None, ge=1, le=150)
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    bio: Optional[str] = Field(None, max_length=500)


class ChangePasswordRequest(BaseModel):
    """修改密码"""
    old_password: str = Field(..., min_length=6, max_length=128)
    new_password: str = Field(..., min_length=6, max_length=128)


class UserTokenResponse(BaseModel):
    """登录成功响应（含 Token）"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
