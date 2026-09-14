"""单词数据操作"""
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from crud.base import CrudBase
from models import Word, WordBookWord


class WordCrud(CrudBase):
    """单词 Repository：列表/计数支持按书（经关联表）与关键词过滤"""
    model = Word

    def list_filtered(
        self,
        db: Session,
        book_id: Optional[int] = None,
        keyword: Optional[str] = None,
        offset: int = 0,
        limit: Optional[int] = None,
    ) -> List[Word]:
        q = db.query(Word)
        if book_id:
            q = q.join(WordBookWord, WordBookWord.word_id == Word.id).filter(WordBookWord.book_id == book_id)
        if keyword:
            q = q.filter(Word.word.like(f"%{keyword}%"))
        if limit is not None:
            q = q.offset(offset).limit(limit)
        return list(q.all())

    def count_filtered(
        self,
        db: Session,
        book_id: Optional[int] = None,
        keyword: Optional[str] = None,
    ) -> int:
        q = db.query(func.count()).select_from(Word)
        if book_id:
            q = q.join(WordBookWord, WordBookWord.word_id == Word.id).filter(WordBookWord.book_id == book_id)
        if keyword:
            q = q.filter(Word.word.like(f"%{keyword}%"))
        return q.scalar()

    def list_by_book(self, db: Session, book_id: int) -> List[Word]:
        """取某书全部词，经 word_book_words 关联并按 position 排序"""
        return list(
            db.query(Word)
            .join(WordBookWord, WordBookWord.word_id == Word.id)
            .filter(WordBookWord.book_id == book_id)
            .order_by(WordBookWord.position)
            .all()
        )

    def count_by_book(self, db: Session, book_id: int) -> int:
        return self.count(db, [WordBookWord.book_id == book_id])


word_crud = WordCrud()
