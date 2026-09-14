"""单词业务逻辑：分页搜索 / 详情"""
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from core.response import ok
from crud.word import word_crud
from schemas.word import WordPageResponse, WordResponse


def list_words(
    book_id: Optional[int],
    keyword: Optional[str],
    page: int,
    page_size: int,
    db: Session,
) -> dict:
    """单词列表：按书 / 关键词过滤、分页"""
    total = word_crud.count_filtered(db, book_id, keyword)
    words = word_crud.list_filtered(db, book_id, keyword, offset=(page - 1) * page_size, limit=page_size)
    items = [WordResponse.model_validate(w).model_dump(mode="json") for w in words]
    result = WordPageResponse(total=total, page=page, page_size=page_size, items=items)
    return ok(data=result.model_dump(mode="json"))


def get_word(word_id: int, db: Session) -> dict:
    """单词详情"""
    word = word_crud.get(db, word_id)
    if word is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Word not found")
    return ok(data=WordResponse.model_validate(word).model_dump(mode="json"))
