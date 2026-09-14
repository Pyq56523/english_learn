"""统一业务异常 + 全局异常处理器

- BusinessException：业务可预知异常（响应格式与 FastAPI 默认一致，前端兼容）
- register_exception_handlers：统一错误响应（保留 {"detail": ...} 格式）
"""
import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("core.exceptions")


class BusinessException(HTTPException):
    """业务异常（status_code + message + code）"""

    def __init__(self, status_code: int = 400, message: str = "Business error", code: int = 1):
        super().__init__(status_code=status_code, detail=message)
        self.code = code
        self.error_message = message


def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器（含请求日志）"""

    @app.exception_handler(BusinessException)
    async def business_exc_handler(request: Request, exc: BusinessException):
        logger.warning("%s %s → %s: %s", request.method, request.url.path, exc.status_code, exc.error_message)
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.code, "data": None, "message": exc.error_message},
            mode="json",
        )

    @app.exception_handler(HTTPException)
    async def http_exc_handler(request: Request, exc: HTTPException):
        logger.warning("%s %s → %s: %s", request.method, request.url.path, exc.status_code, exc.detail)
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail}, mode="json")

    @app.exception_handler(Exception)
    async def unhandled_exc_handler(request: Request, exc: Exception):
        logger.exception("未捕获异常 | %s %s", request.method, request.url.path)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"}, mode="json")
