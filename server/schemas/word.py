"""单词 / 单词书相关 Schema"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class WordBookCreate(BaseModel):
    name: str
    category: str
    description: Optional[str] = None


class WordBookResponse(BaseModel):
    id: int
    name: str
    category: str
    description: Optional[str]
    word_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class WordBookDetailResponse(WordBookResponse):
    """详情 + 学习进度"""
    learned_count: int = 0
    mastered_count: int = 0


class WordResponse(BaseModel):
    """词可属多本书，不再有单一 book_id；如需书内上下文字段请另行提供"""
    id: int
    word: str
    phonetic: Optional[str]
    meaning: str
    example: Optional[str]

    model_config = {"from_attributes": True}


class WordPageResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[WordResponse]
