"""数据库：engine / SessionLocal / 建表"""
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import MYSQL
from models.base import Base

DATABASE_URL = (
    f"mysql+pymysql://{quote_plus(MYSQL['user'])}:{quote_plus(MYSQL['password'])}"
    f"@{MYSQL['host']}:{MYSQL['port']}/{MYSQL['database']}"
    f"?charset={MYSQL['charset']}"
)

engine = create_engine(
    DATABASE_URL,
    pool_size=MYSQL.get("pool_size", 10),
    max_overflow=MYSQL.get("max_overflow", 20),
    echo=MYSQL.get("echo", False),
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def create_all_tables() -> None:
    """开发阶段快速建表（生产环境请使用 alembic 迁移）"""
    Base.metadata.create_all(bind=engine)
