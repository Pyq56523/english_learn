"""用户 / 认证接口：只做请求接收、参数校验、路由分发"""
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from api.deps import get_current_user, get_db
from models import User
from schemas.user import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshRequest,
    ResetPasswordRequest,
    UserCreate,
    UserUpdateRequest,
)
from services import user_service

router = APIRouter(tags=["auth"])


@router.post("/auth/register", summary="用户注册")
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    return user_service.register(payload, db)


@router.post("/auth/login", summary="用户登录")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    return user_service.login(payload, db)


@router.post("/auth/refresh", summary="刷新令牌")
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    """刷新令牌"""
    return user_service.refresh(payload, db)


@router.get("/auth/me", summary="当前用户")
def me(user: User = Depends(get_current_user)):
    """当前用户"""
    return user_service.me(user)


@router.put("/auth/update_me", summary="更新个人信息")
def update_me(
    payload: UserUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新个人信息"""
    return user_service.update_me(payload, user, db)


@router.post("/auth/change_password", summary="修改密码")
def change_password(
    payload: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """修改密码"""
    return user_service.change_password(payload, user, db)


@router.post("/auth/upload_avatar", summary="上传头像")
def upload_avatar(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """上传头像"""
    return user_service.save_avatar(file, user, db)


@router.post("/auth/reset_password", summary="找回密码")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    """重置密码"""
    return user_service.reset_password(payload, db)
