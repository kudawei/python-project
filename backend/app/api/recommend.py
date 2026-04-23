"""
智能推荐 API
调用推荐算法服务，返回分梯度的院校推荐结果。
提供推荐历史记录查询功能。
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.recommend_log import RecommendLog
from app.schemas.recommend import RecommendRequest, RecommendResponse
from app.services.recommendation import calculate_recommendation

router = APIRouter(prefix="/recommend", tags=["智能推荐"])


@router.post("/", response_model=RecommendResponse, summary="获取智能推荐结果")
def get_recommendations(
    body: RecommendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    智能推荐接口

    业务流程：
    1. 前端传入用户选定的目标专业代码(zydm)
    2. 后端结合用户画像（意向省市、学习方式、实力自评）进行多维打分
    3. 返回冲刺/稳妥/保底三个梯度的推荐院校列表

    要求：用户必须已完成画像问卷（profile_completed=1）
    """
    result = calculate_recommendation(db=db, user=current_user, zydm=body.zydm)
    return RecommendResponse(
        sprint=result["sprint"],
        stable=result["stable"],
        safe=result["safe"],
    )


# ==================== 推荐历史 ====================


@router.get("/history", summary="获取推荐历史记录")
def get_recommend_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    分页查询当前用户的推荐历史记录。
    按推荐时间倒序排列，展示每次推荐的院校、得分、梯度等信息。
    """
    query = db.query(RecommendLog).filter(RecommendLog.user_id == current_user.id)
    total = query.count()
    items = (
        query.order_by(RecommendLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    tier_labels = {"sprint": "冲刺院校", "stable": "稳妥院校", "safe": "保底院校"}

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": r.id,
                "zydm": r.zydm,
                "dwdm": r.dwdm,
                "dwmc": r.dwmc,
                "score": r.score,
                "tier": r.tier,
                "tier_label": tier_labels.get(r.tier, r.tier or ""),
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in items
        ],
    }


@router.get("/history/summary", summary="推荐历史统计摘要")
def get_recommend_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    返回当前用户推荐历史的统计概览：
    总推荐次数、推荐过的专业数、推荐过的院校数。
    """
    base = db.query(RecommendLog).filter(RecommendLog.user_id == current_user.id)
    total_records = base.count()
    total_majors = base.with_entities(func.count(distinct(RecommendLog.zydm))).scalar() or 0
    total_universities = base.with_entities(func.count(distinct(RecommendLog.dwdm))).scalar() or 0

    return {
        "total_records": total_records,
        "total_majors": total_majors,
        "total_universities": total_universities,
    }
