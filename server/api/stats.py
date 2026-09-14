"""统计接口：只做请求接收、参数校验、路由分发"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_current_user, get_db
from models import User
from services import stats_service

router = APIRouter(tags=["stats"])


@router.get("/stats/dashboard", summary="学习仪表盘")
def dashboard(
    start_date: str = "",
    end_date: str = "",
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """学习仪表盘统计（按当前所选词书过滤）"""
    return stats_service.dashboard(start_date, end_date, user.id, db)


@router.get("/stats/heatmap", summary="学习热力图")
def heatmap(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """近 365 天每天复习数热力图"""
    return stats_service.heatmap(user.id, db)


@router.get("/stats/streak", summary="连续打卡")
def streak(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """连续打卡统计（全局）"""
    return stats_service.streak(user.id, db)
