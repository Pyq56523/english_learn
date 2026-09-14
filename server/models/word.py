"""单词表"""
from sqlalchemy import BigInteger, Column, Index, String, Text

from models.base import Base

class Word(Base):
    """单词（一词可属多本单词书，经 word_book_words 关联）"""
    __tablename__ = "words"
    __table_args__ = (
        Index("idx_words_word", "word"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    word = Column(String(100), nullable=False)
    phonetic = Column(String(100))
    meaning = Column(Text, nullable=False)
    example = Column(Text)
