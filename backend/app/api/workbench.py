"""
我的工作台 API
提供收藏夹管理和院校横向对比功能。
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.favorite import Favorite
from app.models.major_university import MajorUniversity
from app.models.major_detail import MajorDetail
from app.schemas.favorite import FavoriteCreate, FavoriteItem, CompareRequest, CompareItem

router = APIRouter(prefix="/workbench", tags=["我的工作台"])


# ==================== 收藏夹管理 ====================


@router.get("/favorites", response_model=list[FavoriteItem], summary="获取我的收藏列表")
def get_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前用户的所有收藏记录"""
    items = (
        db.query(Favorite)
        .filter(Favorite.user_id == current_user.id)
        .order_by(Favorite.created_at.desc())
        .all()
    )
    return [FavoriteItem.model_validate(item) for item in items]


@router.post("/favorites", summary="添加收藏")
def add_favorite(
    body: FavoriteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    添加院校-专业到收藏夹
    同一用户不能重复收藏同一院校同一专业。
    """
    # 检查是否已收藏
    existing = (
        db.query(Favorite)
        .filter(
            Favorite.user_id == current_user.id,
            Favorite.dwdm == body.dwdm,
            Favorite.zydm == body.zydm,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该院校专业已在收藏夹中",
        )

    fav = Favorite(
        user_id=current_user.id,
        dwdm=body.dwdm,
        dwmc=body.dwmc,
        zydm=body.zydm,
        zymc=body.zymc,
    )
    db.add(fav)
    db.commit()
    return {"message": "收藏成功"}


@router.delete("/favorites/{favorite_id}", summary="取消收藏")
def remove_favorite(
    favorite_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """根据收藏记录ID取消收藏"""
    fav = (
        db.query(Favorite)
        .filter(Favorite.id == favorite_id, Favorite.user_id == current_user.id)
        .first()
    )
    if not fav:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="收藏记录不存在",
        )
    db.delete(fav)
    db.commit()
    return {"message": "取消收藏成功"}


@router.get("/favorites/check", summary="检查是否已收藏")
def check_favorite(
    dwdm: str = Query(..., description="院校代码"),
    zydm: str = Query(..., description="专业代码"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """检查用户是否已收藏指定院校专业"""
    existing = (
        db.query(Favorite)
        .filter(
            Favorite.user_id == current_user.id,
            Favorite.dwdm == dwdm,
            Favorite.zydm == zydm,
        )
        .first()
    )
    return {"is_favorited": existing is not None, "favorite_id": existing.id if existing else None}


@router.get("/favorites/batch_check", summary="批量检查收藏状态")
def batch_check_favorites(
    zydm: str = Query(..., description="专业代码"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    批量返回当前用户在指定专业下已收藏的所有院校代码。
    前端可用于标记检索结果中的已收藏项。
    """
    favorites = (
        db.query(Favorite.dwdm)
        .filter(Favorite.user_id == current_user.id, Favorite.zydm == zydm)
        .all()
    )
    return {"favorited_dwdm_list": [f[0] for f in favorites]}


# ==================== 院校横向对比 ====================


@router.post("/compare", response_model=list[CompareItem], summary="院校横向对比")
def compare_universities(
    body: CompareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    院校PK（横向对比）
    用户选择 2-3 个院校代码和一个专业代码，
    返回这几所院校在该专业下的详细属性对比数据。

    优先从 major_detail 表获取详细信息，
    若该表无数据则回退到 major_university 表。
    """
    if len(body.dwdm_list) < 2 or len(body.dwdm_list) > 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请选择 2-3 个院校进行对比",
        )

    results: list[CompareItem] = []

    for dwdm in body.dwdm_list:
        # 优先从详情表获取
        detail = (
            db.query(MajorDetail)
            .filter(MajorDetail.dwdm == dwdm, MajorDetail.zydm == body.zydm)
            .first()
        )

        if detail:
            results.append(CompareItem(
                dwdm=detail.dwdm,
                dwmc=detail.dwmc,
                szss=detail.szss,
                zhx=detail.zhx,
                bs=detail.bs,
                syl=detail.syl,
                xxfs="全日制" if detail.xxfs == "1" else ("非全日制" if detail.xxfs == "2" else detail.xxfs),
                tydxs=detail.tydxs,
                jsggjh=detail.jsggjh,
                zydm=detail.zydm,
                zymc=detail.zymc,
                b985=detail.b985,
                b211=detail.b211,
                yjsy=detail.yjsy,
                yxsmc=detail.yxsmc,
                yjfxmc=detail.yjfxmc,
                zdjs=detail.zdjs,
                nzsrs=detail.nzsrs,
                km1mc=detail.km1mc,
                km2mc=detail.km2mc,
                km3mc=detail.km3mc,
                km4mc=detail.km4mc,
            ))
        else:
            # 回退到关联表
            mu = (
                db.query(MajorUniversity)
                .filter(MajorUniversity.dwdm == dwdm, MajorUniversity.zydm == body.zydm)
                .first()
            )
            if mu:
                results.append(CompareItem(
                    dwdm=mu.dwdm,
                    dwmc=mu.dwmc,
                    szss=mu.szss,
                    zhx=mu.zhx,
                    bs=mu.bs,
                    syl=mu.syl,
                    xxfs=mu.xxfs,
                    tydxs=mu.tydxs,
                    jsggjh=mu.jsggjh,
                    zydm=mu.zydm,
                    zymc=mu.zymc,
                ))

    return results
