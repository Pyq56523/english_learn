"""单词书表 + 单词书-单词关联表"""
from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint

from models.base import Base

class WordBook(Base):
    """单词书"""
    __tablename__ = "word_books"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), index=True)  # CET4 / CET6 / IELTS / TOEFL / GRE
    description = Column(Text)
    word_count = Column(Integer, default=0)  # 冗余字段，加速查询
    created_at = Column(DateTime, default=datetime.now)


class WordBookWord(Base):
    """单词 ↔ 单词书 多对多关联表"""
    __tablename__ = "word_book_words"
    __table_args__ = (
        UniqueConstraint("book_id", "word_id", name="uk_book_word"),
        Index("idx_book_position", "book_id", "position"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    book_id = Column(BigInteger, ForeignKey("word_books.id"), nullable=False)
    word_id = Column(BigInteger, ForeignKey("words.id"), nullable=False)
    position = Column(Integer, nullable=False, default=0)  # 该词在书内顺序
