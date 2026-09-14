"""学习业务逻辑：今日卡片 / 开始学习 / 提交复习(SM-2) / 进度"""
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from common.constants import (
    DEFAULT_DAILY_TARGET,
    MIN_EASE_FACTOR,
    STATUS_LEARNING,
    STATUS_MASTERED,
    STATUS_NEW,
)
from core.logger import get_logger
from core.response import ok
from crud.record import record_crud
from crud.settings import setting_crud
from crud.word import word_crud
from crud.word_book import word_book_crud, word_book_word_crud
from models import UserWordRecord, WordBookWord
from schemas.learning import LearningProgressResponse, ReviewResponse, TodayCardsResponse, TodaySummary, WordCard

logger = get_logger("learning")


# ---------- SM-2 核心（纯函数，无 DB 依赖） ----------

def sm2_update(record: UserWordRecord, quality: int) -> UserWordRecord:
    """SM-2 核心计算（纯函数，便于单元测试）"""
    quality = int(quality)
    # 1. 更新难度因子 E-Factor
    record.ease_factor = max(
        MIN_EASE_FACTOR,
        record.ease_factor
        + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)),
    )

    # 2. 根据评分调整间隔
    if quality >= 3:
        if record.repetition == 0:
            record.interval_days = 1
        elif record.repetition == 1:
            record.interval_days = 6
        else:
            record.interval_days = round(record.interval_days * record.ease_factor)
        record.repetition += 1
        record.status = STATUS_MASTERED if record.repetition >= 5 else STATUS_LEARNING
    else:
        # 没记住 → 重置
        record.repetition = 0
        record.interval_days = 1
        record.status = STATUS_LEARNING

    # 3. 更新时间
    now = datetime.utcnow()
    record.last_review_at = now
    record.next_review_at = now + timedelta(days=record.interval_days)
    return record


# ---------- 内部工具 ----------

def to_word_card(db: Session, record: UserWordRecord, with_record: bool) -> WordCard:
    word = word_crud.get(db, record.word_id)
    return WordCard(
        word_id=record.word_id,
        word=word.word,
        phonetic=word.phonetic,
        meaning=word.meaning,
        example=word.example,
        record_id=record.id if with_record else None,
        repetition=record.repetition if with_record else None,
        interval_days=record.interval_days if with_record else None,
    )


def get_today_cards(db: Session, user_id: int) -> TodayCardsResponse:
    # 读取当前所选词书
    book_id_raw = setting_crud.get(db, user_id, "current_book_id")
    book_id = int(book_id_raw) if book_id_raw else None

    today = datetime.now()  # 本地时区
    day_start = today.replace(hour=0, minute=0, second=0, microsecond=0)

    # 书范围过滤
    word_ids: set[int] | None = None
    if book_id:
        rows = word_book_word_crud.list(
            db,
            filters=[WordBookWord.book_id == book_id],
        )
        word_ids = {r.word_id for r in rows}

    # 每日新学目标
    daily_target = int(
        setting_crud.get(db, user_id, "daily_target", str(DEFAULT_DAILY_TARGET))
    )

    # 所有用户记录
    all_records = record_crud.list_by_user(db, user_id)
    book_records = (
        [r for r in all_records if r.word_id in word_ids]
        if word_ids is not None else all_records
    )

    if not book_records:
        # 未选词书或词书未初始化记录
        return TodayCardsResponse(
            new_cards=[], due_cards=[], learned_cards=[],
            summary=TodaySummary(
                daily_target=daily_target,
                learn_count=0, total_new=0, total_due=0, mastered=0,
            ),
        )

    # 今日已学新词数（本地时区）
    learned_today = len([
        r for r in book_records
        if r.learned_at is not None and r.learned_at >= day_start
    ])
    remaining = max(0, daily_target - learned_today)

    new_records = (
        [r for r in book_records if r.status == STATUS_NEW]
        if word_ids is not None
        else record_crud.list_new(db, user_id, remaining)
    )
    new_records = new_records[:remaining]

    due_records = [
        r for r in book_records
        if r.next_review_at is not None and r.next_review_at <= today
    ]

    learned_cards = [
        to_word_card(db, r, True) for r in book_records
        if r.learned_at is not None and r.learned_at >= day_start
    ]

    total_new = len([r for r in book_records if r.status == STATUS_NEW])
    mastered = len([r for r in book_records if r.status == STATUS_MASTERED])

    return TodayCardsResponse(
        new_cards=[to_word_card(db, r, True) for r in new_records],
        due_cards=[to_word_card(db, r, True) for r in due_records],
        learned_cards=learned_cards,
        summary=TodaySummary(
            daily_target=daily_target,
            learn_count=len(new_records),
            total_new=total_new,
            total_due=len(due_records),
            mastered=mastered,
        ),
    )


# ---------- 业务入口 ----------

def today_cards(user_id: int, db: Session) -> dict:
    """今日学习卡片（新卡 + 到期复习卡）"""
    return ok(data=get_today_cards(db, user_id).model_dump(mode="json"))


def start_learning(payload, user_id: int, db: Session) -> dict:
    """初始化某本单词书的学习记录，返回新增条数"""
    if word_book_crud.get(db, payload.book_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "WordBook not found")

    existing = {r.word_id for r in record_crud.list_by_user(db, user_id)}
    record_list = [
        UserWordRecord(
            user_id=user_id,
            word_id=w.id,
            status=STATUS_NEW,
            ease_factor=2.5,
            interval_days=0,
            repetition=0,
        )
        for w in word_crud.list_by_book(db, payload.book_id)
        if w.id not in existing
    ]
    count = record_crud.add_all(db, record_list) if record_list else 0
    logger.info("开始学习 | user_id=%s book_id=%s 初始化=%d 条", user_id, payload.book_id, count)
    return ok(data={"initialized": count}, message="Learning started")


def review(payload, user_id: int, db: Session) -> dict:
    """提交复习评分并执行 SM-2 算法"""
    record = record_crud.get(db, payload.record_id)
    if record is None or record.user_id != user_id:
        logger.warning("复习提交失败 | user_id=%s record_id=%s 不存在或不属于自己", user_id, payload.record_id)
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Record not found")

    was_new = record.status == STATUS_NEW
    sm2_update(record, payload.quality)
    # 首次学习（从 new 转出）时记录今天，用于计算今日已学新词数
    if was_new and record.learned_at is None:
        record.learned_at = datetime.utcnow()
    record_crud.commit(db)
    result = ReviewResponse(
        record_id=record.id,
        word_id=record.word_id,
        new_ease_factor=round(record.ease_factor, 2),
        new_interval_days=record.interval_days,
        next_review_at=record.next_review_at,
        status=record.status,
    )
    logger.info("复习提交 | user_id=%s record_id=%s quality=%d word_id=%s status=%s interval=%d天",
                user_id, record.id, payload.quality, record.word_id, record.status, record.interval_days)
    return ok(data=result.model_dump(mode="json"), message="Review saved")


def get_progress(book_id: int, user_id: int, db: Session) -> dict:
    """某本书的学习进度"""
    word_ids = [w.id for w in word_crud.list_by_book(db, book_id)]
    if not word_ids:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No words in this book")

    records = record_crud.list_in_book(db, user_id, word_ids)
    learning = len([r for r in records if r.status == STATUS_LEARNING])
    mastered = len([r for r in records if r.status == STATUS_MASTERED])
    result = LearningProgressResponse(
        book_id=book_id,
        total=len(word_ids),
        learning=learning,
        mastered=mastered,
        progress_rate=round((learning + mastered) / len(word_ids), 2),
    )
    return ok(data=result.model_dump(mode="json"))
