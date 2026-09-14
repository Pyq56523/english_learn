"""统计相关 Schema"""
from pydantic import BaseModel


class TodayStat(BaseModel):
    learned: int = 0
    reviewed: int = 0
    accuracy_rate: float = 0.0


class TotalStat(BaseModel):
    words_total: int = 0    # 所选词书单词总数（学习目标）
    words_learned: int = 0  # 已学（learned_at 已标记）
    words_mastered: int = 0
    days_total: int = 0     # 累计学习天数


class DayStat(BaseModel):
    """某一天的学习记录"""
    date: str
    learned: int  # 当天新学
    reviewed: int  # 当天学习/复习总数


class StreakStat(BaseModel):
    current_streak_days: int = 0
    max_streak_days: int = 0


class DashboardStats(BaseModel):
    today: TodayStat
    total: TotalStat
    streak: StreakStat
    days: list[DayStat]


class HeatmapData(BaseModel):
    """近 365 天学习热力图"""
    dates: list[str]      # ISO 日期
    counts: list[int]     # 对应学习数
