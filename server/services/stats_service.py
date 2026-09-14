"""统计业务逻辑：仪表盘（按当前所选词书过滤）/ 热力图 / 连续打卡"""
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from common.utils import parse_date
from core.response import ok
from crud.record import record_crud
from crud.settings import setting_crud
from crud.word_book import word_book_word_crud
from models import WordBookWord
from schemas.stats import DashboardStats, DayStat, HeatmapData, StreakStat, TodayStat, TotalStat


# ---------- 内部工具 ----------

def user_book_id(db: Session, user_id: int) -> Optional[int]:
    """读取用户当前选择的单词书 id（后端持久化）"""
    v = setting_crud.get(db, user_id, "current_book_id")
    return int(v) if v else None


def book_word_ids(db: Session, book_id: int) -> set[int]:
    """返回某词书包含的所有 word_id"""
    rows = word_book_word_crud.list(
        db,
        filters=[WordBookWord.book_id == book_id],
    )
    return {r.word_id for r in rows}


def filter_by_book(records: list, word_ids: set[int]) -> list:
    """把 record 列表过滤到属于某词书的子集"""
    if not word_ids:
        return records
    return [r for r in records if r.word_id in word_ids]


def calc_streak(db: Session, user_id: int, word_ids: Optional[set[int]] = None) -> StreakStat:
    records = record_crud.list_by_user(db, user_id, review_only=True)
    if word_ids is None:
        records = []
    elif word_ids:
        records = filter_by_book(records, word_ids)
    active_days = {r.last_review_at.strftime("%Y-%m-%d") for r in records if r.last_review_at}

    # 当前连续（含今天或昨天）
    cursor = datetime.now().date()
    if cursor.strftime("%Y-%m-%d") not in active_days:
        cursor -= timedelta(days=1)
    current = 0
    while cursor.strftime("%Y-%m-%d") in active_days:
        current += 1
        cursor -= timedelta(days=1)

    # 最大连续
    max_streak = 0
    run = 0
    prev = None
    for day in sorted(active_days):
        d = datetime.strptime(day, "%Y-%m-%d").date()
        run = run + 1 if (prev is not None and (d - prev).days == 1) else 1
        max_streak = max(max_streak, run)
        prev = d

    return StreakStat(current_streak_days=current, max_streak_days=max_streak)


def learning_days(db: Session, user_id: int, word_ids: Optional[set[int]] = None) -> int:
    """累计学习天数（distinct 有过 last_review_at 的日期）"""
    records = record_crud.list_by_user(db, user_id, review_only=True)
    if word_ids is None:
        records = []
    elif word_ids:
        records = filter_by_book(records, word_ids)
    days = {r.last_review_at.strftime("%Y-%m-%d") for r in records if r.last_review_at}
    return len(days)


def daily_series(db: Session, user_id: int, start_date, end_date, word_ids=None) -> list:
    """返回 [start, end] 内每天的学习记录"""
    if end_date is None:
        end_date = datetime.now().date()
    if start_date is None:
        start_date = end_date - timedelta(days=6)  # 默认一周

    all_records = record_crud.list_by_user(db, user_id)
    records = (
        []
        if word_ids is None
        else filter_by_book(all_records, word_ids)
    )

    learned_by_day: dict[str, int] = {}
    reviewed_by_day: dict[str, int] = {}
    for r in records:
        if r.learned_at:
            key = r.learned_at.strftime("%Y-%m-%d")
            learned_by_day[key] = learned_by_day.get(key, 0) + 1
        if r.last_review_at:
            key = r.last_review_at.strftime("%Y-%m-%d")
            reviewed_by_day[key] = reviewed_by_day.get(key, 0) + 1

    days: list[DayStat] = []
    cursor = start_date
    while cursor <= end_date:
        key = cursor.strftime("%Y-%m-%d")
        days.append(
            DayStat(
                date=key,
                learned=learned_by_day.get(key, 0),
                reviewed=reviewed_by_day.get(key, 0),
            )
        )
        cursor += timedelta(days=1)
    return days


# ---------- 业务入口 ----------

def dashboard(start_date: str, end_date: str, user_id: int, db: Session) -> dict:
    """学习仪表盘统计（按当前所选词书过滤，未选词书时数据为 0）"""
    book_id = user_book_id(db, user_id)
    word_ids = book_word_ids(db, book_id) if book_id else None

    local_today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    all_records = record_crud.list_by_user(db, user_id)
    # 未选词书时返回空，不展示任何历史残留数据
    if word_ids is None:
        records = []
    else:
        records = filter_by_book(all_records, word_ids)

    # 今日学习（本地时区）
    today_records = [
        r for r in records
        if r.last_review_at is not None and r.last_review_at >= local_today_start
    ]
    reviewed = len(today_records)
    learned = len([r for r in today_records if r.repetition <= 1])

    # 总数
    words_total = len(records)  # 所选词书已建记录数
    words_learned = len([r for r in records if r.learned_at is not None])
    accuracy = round(learned / max(reviewed, 1), 2) if reviewed else 0.0

    result = DashboardStats(
        today=TodayStat(learned=learned, reviewed=reviewed, accuracy_rate=accuracy),
        total=TotalStat(
            words_total=words_total,
            words_learned=words_learned,
            days_total=learning_days(db, user_id, word_ids),
        ),
        streak=calc_streak(db, user_id, word_ids),
        days=daily_series(db, user_id, parse_date(start_date), parse_date(end_date), word_ids),
    )
    return ok(data=result.model_dump(mode="json"))


def heatmap(user_id: int, db: Session) -> dict:
    """近 365 天每天复习数热力图"""
    days = 365
    records = record_crud.list_by_user(
        db, user_id, since=datetime.now() - timedelta(days=days)
    )
    by_date: dict[str, int] = {}
    for r in records:
        if r.last_review_at:
            key = r.last_review_at.strftime("%Y-%m-%d")
            by_date[key] = by_date.get(key, 0) + 1

    dates: list[str] = []
    counts: list[int] = []
    for i in range(days - 1, -1, -1):
        d = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        dates.append(d)
        counts.append(by_date.get(d, 0))
    return ok(data=HeatmapData(dates=dates, counts=counts).model_dump(mode="json"))


def streak(user_id: int, db: Session) -> dict:
    """连续打卡统计（全局）"""
    return ok(data=calc_streak(db, user_id).model_dump(mode="json"))
