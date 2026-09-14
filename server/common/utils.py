"""通用工具函数"""
from datetime import date, datetime


def parse_date(value: str, default=None) -> date | None:
    """解析 'YYYY-MM-DD' 字符串为 date；空值/非法值返回 default"""
    if not value:
        return default
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return default
