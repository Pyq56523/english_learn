"""用户设置接口：只做请求接收、参数校验、路由分发"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_current_user, get_db
from models import User
from schemas.settings import SettingsUpdateRequest
from services import settings_service

router = APIRouter(tags=["settings"])


@router.get("/settings", summary="读取用户设置")
def get_settings(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """读取当前用户设置"""
    return settings_service.get_settings(user.id, db)


@router.put("/settings", summary="更新用户设置")
def update_settings(
    payload: SettingsUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新当前用户设置（仅写传入的字段）"""
    return settings_service.update_settings(payload, user.id, db)
