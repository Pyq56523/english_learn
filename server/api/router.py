"""总路由聚合：/api/v1 下所有接口统一挂载"""
from fastapi import APIRouter

from api import captcha, learning, settings, stats, user, word, word_book

api_router = APIRouter()

# 认证 + 验证码
api_router.include_router(user.router)
api_router.include_router(captcha.router)
# 单词 / 单词书
api_router.include_router(word.router)
api_router.include_router(word_book.router)
# 学习 / 设置 / 统计
api_router.include_router(learning.router)
api_router.include_router(settings.router)
api_router.include_router(stats.router)
