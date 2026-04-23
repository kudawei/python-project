"""
操作日志 API
提供操作日志的记录和查询功能。
前端在用户执行关键操作（如登录、搜索、推荐、收藏、对比、导出）时调用记录接口。
"""

import json
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.operation_log import OperationLog

router = APIRouter(prefix="/oplog", tags=["操作日志"])

# 操作类型中文映射
ACTION_LABELS = {
    "login": "用户登录",
    "logout": "用户登出",
    "search": "检索查询",
    "recommend": "智能推荐",
    "favorite_add": "添加收藏",
    "favorite_remove": "取消收藏",
    "compare": "院校对比",
    "export_pdf": "导出报告",
    "view_detail": "查看详情",
    "profile_update": "更新画像",
}


@router.post("/log", summary="记录操作日志")
def add_log(
    action: str = Query(..., description="操作类型"),
    detail: Optional[str] = Query(None, description="操作详情JSON"),
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    前端在用户执行关键操作后调用此接口记录日志。
    支持的操作类型：login/search/recommend/favorite_add/favorite_remove/compare/export_pdf/view_detail
    """
    ip = request.client.host if request and request.client else None
    log = OperationLog(
        user_id=current_user.id,
        username=current_user.username,
        action=action,
        detail=detail,
        ip_address=ip,
    )
    db.add(log)
    db.commit()
    return {"msg": "操作已记录"}


@router.get("/logs", summary="查询操作日志")
def get_logs(
    action: Optional[str] = Query(None, description="操作类型筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    分页查询当前用户的操作日志，支持按操作类型筛选。
    """
    query = db.query(OperationLog).filter(OperationLog.user_id == current_user.id)
    if action:
        query = query.filter(OperationLog.action == action)

    total = query.count()
    items = (
        query.order_by(OperationLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": r.id,
                "action": r.action,
                "action_label": ACTION_LABELS.get(r.action, r.action),
                "detail": r.detail,
                "ip_address": r.ip_address,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in items
        ],
    }
