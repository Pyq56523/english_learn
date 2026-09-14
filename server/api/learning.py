"""学习接口：只做请求接收、参数校验、路由分发"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_current_user, get_db
from models import User
from schemas.learning import ReviewRequest, StartLearningRequest
from services import learning_service

router = APIRouter(tags=["learning"])


@router.get("/learning/today", summary="今日学习卡片")
def today_cards(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """今日学习卡片（新卡 + 到期复习卡）"""
    return learning_service.today_cards(user.id, db)


@router.post("/learning/start", summary="开始学习")
def start_learning(
    payload: StartLearningRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """开始学习：初始化某本单词书的学习记录"""
    return learning_service.start_learning(payload, user.id, db)


@router.post("/learning/review", summary="提交复习")
def review(
    payload: ReviewRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """提交复习评分并执行 SM-2 算法"""
    return learning_service.review(payload, user.id, db)


@router.get("/learning/progress/{book_id}", summary="学习进度")
def get_progress(
    book_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """某本书的学习进度"""
    return learning_service.get_progress(book_id, user.id, db)
