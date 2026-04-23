"""
院校深度画像 API
提供单所院校的详细信息、专业分布、招生数据图表等。
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, case, or_

from app.core.database import get_db
from app.models.major_detail import MajorDetail
from app.models.major_university import MajorUniversity

router = APIRouter(prefix="/university", tags=["院校画像"])


def _is_true(column):
    """兼容 '1' 和 '是' 两种取值的布尔判断条件"""
    return or_(column == "1", column == "是")


@router.get("/detail", summary="院校基本信息")
def university_detail(
    dwdm: str = Query(..., description="院校代码"),
    db: Session = Depends(get_db),
):
    """
    获取指定院校的基本属性信息。
    从 major_detail 表中取第一条记录获取院校名称、省市、各类标签。
    """
    first = db.query(MajorDetail).filter(MajorDetail.dwdm == dwdm).first()
    if not first:
        raise HTTPException(status_code=404, detail="院校不存在")

    # 统计该校的招生方向总数
    total_directions = (
        db.query(func.count(MajorDetail.id))
        .filter(MajorDetail.dwdm == dwdm)
        .scalar() or 0
    )
    # 涉及专业数
    total_majors = (
        db.query(func.count(distinct(MajorDetail.zydm)))
        .filter(MajorDetail.dwdm == dwdm)
        .scalar() or 0
    )
    # 涉及院系数
    total_departments = (
        db.query(func.count(distinct(MajorDetail.yxsmc)))
        .filter(MajorDetail.dwdm == dwdm, MajorDetail.yxsmc.isnot(None))
        .scalar() or 0
    )
    # 总招生人数
    total_enrollment = (
        db.query(func.sum(MajorDetail.nzsrs))
        .filter(MajorDetail.dwdm == dwdm)
        .scalar() or 0
    )
    # 总推免人数
    total_tuimian = (
        db.query(func.sum(MajorDetail.ssjstmrs))
        .filter(MajorDetail.dwdm == dwdm)
        .scalar() or 0
    )

    return {
        "dwdm": first.dwdm,
        "dwmc": first.dwmc,
        "szss": first.szss,
        "zhx": first.zhx,
        "bs": first.bs,
        "syl": first.syl,
        "b985": first.b985,
        "b211": first.b211,
        "yjsy": first.yjsy,
        "total_directions": total_directions,
        "total_majors": total_majors,
        "total_departments": total_departments,
        "total_enrollment": total_enrollment,
        "total_tuimian": total_tuimian,
    }


@router.get("/enrollment_pie", summary="统考与推免名额比例")
def enrollment_pie(
    dwdm: str = Query(..., description="院校代码"),
    db: Session = Depends(get_db),
):
    """
    统计指定院校的统考名额与推免名额的占比，用于饼图展示。
    统考名额 = 总招生人数 - 推免人数。
    """
    total = (
        db.query(func.sum(MajorDetail.nzsrs))
        .filter(MajorDetail.dwdm == dwdm)
        .scalar() or 0
    )
    tuimian = (
        db.query(func.sum(MajorDetail.ssjstmrs))
        .filter(MajorDetail.dwdm == dwdm)
        .scalar() or 0
    )
    tongkao = max(total - tuimian, 0)

    return {
        "items": [
            {"name": "统考名额", "value": tongkao},
            {"name": "推免名额", "value": tuimian},
        ],
        "total": total,
    }


@router.get("/department_bar", summary="院系招生分布")
def department_bar(
    dwdm: str = Query(..., description="院校代码"),
    db: Session = Depends(get_db),
):
    """
    统计指定院校各院系所的招生方向数量和招生人数，用于柱状图展示。
    """
    rows = (
        db.query(
            MajorDetail.yxsmc,
            func.count(MajorDetail.id).label("direction_count"),
            func.sum(MajorDetail.nzsrs).label("enrollment"),
        )
        .filter(MajorDetail.dwdm == dwdm, MajorDetail.yxsmc.isnot(None))
        .group_by(MajorDetail.yxsmc)
        .order_by(func.count(MajorDetail.id).desc())
        .limit(20)
        .all()
    )
    return {
        "categories": [r[0] for r in rows],
        "direction_counts": [r[1] for r in rows],
        "enrollment_values": [r[2] or 0 for r in rows],
    }


@router.get("/study_mode_pie", summary="学习方式分布")
def study_mode_pie(
    dwdm: str = Query(..., description="院校代码"),
    db: Session = Depends(get_db),
):
    """该校全日制 vs 非全日制招生方向数量饼图"""
    full_time = (
        db.query(func.count(MajorDetail.id))
        .filter(MajorDetail.dwdm == dwdm, MajorDetail.xxfs == "1")
        .scalar() or 0
    )
    part_time = (
        db.query(func.count(MajorDetail.id))
        .filter(MajorDetail.dwdm == dwdm, MajorDetail.xxfs == "2")
        .scalar() or 0
    )
    return {
        "items": [
            {"name": "全日制", "value": full_time},
            {"name": "非全日制", "value": part_time},
        ]
    }


@router.get("/programs", summary="该校所有专业研究方向列表")
def university_programs(
    dwdm: str = Query(..., description="院校代码"),
    keyword: str = Query(None, description="专业/方向关键字"),
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """
    分页查询该校所有专业研究方向详情，支持关键字筛选。
    """
    query = db.query(MajorDetail).filter(MajorDetail.dwdm == dwdm)
    if keyword:
        query = query.filter(
            MajorDetail.zymc.contains(keyword) |
            MajorDetail.yjfxmc.contains(keyword) |
            MajorDetail.yxsmc.contains(keyword)
        )
    total = query.count()
    items = query.order_by(MajorDetail.yxsmc, MajorDetail.zydm).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": r.id, "zydm": r.zydm, "zymc": r.zymc,
                "mlmc": r.mlmc, "yjxkmc": r.yjxkmc,
                "yxsmc": r.yxsmc, "yjfxmc": r.yjfxmc,
                "zdjs": r.zdjs, "nzsrs": r.nzsrs,
                "ssjstmrs": r.ssjstmrs,
                "xxfs": r.xxfs, "xwlx": r.xwlx,
                "km1mc": r.km1mc, "km2mc": r.km2mc,
                "km3mc": r.km3mc, "km4mc": r.km4mc,
                "zybz": r.zybz,
            }
            for r in items
        ],
    }
