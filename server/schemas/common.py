"""通用 DTO：分页请求 / 分页响应（统一响应体 BaseResp 在 core/response.py）"""
from typing import Generic, List, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PageQuery(BaseModel):
    """分页查询参数（查询字符串）"""
    page: int = 1
    page_size: int = 20


class PageResponse(BaseModel, Generic[T]):
    """通用分页响应"""
    total: int
    page: int
    page_size: int
    items: List[T]
