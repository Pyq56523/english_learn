"""ORM 公共基类（全项目唯一 Base，保证 FK 跨表解析）"""
from sqlalchemy.orm import declarative_base

Base = declarative_base()
