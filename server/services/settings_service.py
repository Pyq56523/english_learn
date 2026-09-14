"""用户设置业务逻辑：读取 / 更新（按用户持久化到后端）"""
from sqlalchemy.orm import Session

from common.constants import DEFAULT_DAILY_TARGET
from core.logger import get_logger
from core.response import ok
from crud.settings import setting_crud
from schemas.settings import SettingsResponse

logger = get_logger("settings")


def get_settings(user_id: int, db: Session) -> dict:
    """读取当前用户设置"""
    daily_target = int(
        setting_crud.get(db, user_id, "daily_target", str(DEFAULT_DAILY_TARGET))
    )
    current_book_id = setting_crud.get(db, user_id, "current_book_id")
    return ok(
        data=SettingsResponse(
            daily_target=daily_target,
            current_book_id=int(current_book_id) if current_book_id else None,
        ).model_dump(mode="json")
    )


def update_settings(payload, user_id: int, db: Session) -> dict:
    """更新当前用户设置（仅写传入的字段）"""
    setting_crud.set(db, user_id, "daily_target", str(payload.daily_target))
    if payload.current_book_id is not None:
        setting_crud.set(db, user_id, "current_book_id", str(payload.current_book_id))
    logger.info("用户设置更新 | user_id=%s daily_target=%s book_id=%s",
                user_id, payload.daily_target, payload.current_book_id)
    return ok(
        data=SettingsResponse(
            daily_target=payload.daily_target,
            current_book_id=payload.current_book_id,
        ).model_dump(mode="json"),
        message="Settings saved",
    )
