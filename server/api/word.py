"""单词接口：只做请求接收、参数校验、路由分发"""
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_db
from services import word_service

router = APIRouter(tags=["words"])


@router.get("/words", summary="单词列表")
def list_words(
    book_id: Optional[int] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    """单词列表：按书 / 关键词过滤、分页"""
    return word_service.list_words(book_id, keyword, page, page_size, db)


@router.get("/words/{word_id}", summary="单词详情")
def get_word(word_id: int, db: Session = Depends(get_db)):
    """单词详情"""
    return word_service.get_word(word_id, db)
