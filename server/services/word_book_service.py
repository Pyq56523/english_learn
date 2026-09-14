"""单词书业务逻辑：列表 / 详情含学习进度"""
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from core.response import ok
from crud.record import record_crud
from crud.word import word_crud
from crud.word_book import word_book_crud
from schemas.word import WordBookDetailResponse, WordBookResponse


def list_books(category: Optional[str], db: Session) -> dict:
    """单词书列表：可选按分类过滤"""
    books = word_book_crud.list(db, category)
    return ok(data=[WordBookResponse.model_validate(b).model_dump(mode="json") for b in books])


def get_book(book_id: int, user_id: int, db: Session) -> dict:
    """单词书详情 + 当前用户学习进度"""
    book = word_book_crud.get(db, book_id)
    if book is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "WordBook not found")

    detail = WordBookDetailResponse.model_validate(book)
    word_ids = [w.id for w in word_crud.list_by_book(db, book_id)]
    if word_ids:
        records = record_crud.list_in_book(db, user_id, word_ids)
        detail.learned_count = len([r for r in records if r.status != "new"])
        detail.mastered_count = len([r for r in records if r.status == "mastered"])
    return ok(data=detail.model_dump(mode="json"))
