"""English_Leaner 应用入口

- 中间件：跨域 + 请求日志/耗时
- 全局异常处理
- 路由：api/router.py 的 api_v1_router 统一挂载到 /api/v1
- 静态资源：/uploads 头像等

启动方式（在 server 目录下）：python main.py
"""
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.router import api_router
from core.config import API_PREFIX, APP_NAME, CORS_ORIGINS, ENV, HOST, PORT
from core.database import create_all_tables
from core.exceptions import register_exception_handlers
from core.logger import get_logger
from core.middlewares import add_cors_middleware, add_request_logging_middleware

logger = get_logger("router")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    logger.info("应用启动 | env=%s host=%s port=%s", ENV, HOST, PORT)
    if ENV == "dev":
        create_all_tables()
        logger.info("dev 环境自动建表完成")
    yield
    # shutdown
    logger.info("应用关闭")


app = FastAPI(title=APP_NAME, version="1.0.0", lifespan=lifespan)

# 中间件：跨域 + 请求日志
add_cors_middleware(app, CORS_ORIGINS)
add_request_logging_middleware(app)

# 全局异常处理
register_exception_handlers(app)

# 头像等图片静态目录挂载：/uploads/avatars/xxx 可被浏览器访问
UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# 业务路由统一挂载到 /api
app.include_router(api_router, prefix=API_PREFIX)


@app.get(API_PREFIX)
def root():
    return {"app": APP_NAME, "status": "running"}

    
def root():
    return {"app": APP_NAME, "status": "running"}


def main() -> None:
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("应用启动失败")
        raise
