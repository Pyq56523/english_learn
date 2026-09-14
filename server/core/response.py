"""统一全局响应结构体：BaseResp + ok()（响应格式 {code, data, message}）"""
from typing import Any

from pydantic import BaseModel


class BaseResp(BaseModel):
    """统一响应体"""
    code: int = 0
    data: Any = None
    message: str = "ok"


def ok(data: Any = None, message: str = "ok") -> dict:
    """统一成功响应"""
    return BaseResp(code=0, data=data, message=message).model_dump(mode="json")
