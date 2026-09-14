"""状态常量与 SM-2 初始参数（与 ORM 解耦，供 service / schema 使用）"""
STATUS_NEW = "new"
STATUS_LEARNING = "learning"
STATUS_MASTERED = "mastered"

# SM-2 初始参数
DEFAULT_EASE_FACTOR = 2.5
DEFAULT_INTERVAL_DAYS = 0
DEFAULT_REPETITION = 0
MIN_EASE_FACTOR = 1.3

# 每日新学单词数（学习计划默认值）
DEFAULT_DAILY_TARGET = 20
