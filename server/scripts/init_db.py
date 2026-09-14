"""初始化脚本：创建数据表

dev 环境 main.py 启动时也会自动建表（lifespan → create_all_tables），
此脚本用于手动初始化或生产环境首次部署。

用法（server 目录下）：python scripts/init_db.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.logger import get_logger  # noqa: E402
from core.database import create_all_tables  # noqa: E402

logger = get_logger("init_db")


def main() -> None:
    create_all_tables()
    logger.info("数据表创建完成（create_all）")


if __name__ == "__main__":
    main()
