"""用户单词学习记录表（SM-2 算法核心表）"""
from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Enum, Float, ForeignKey, Index, Integer, UniqueConstraint

from common.constants import (
    DEFAULT_EASE_FACTOR,
    STATUS_LEARNING,
    STATUS_MASTERED,
    STATUS_NEW,
)
from models.base import Base

class UserWordRecord(Base):
    """用户单词学习记录"""
    __tablename__ = "user_word_records"
    __table_args__ = (
        UniqueConstraint("user_id", "word_id", name="uk_user_word"),
        Index("idx_user_next_review", "user_id", "next_review_at"),
        Index("idx_user_status", "user_id", "status"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    word_id = Column(BigInteger, ForeignKey("words.id"), nullable=False)
    status = Column(
        Enum(STATUS_NEW, STATUS_LEARNING, STATUS_MASTERED, name="record_status"),
        default=STATUS_NEW,
        nullable=False,
    )
    ease_factor = Column(Float, default=DEFAULT_EASE_FACTOR, nullable=False)
    interval_days = Column(Integer, default=0, nullable=False)
    repetition = Column(Integer, default=0, nullable=False)
    next_review_at = Column(DateTime, index=True)
    last_review_at = Column(DateTime)
    learned_at = Column(DateTime, nullable=True)  # 首次学习（从 new 转出）时间，用于统计今日新学
    created_at = Column(DateTime, default=datetime.now)
