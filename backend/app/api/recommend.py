"""
智能推荐 API
调用推荐算法服务，返回分梯度的院校推荐结果。
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
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
