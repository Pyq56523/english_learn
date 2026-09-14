"""用户设置相关 Schema"""
from typing import Optional

from pydantic import BaseModel, Field


class SettingsUpdateRequest(BaseModel):
    """更新用户设置"""
    daily_target: int = Field(..., ge=1, le=500)
    current_book_id: Optional[int] = None


class SettingsResponse(BaseModel):
    """用户设置响应"""
    daily_target: int
    current_book_id: Optional[int] = None
