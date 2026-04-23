"""
数据分析 API
提供专业院校省市分布、研究方向词云等高级分析功能。
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct

import jieba
from collections import Counter

from app.core.database import get_db
from app.models.major_detail import MajorDetail
from app.models.major_university import MajorUniversity

router = APIRouter(prefix="/analysis", tags=["数据分析"])


@router.get("/major_province_distribution", summary="专业院校省市分布")
def major_province_distribution(
    zydm: str = Query(..., description="专业代码"),
    db: Session = Depends(get_db),
):
    """
    统计指定专业在全国各省市的院校数量分布，用于柱状图/地图展示。
    展示哪些省份开设该专业的院校最多。
    """
    rows = (
        db.query(
            MajorUniversity.szss,
            func.count(distinct(MajorUniversity.dwdm)).label("count"),
        )
        .filter(
            MajorUniversity.zydm == zydm,
            MajorUniversity.szss.isnot(None),
            MajorUniversity.szss != "",
        )
        .group_by(MajorUniversity.szss)
        .order_by(func.count(distinct(MajorUniversity.dwdm)).desc())
        .all()
    )

    # 同时返回该专业名称
    first = db.query(MajorUniversity.zymc).filter(MajorUniversity.zydm == zydm).first()
    zymc = first[0] if first else zydm

    return {
        "zymc": zymc,
        "categories": [r[0] for r in rows],
        "values": [r[1] for r in rows],
        "total_universities": sum(r[1] for r in rows),
        "total_provinces": len(rows),
    }


@router.get("/wordcloud", summary="研究方向词云分析")
def wordcloud_analysis(
    dwdm: str = Query(None, description="院校代码（可选）"),
    zydm: str = Query(None, description="专业代码（可选）"),
    db: Session = Depends(get_db),
):
    """
    基于 NLP（jieba 分词）技术，对研究方向名称和专业备注进行词频分析。
    可按院校或按专业维度分析。返回词频列表用于前端词云图渲染。

    算法流程：
    1. 从 major_detail 表中提取 yjfxmc（研究方向名称）和 zybz（专业备注）
    2. 使用 jieba 进行中文分词
    3. 过滤停用词和单字词
    4. 统计词频，返回 TOP 100 高频词
    """
    query = db.query(MajorDetail.yjfxmc, MajorDetail.zybz)

    if dwdm:
        query = query.filter(MajorDetail.dwdm == dwdm)
    if zydm:
        query = query.filter(MajorDetail.zydm == zydm)

    rows = query.all()

    # 拼接所有文本
    text_parts = []
    for r in rows:
        if r[0]:
            text_parts.append(r[0])
        if r[1]:
            text_parts.append(r[1])

    full_text = " ".join(text_parts)
    if not full_text.strip():
        return {"words": [], "total_docs": len(rows)}

    # jieba 分词
    words = jieba.lcut(full_text)

    # 停用词列表（常见无意义词汇）
    stop_words = {
        "的", "了", "在", "是", "我", "有", "和", "就", "不", "人",
        "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去",
        "你", "会", "着", "没有", "看", "好", "自己", "这", "他", "她",
        "它", "们", "那", "被", "从", "把", "与", "等", "及", "或",
        "中", "为", "以", "对", "方", "所", "其", "之", "者", "于",
        "但", "而", "能", "可", "已", "由", "此", "如", "用", "向",
        "多", "后", "则", "得", "使", "来", "年", "个", "含", "限",
        "另", "外", "内", "间", "下", "请", "见", "须", "需", "按",
        "选", "任", "门", "组", "套", "类", "项", "名", "号", "学",
        "不区分", "研究", "方向", "专业", "学科", "领域", "技术",
    }

    # 过滤：去掉单字词、数字、停用词
    filtered = [
        w for w in words
        if len(w) >= 2 and w not in stop_words and not w.isdigit()
    ]

    # 词频统计
    counter = Counter(filtered)
    top_words = counter.most_common(100)

    return {
        "words": [{"name": w, "value": c} for w, c in top_words],
        "total_docs": len(rows),
    }


@router.get("/university_radar", summary="院校对比雷达图数据")
def university_radar(
    dwdm_list: str = Query(..., description="院校代码列表，逗号分隔"),
    db: Session = Depends(get_db),
):
    """
    为院校对比提供雷达图所需的多维度数据。
    维度包括：双一流、985、211、博士点、自划线、招生规模（归一化到0-100）。
    """
    dwdm_codes = [d.strip() for d in dwdm_list.split(",") if d.strip()]

    # 获取所有院校的最大招生数用于归一化
    max_enrollment = (
        db.query(func.sum(MajorDetail.nzsrs))
        .filter(MajorDetail.dwdm.in_(dwdm_codes))
        .group_by(MajorDetail.dwdm)
        .order_by(func.sum(MajorDetail.nzsrs).desc())
        .first()
    )
    max_enroll_val = max_enrollment[0] if max_enrollment and max_enrollment[0] else 1

    # 最大专业数
    max_majors = (
        db.query(func.count(distinct(MajorDetail.zydm)))
        .filter(MajorDetail.dwdm.in_(dwdm_codes))
        .group_by(MajorDetail.dwdm)
        .order_by(func.count(distinct(MajorDetail.zydm)).desc())
        .first()
    )
    max_major_val = max_majors[0] if max_majors and max_majors[0] else 1

    results = []
    for dwdm in dwdm_codes:
        first = db.query(MajorDetail).filter(MajorDetail.dwdm == dwdm).first()
        if not first:
            continue

        enrollment = (
            db.query(func.sum(MajorDetail.nzsrs))
            .filter(MajorDetail.dwdm == dwdm)
            .scalar() or 0
        )
        major_count = (
            db.query(func.count(distinct(MajorDetail.zydm)))
            .filter(MajorDetail.dwdm == dwdm)
            .scalar() or 0
        )

        def _yes_score(val):
            return 100 if val in ("是", "1") else 0

        results.append({
            "dwdm": dwdm,
            "dwmc": first.dwmc,
            "values": [
                _yes_score(first.syl),       # 双一流
                _yes_score(first.b985),      # 985
                _yes_score(first.b211),      # 211
                _yes_score(first.bs),        # 博士点
                _yes_score(first.zhx),       # 自划线
                round(enrollment / max_enroll_val * 100) if max_enroll_val else 0,  # 招生规模
                round(major_count / max_major_val * 100) if max_major_val else 0,   # 专业覆盖
            ],
        })

    return {
        "indicators": [
            {"name": "双一流", "max": 100},
            {"name": "985", "max": 100},
            {"name": "211", "max": 100},
            {"name": "博士点", "max": 100},
            {"name": "自划线", "max": 100},
            {"name": "招生规模", "max": 100},
            {"name": "专业覆盖", "max": 100},
        ],
        "universities": results,
    }
