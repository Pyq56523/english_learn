"""按业务分类 + 按日期分层的日志工具

目录结构：
    server/log/20260906/router.log
    server/log/20260906/user.log

自动清理 14 天前的过期日志目录。

用法：
    from core.logger import get_logger
    logger = get_logger("user")
    logger.info("登录成功 | user_id=%s", 1)
"""
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "log"
LOG_DIR.mkdir(parents=True, exist_ok=True)

_FMT = logging.Formatter(
    "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
)

_loggers: dict[str, logging.Logger] = {}


def _clean_old_logs():
    """删除 14 天前的日志目录"""
    cutoff = datetime.now().date() - timedelta(days=14)
    for d in LOG_DIR.iterdir():
        if not d.is_dir() or len(d.name) != 8 or not d.name.isdigit():
            continue
        try:
            day = datetime.strptime(d.name, "%Y%m%d").date()
            if day < cutoff:
                shutil.rmtree(d, ignore_errors=True)
        except (ValueError, OSError):
            continue


# 模块加载时清理一次
_clean_old_logs()


def _get_log_path(category: str) -> Path:
    now = datetime.now()
    day_dir = LOG_DIR / now.strftime("%Y%m%d")
    return day_dir / f"{category}.log"


def get_logger(category: str) -> logging.Logger:
    """获取按业务分类的 logger（幂等，首次调用时配置）"""
    if category in _loggers:
        return _loggers[category]

    logger = logging.getLogger(category)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # 文件 handler：按 log/YYYYMMDD/<category>.log 写入
    log_path = _get_log_path(category)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(_FMT)
    logger.addHandler(file_handler)

    # 控制台 handler：开发期方便看（只输出 INFO 及以上，避免刷屏）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(_FMT)
    logger.addHandler(console_handler)

    _loggers[category] = logger
    return logger
