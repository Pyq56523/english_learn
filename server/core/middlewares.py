"""中间件：跨域 + 请求日志/耗时"""
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from core.logger import get_logger

logger = get_logger("router")


def add_cors_middleware(app: FastAPI, origins: list[str]) -> None:
    """跨域中间件（origins 来自 core.config.CORS_ORIGINS）"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def add_request_logging_middleware(app: FastAPI) -> None:
    """请求日志中间件：记录方法、路径、状态码与耗时"""

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        cost_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "%s %s → %s | %.1fms",
            request.method,
            request.url.path,
            response.status_code,
            cost_ms,
        )
        return response
