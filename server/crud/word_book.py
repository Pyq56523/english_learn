"""单词书数据操作"""
from typing import List, Optional

from sqlalchemy.orm import Session

from crud.base import CrudBase
from models import WordBook, WordBookWord


class WordBookCrud(CrudBase):
    """单词书 Repository"""
    model = WordBook

    def list(self, db: Session, category: Optional[str] = None) -> List[WordBook]:
        filters = ([WordBook.category == category] if category else [])
        return super().list(db, filters=filters)

    def add_word(self, db: Session, book_id: int, word_id: int, position: int) -> WordBookWord:
        """把词加入某书（写关联表）并递增 word_books.word_count"""
        rel = WordBookWord(book_id=book_id, word_id=word_id, position=position)
        db.add(rel)
        book = db.get(WordBook, book_id)
        if book is not None:
            book.word_count += 1
        db.commit()
        db.refresh(rel)
        return rel


class WordBookWordCrud(CrudBase):
    """单词书-单词关联表 Repository（学习/统计按书取词用）"""
    model = WordBookWord


word_book_crud = WordBookCrud()
word_book_word_crud = WordBookWordCrud()
