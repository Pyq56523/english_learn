"""用户表 + 用户设置表"""
from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint

from models.base import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)  # bcrypt 哈希
    avatar = Column(String(500), nullable=True)        # 头像 URL
    age = Column(Integer, nullable=True)                # 年龄
    gender = Column(String(10), nullable=True)         # 性别：male / female / other
    bio = Column(Text, nullable=True)                   # 个人简介
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class UserSetting(Base):
    """用户个性化设置（key-value，如每日学习目标 daily_target）"""
    __tablename__ = "user_settings"
    __table_args__ = (
        UniqueConstraint("user_id", "key", name="uk_user_setting_key"),
        Index("idx_user_setting", "user_id"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    key = Column(String(50), nullable=False)
    value = Column(String(255), nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
