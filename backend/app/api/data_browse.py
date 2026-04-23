"""
支撑数据浏览 API
提供 major、major_university、major_detail 三张采集表的数据浏览接口，
支持分页和关键字段筛选。
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from typing import Optional

from app.core.database import get_db
from app.models.major import Major
from app.models.major_university import MajorUniversity
from app.models.major_detail import MajorDetail

router = APIRouter(prefix="/data", tags=["支撑数据"])


# ==================== 专业信息表 major ====================

@router.get("/major", summary="专业信息表分页查询")
def list_major(
    keyword: Optional[str] = Query(None, description="专业名称/代码关键字"),
    mldm: Optional[str] = Query(None, description="门类代码"),
    xwlx: Optional[str] = Query(None, description="学位类型 xs/zy"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    分页查询 major 表（研究生专业信息表）。
    支持按专业名称/代码关键字、门类代码、学位类型筛选。
    """
    query = db.query(Major)

    if keyword:
        query = query.filter(
            Major.zymc.contains(keyword) | Major.zydm.contains(keyword)
        )
    if mldm:
        query = query.filter(Major.mldm == mldm)
    if xwlx:
        query = query.filter(Major.xwlx == xwlx)

    total = query.count()
    items = query.order_by(Major.id).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": r.id, "zydm": r.zydm, "zymc": r.zymc,
                "mldm": r.mldm, "mlmc": r.mlmc,
                "yjxkdm": r.yjxkdm, "yjxkmc": r.yjxkmc,
                "xwlx": r.xwlx, "xwlxmc": r.xwlxmc,
            }
            for r in items
        ],
    }


@router.get("/major/filters", summary="专业表筛选选项")
def major_filters(db: Session = Depends(get_db)):
    """返回 major 表可用的门类列表（用于筛选下拉框）"""
    categories = (
        db.query(distinct(Major.mldm), Major.mlmc)
        .filter(Major.mldm.isnot(None))
        .order_by(Major.mldm)
        .all()
    )
    return {
        "categories": [{"value": r[0], "label": r[1] or r[0]} for r in categories],
    }


# ==================== 专业-院校关联表 major_university ====================

@router.get("/major_university", summary="专业-院校关联表分页查询")
def list_major_university(
    keyword: Optional[str] = Query(None, description="院校名称/专业名称关键字"),
    szss: Optional[str] = Query(None, description="省市"),
    mldm: Optional[str] = Query(None, description="门类代码"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    分页查询 major_university 表（专业-院校关联表）。
    支持按院校/专业名称关键字、省市、门类筛选。
    """
    query = db.query(MajorUniversity)

    if keyword:
        query = query.filter(
            MajorUniversity.dwmc.contains(keyword) | MajorUniversity.zymc.contains(keyword)
        )
    if szss:
        query = query.filter(MajorUniversity.szss == szss)
    if mldm:
        query = query.filter(MajorUniversity.mldm == mldm)

    total = query.count()
    items = query.order_by(MajorUniversity.id).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": r.id, "zydm": r.zydm, "zymc": r.zymc,
                "mldm": r.mldm, "mlmc": r.mlmc,
                "yjxkdm": r.yjxkdm, "yjxkmc": r.yjxkmc,
                "xwlx": r.xwlx, "xwlxmc": r.xwlxmc,
                "dwdm": r.dwdm, "dwmc": r.dwmc,
                "szss": r.szss, "zhx": r.zhx, "bs": r.bs,
                "syl": r.syl, "xxfs": r.xxfs,
                "tydxs": r.tydxs, "jsggjh": r.jsggjh,
            }
            for r in items
        ],
    }


@router.get("/major_university/filters", summary="关联表筛选选项")
def major_university_filters(db: Session = Depends(get_db)):
    """返回 major_university 表可用的省市和门类列表"""
    provinces = (
        db.query(distinct(MajorUniversity.szss))
        .filter(MajorUniversity.szss.isnot(None), MajorUniversity.szss != "")
        .order_by(MajorUniversity.szss)
        .all()
    )
    categories = (
        db.query(distinct(MajorUniversity.mldm), MajorUniversity.mlmc)
        .filter(MajorUniversity.mldm.isnot(None))
        .order_by(MajorUniversity.mldm)
        .all()
    )
    return {
        "provinces": [{"value": r[0], "label": r[0]} for r in provinces],
        "categories": [{"value": r[0], "label": r[1] or r[0]} for r in categories],
    }


# ==================== 专业研究方向详情表 major_detail ====================

@router.get("/major_detail", summary="专业研究方向详情表分页查询")
def list_major_detail(
    keyword: Optional[str] = Query(None, description="院校名称/专业名称/研究方向关键字"),
    szss: Optional[str] = Query(None, description="省市"),
    mldm: Optional[str] = Query(None, description="门类代码"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    分页查询 major_detail 表（专业研究方向详情表）。
    支持按院校/专业/研究方向名称关键字、省市、门类筛选。
    """
    query = db.query(MajorDetail)

    if keyword:
        query = query.filter(
            MajorDetail.dwmc.contains(keyword) |
            MajorDetail.zymc.contains(keyword) |
            MajorDetail.yjfxmc.contains(keyword)
        )
    if szss:
        query = query.filter(MajorDetail.szss == szss)
    if mldm:
        query = query.filter(MajorDetail.mldm == mldm)

    total = query.count()
    items = query.order_by(MajorDetail.id).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": r.id, "zydm": r.zydm, "zymc": r.zymc,
                "mldm": r.mldm, "mlmc": r.mlmc,
                "yjxkdm": r.yjxkdm, "yjxkmc": r.yjxkmc,
                "xwlx": r.xwlx, "xwlxmc": r.xwlxmc,
                "dwdm": r.dwdm, "dwmc": r.dwmc,
                "szss": r.szss, "zhx": r.zhx, "bs": r.bs,
                "syl": r.syl, "b985": r.b985, "b211": r.b211,
                "yjsy": r.yjsy, "yxsmc": r.yxsmc,
                "yjfxmc": r.yjfxmc, "zdjs": r.zdjs,
                "nzsrs": r.nzsrs, "xxfs": r.xxfs,
                "tydxs": r.tydxs, "jsggjh": r.jsggjh,
                "ssjstmrs": r.ssjstmrs,
                "km1mc": r.km1mc, "km2mc": r.km2mc,
                "km3mc": r.km3mc, "km4mc": r.km4mc,
            }
            for r in items
        ],
    }


@router.get("/major_detail/filters", summary="详情表筛选选项")
def major_detail_filters(db: Session = Depends(get_db)):
    """返回 major_detail 表可用的省市和门类列表"""
    provinces = (
        db.query(distinct(MajorDetail.szss))
        .filter(MajorDetail.szss.isnot(None), MajorDetail.szss != "")
        .order_by(MajorDetail.szss)
        .all()
    )
    categories = (
        db.query(distinct(MajorDetail.mldm), MajorDetail.mlmc)
        .filter(MajorDetail.mldm.isnot(None))
        .order_by(MajorDetail.mldm)
        .all()
    )
    return {
        "provinces": [{"value": r[0], "label": r[0]} for r in provinces],
        "categories": [{"value": r[0], "label": r[1] or r[0]} for r in categories],
    }
