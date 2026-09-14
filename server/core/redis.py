"""Redis 连接（惰性单例）：验证码存储等"""
import redis as redis_lib

from core.config import REDIS

_client = None


def get_redis() -> redis_lib.Redis:
    """获取 Redis 客户端（首次调用时创建连接）"""
    global _client
    if _client is None:
        _client = redis_lib.Redis(
            host=REDIS.get("host", "127.0.0.1"),
            port=REDIS.get("port", 6379),
            db=REDIS.get("db", 0),
            password=REDIS.get("password", None),
            decode_responses=True,
        )
    return _client
