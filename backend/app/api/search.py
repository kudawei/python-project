"""
考研专业与院校多维检索 API
提供级联筛选器数据和高级过滤检索接口。
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from typing import Optional

from app.core.database import get_db
from app.models.major import Major
from app.models.major_university import MajorUniversity
from app.schemas.search import CascadeOption, UniversityItem, SearchResponse

router = APIRouter(prefix="/search", tags=["多维检索"])


@router.get("/categories", response_model=list[CascadeOption], summary="获取门类列表")
def get_categories(db: Session = Depends(get_db)):
    """
    获取所有门类 —— 级联选择器第一级
    从 major 表中查询去重的门类信息。
    """
    rows = (
        db.query(distinct(Major.mldm), Major.mlmc)
        .filter(Major.mldm.isnot(None))
        .order_by(Major.mldm)
        .all()
    )
    return [CascadeOption(value=r[0], label=r[1] or r[0]) for r in rows]


@router.get("/disciplines", response_model=list[CascadeOption], summary="获取一级学科列表")
def get_disciplines(mldm: str = Query(..., description="门类代码"), db: Session = Depends(get_db)):
    """
    根据门类代码获取一级学科列表 —— 级联选择器第二级
    """
    rows = (
        db.query(distinct(Major.yjxkdm), Major.yjxkmc)
        .filter(Major.mldm == mldm, Major.yjxkdm.isnot(None))
        .order_by(Major.yjxkdm)
        .all()
    )
    return [CascadeOption(value=r[0], label=r[1] or r[0]) for r in rows]


@router.get("/majors", response_model=list[CascadeOption], summary="获取专业列表")
def get_majors(yjxkdm: str = Query(..., description="一级学科代码"), db: Session = Depends(get_db)):
    """
    根据一级学科代码获取专业列表 —— 级联选择器第三级
    """
    rows = (
        db.query(distinct(Major.zydm), Major.zymc)
        .filter(Major.yjxkdm == yjxkdm, Major.zydm.isnot(None))
        .order_by(Major.zydm)
        .all()
    )
    return [CascadeOption(value=r[0], label=r[1] or r[0]) for r in rows]


@router.get("/provinces", response_model=list[CascadeOption], summary="获取省市列表")
def get_provinces(db: Session = Depends(get_db)):
    """
    获取所有省市选项 —— 用于高级过滤面板的省市筛选
    """
    rows = (
        db.query(distinct(MajorUniversity.szss))
        .filter(MajorUniversity.szss.isnot(None))
        .order_by(MajorUniversity.szss)
        .all()
    )
    return [CascadeOption(value=r[0], label=r[0]) for r in rows]


@router.get("/universities", response_model=SearchResponse, summary="高级检索院校列表")
def search_universities(
    zydm: str = Query(..., description="专业代码"),
    szss: Optional[str] = Query(None, description="省市名称，多个用逗号分隔"),
    syl: Optional[bool] = Query(None, description="仅看双一流"),
    zhx: Optional[bool] = Query(None, description="仅看自划线"),
    bs: Optional[bool] = Query(None, description="仅看有博士点"),
    xxfs: Optional[str] = Query(None, description="学习方式: 全日制/非全日制"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
):
    """
    高级检索接口
    根据专业代码和多种筛选条件查询匹配的院校列表，支持分页。

    筛选逻辑：
    1. 必选条件：专业代码(zydm)
    2. 可选条件：省市、双一流、自划线、博士点、学习方式
    3. 结果分页返回
    """
    # 构建基础查询
    query = db.query(MajorUniversity).filter(MajorUniversity.zydm == zydm)

    # 省市过滤（支持多选，前端以逗号分隔传入）
    if szss:
        province_list = [p.strip() for p in szss.split(",") if p.strip()]
        if province_list:
            query = query.filter(MajorUniversity.szss.in_(province_list))

    # 特性过滤：仅看双一流
    if syl:
        query = query.filter(MajorUniversity.syl == "是")

    # 特性过滤：仅看自划线
    if zhx:
        query = query.filter(MajorUniversity.zhx == "是")

    # 特性过滤：仅看有博士点
    if bs:
        query = query.filter(MajorUniversity.bs == "是")

    # 学习方式过滤
    if xxfs:
        query = query.filter(MajorUniversity.xxfs.contains(xxfs))

    # 计算总数
    total = query.count()

    # 分页查询
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return SearchResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[
            UniversityItem(
                id=item.id,
                dwdm=item.dwdm,
                dwmc=item.dwmc,
                szss=item.szss,
                zhx=item.zhx,
                bs=item.bs,
                syl=item.syl,
                xxfs=item.xxfs,
                tydxs=item.tydxs,
                jsggjh=item.jsggjh,
                zydm=item.zydm,
                zymc=item.zymc,
            )
            for item in items
        ],
    )
