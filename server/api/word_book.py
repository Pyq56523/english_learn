"""单词书接口：只做请求接收、参数校验、路由分发"""
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_current_user, get_db
from models import User
from services import word_book_service

router = APIRouter(tags=["word-books"])


@router.get("/word-books", summary="单词书列表")
def list_books(category: Optional[str] = None, db: Session = Depends(get_db)):
    """单词书列表：可选按分类过滤"""
    return word_book_service.list_books(category, db)


@router.get("/word-books/{book_id}", summary="单词书详情含进度")
def get_book(
    book_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """单词书详情 + 当前用户学习进度"""
    return word_book_service.get_book(book_id, user.id, db)
