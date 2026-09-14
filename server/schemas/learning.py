"""学习 / SM-2 相关 Schema"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class StartLearningRequest(BaseModel):
    """开始学习某本单词书"""
    book_id: int


class ReviewRequest(BaseModel):
    """提交复习评分"""
    record_id: int
    quality: int = Field(..., ge=0, le=5, description="用户自评分 0-5")
    time_spent_ms: Optional[int] = Field(0, ge=0)


class ReviewResponse(BaseModel):
    """复习响应（SM-2 计算后结果）"""
    record_id: int
    word_id: int
    new_ease_factor: float
    new_interval_days: int
    next_review_at: Optional[datetime]
    status: str


class WordCard(BaseModel):
    """今日学习卡片"""
    word_id: int
    word: str
    phonetic: Optional[str]
    meaning: str
    example: Optional[str]
    # due_cards 专属字段
    record_id: Optional[int] = None
    repetition: Optional[int] = None
    interval_days: Optional[int] = None


class TodaySummary(BaseModel):
    daily_target: int
    learn_count: int    # 今日可学新词数 = min(未学总数, daily_target)
    total_new: int      # 全部未学新词数（含未分配到今日的）
    total_due: int      # 到期复习数
    mastered: int


class TodayCardsResponse(BaseModel):
    new_cards: list[WordCard]
    due_cards: list[WordCard]
    learned_cards: list[WordCard]  # 今日已学新词，供拼写练习
    summary: TodaySummary


class LearningProgressResponse(BaseModel):
    """某本书学习进度"""
    book_id: int
    total: int
    learning: int
    mastered: int
    progress_rate: float  # 0-1
