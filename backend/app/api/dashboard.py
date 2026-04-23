"""
数据看板 API
提供 9 个统计图表所需的数据接口，覆盖院校分布、专业分布、属性占比等维度。
其中第 9 个接口使用 K-Means 聚类算法对院校竞争力进行数据分析。
"""

import json
from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case, distinct

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from app.core.database import get_db
from app.models.major import Major
from app.models.major_university import MajorUniversity

router = APIRouter(prefix="/dashboard", tags=["数据看板"])


# ==================== 图表1：各门类院校数量分布（柱状图） ====================

@router.get("/category_university_count", summary="各门类院校数量分布")
def category_university_count(db: Session = Depends(get_db)):
    """
    统计每个门类下有多少所不同院校招生。
    用于柱状图展示，横轴为门类名称，纵轴为院校数量。
    """
    rows = (
        db.query(
            MajorUniversity.mlmc,
            func.count(distinct(MajorUniversity.dwdm)).label("count"),
        )
        .filter(MajorUniversity.mlmc.isnot(None))
        .group_by(MajorUniversity.mlmc)
        .order_by(func.count(distinct(MajorUniversity.dwdm)).desc())
        .all()
    )
    return {
        "categories": [r[0] for r in rows],
        "values": [r[1] for r in rows],
    }


# ==================== 图表2：各省市院校数量分布（柱状图） ====================

@router.get("/province_university_count", summary="各省市院校数量分布")
def province_university_count(db: Session = Depends(get_db)):
    """
    统计每个省市有多少所不同院校，用于柱状图或地图可视化。
    """
    rows = (
        db.query(
            MajorUniversity.szss,
            func.count(distinct(MajorUniversity.dwdm)).label("count"),
        )
        .filter(MajorUniversity.szss.isnot(None))
        .group_by(MajorUniversity.szss)
        .order_by(func.count(distinct(MajorUniversity.dwdm)).desc())
        .all()
    )
    return {
        "categories": [r[0] for r in rows],
        "values": [r[1] for r in rows],
    }


# ==================== 图表3：双一流院校占比（饼图） ====================

@router.get("/syl_ratio", summary="双一流院校占比")
def syl_ratio(db: Session = Depends(get_db)):
    """
    统计双一流院校与非双一流院校的数量占比，用于饼图展示。
    """
    total = db.query(func.count(distinct(MajorUniversity.dwdm))).scalar() or 0
    syl_count = (
        db.query(func.count(distinct(MajorUniversity.dwdm)))
        .filter(MajorUniversity.syl == "是")
        .scalar()
    ) or 0
    non_syl = total - syl_count
    return {
        "items": [
            {"name": "双一流院校", "value": syl_count},
            {"name": "非双一流院校", "value": non_syl},
        ]
    }


# ==================== 图表4：学位类型分布（饼图） ====================

@router.get("/degree_type_distribution", summary="学位类型分布")
def degree_type_distribution(db: Session = Depends(get_db)):
    """
    统计学术学位与专业学位的专业数量分布，用于饼图展示。
    """
    rows = (
        db.query(
            Major.xwlxmc,
            func.count(Major.id).label("count"),
        )
        .filter(Major.xwlxmc.isnot(None))
        .group_by(Major.xwlxmc)
        .all()
    )
    return {
        "items": [{"name": r[0], "value": r[1]} for r in rows],
    }


# ==================== 图表5：学习方式分布（饼图） ====================

@router.get("/study_mode_distribution", summary="学习方式分布")
def study_mode_distribution(db: Session = Depends(get_db)):
    """
    统计全日制与非全日制招生的院校专业数量，用于饼图展示。
    """
    rows = (
        db.query(
            MajorUniversity.xxfs,
            func.count(MajorUniversity.id).label("count"),
        )
        .filter(MajorUniversity.xxfs.isnot(None))
        .group_by(MajorUniversity.xxfs)
        .all()
    )
    return {
        "items": [{"name": r[0], "value": r[1]} for r in rows],
    }


# ==================== 图表6：自划线 vs 非自划线院校对比（柱状图） ====================

@router.get("/zhx_comparison", summary="自划线与非自划线院校对比")
def zhx_comparison(db: Session = Depends(get_db)):
    """
    统计自划线院校和非自划线院校的数量，
    同时对比各自的双一流、博士点占比，用于分组柱状图。
    """
    # 自划线院校列表
    zhx_unis = (
        db.query(distinct(MajorUniversity.dwdm))
        .filter(MajorUniversity.zhx == "是")
        .all()
    )
    zhx_dwdm_set = {r[0] for r in zhx_unis}

    # 非自划线院校列表
    non_zhx_unis = (
        db.query(distinct(MajorUniversity.dwdm))
        .filter(MajorUniversity.zhx != "是")
        .all()
    )
    non_zhx_dwdm_set = {r[0] for r in non_zhx_unis} - zhx_dwdm_set

    # 统计双一流数量
    zhx_syl = (
        db.query(func.count(distinct(MajorUniversity.dwdm)))
        .filter(MajorUniversity.zhx == "是", MajorUniversity.syl == "是")
        .scalar()
    ) or 0
    non_zhx_syl = (
        db.query(func.count(distinct(MajorUniversity.dwdm)))
        .filter(MajorUniversity.zhx != "是", MajorUniversity.syl == "是")
        .scalar()
    ) or 0

    return {
        "categories": ["自划线院校", "非自划线院校"],
        "series": [
            {"name": "院校总数", "values": [len(zhx_dwdm_set), len(non_zhx_dwdm_set)]},
            {"name": "其中双一流", "values": [zhx_syl, non_zhx_syl]},
        ],
    }


# ==================== 图表7：各门类专业数量 TOP10（横向条形图） ====================

@router.get("/category_major_top10", summary="各门类专业数量TOP10")
def category_major_top10(db: Session = Depends(get_db)):
    """
    统计每个门类下的专业数量，取 TOP 10，用于横向条形图展示。
    """
    rows = (
        db.query(
            Major.mlmc,
            func.count(Major.id).label("count"),
        )
        .filter(Major.mlmc.isnot(None))
        .group_by(Major.mlmc)
        .order_by(func.count(Major.id).desc())
        .limit(10)
        .all()
    )
    return {
        "categories": [r[0] for r in rows],
        "values": [r[1] for r in rows],
    }


# ==================== 图表8：博士点院校省市分布（柱状图） ====================

@router.get("/bs_province_distribution", summary="博士点院校省市分布")
def bs_province_distribution(db: Session = Depends(get_db)):
    """
    统计拥有博士点的院校在各省市的分布数量，用于柱状图展示。
    """
    rows = (
        db.query(
            MajorUniversity.szss,
            func.count(distinct(MajorUniversity.dwdm)).label("count"),
        )
        .filter(MajorUniversity.bs == "是", MajorUniversity.szss.isnot(None))
        .group_by(MajorUniversity.szss)
        .order_by(func.count(distinct(MajorUniversity.dwdm)).desc())
        .all()
    )
    return {
        "categories": [r[0] for r in rows],
        "values": [r[1] for r in rows],
    }


# ==================== 图表9：【数据分析算法】K-Means 院校竞争力聚类分析（散点图） ====================

@router.get("/university_cluster_analysis", summary="院校竞争力聚类分析")
def university_cluster_analysis(db: Session = Depends(get_db)):
    """
    【核心数据分析算法 —— K-Means 聚类】

    算法思路：
    1. 从 major_university 表中按院校聚合，提取每所院校的多维特征：
       - 招生专业数量（反映学科覆盖广度）
       - 是否双一流（0/1）
       - 是否自划线（0/1）
       - 是否有博士点（0/1）
    2. 使用 StandardScaler 对特征进行标准化（消除量纲影响）
    3. 使用 K-Means 算法将院校聚为 3 类：
       - 高竞争力院校（双一流+自划线+博士点+专业多）
       - 中等竞争力院校
       - 一般竞争力院校
    4. 返回每所院校的聚类标签及特征值，前端用散点图可视化

    该算法使用 Scikit-learn 的 KMeans 实现，适用于毕业论文中的
    "基于聚类算法的院校竞争力分析"章节。
    """

    # 第一步：按院校聚合特征数据
    rows = (
        db.query(
            MajorUniversity.dwdm,
            MajorUniversity.dwmc,
            func.count(distinct(MajorUniversity.zydm)).label("major_count"),
            func.max(case((MajorUniversity.syl == "是", 1), else_=0)).label("is_syl"),
            func.max(case((MajorUniversity.zhx == "是", 1), else_=0)).label("is_zhx"),
            func.max(case((MajorUniversity.bs == "是", 1), else_=0)).label("is_bs"),
        )
        .filter(MajorUniversity.dwdm.isnot(None))
        .group_by(MajorUniversity.dwdm, MajorUniversity.dwmc)
        .all()
    )

    if len(rows) < 3:
        return {"clusters": [], "centers": [], "labels": ["高竞争力", "中等竞争力", "一般竞争力"]}

    # 第二步：构建特征矩阵
    data = []
    uni_info = []
    for r in rows:
        data.append([r.major_count, r.is_syl, r.is_zhx, r.is_bs])
        uni_info.append({"dwdm": r.dwdm, "dwmc": r.dwmc})

    X = np.array(data, dtype=float)

    # 第三步：特征标准化（Z-Score 标准化，消除量纲差异）
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 第四步：K-Means 聚类，分为 3 类
    n_clusters = 3
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    # 第五步：根据聚类中心的特征均值排序，确定竞争力等级
    # 计算每个簇的平均特征值之和，值越大竞争力越高
    cluster_scores = []
    for i in range(n_clusters):
        mask = labels == i
        mean_features = X[mask].mean(axis=0)
        # 综合得分 = 专业数量均值 * 0.3 + 双一流 * 3 + 自划线 * 5 + 博士点 * 1
        score = mean_features[0] * 0.3 + mean_features[1] * 3 + mean_features[2] * 5 + mean_features[3] * 1
        cluster_scores.append((i, score))

    # 按综合得分降序排列：最高=高竞争力，中间=中等，最低=一般
    cluster_scores.sort(key=lambda x: x[1], reverse=True)
    tier_map = {}
    tier_names = ["高竞争力", "中等竞争力", "一般竞争力"]
    for rank, (cluster_id, _) in enumerate(cluster_scores):
        tier_map[cluster_id] = tier_names[rank]

    # 第六步：组装返回数据
    clusters = []
    for i, info in enumerate(uni_info):
        cluster_id = int(labels[i])
        clusters.append({
            "dwdm": info["dwdm"],
            "dwmc": info["dwmc"],
            "major_count": int(X[i][0]),     # 招生专业数
            "is_syl": int(X[i][1]),          # 是否双一流
            "is_zhx": int(X[i][2]),          # 是否自划线
            "is_bs": int(X[i][3]),           # 是否有博士点
            "cluster": cluster_id,
            "tier": tier_map[cluster_id],     # 竞争力等级标签
        })

    # 聚类中心（反标准化回原始尺度）
    centers_original = scaler.inverse_transform(kmeans.cluster_centers_)
    centers = []
    for i in range(n_clusters):
        centers.append({
            "cluster": i,
            "tier": tier_map[i],
            "major_count_avg": round(float(centers_original[i][0]), 1),
            "syl_ratio": round(float(centers_original[i][1]), 2),
            "zhx_ratio": round(float(centers_original[i][2]), 2),
            "bs_ratio": round(float(centers_original[i][3]), 2),
        })

    return {
        "clusters": clusters,
        "centers": centers,
        "labels": tier_names,
    }


# ==================== 汇总统计概览 ====================

@router.get("/overview", summary="数据概览统计")
def overview(db: Session = Depends(get_db)):
    """
    返回系统核心统计数据概览，用于看板顶部的数字卡片展示。
    """
    total_universities = db.query(func.count(distinct(MajorUniversity.dwdm))).scalar() or 0
    total_majors = db.query(func.count(distinct(Major.zydm))).scalar() or 0
    total_categories = db.query(func.count(distinct(Major.mldm))).scalar() or 0
    total_provinces = db.query(func.count(distinct(MajorUniversity.szss))).scalar() or 0
    syl_count = (
        db.query(func.count(distinct(MajorUniversity.dwdm)))
        .filter(MajorUniversity.syl == "是")
        .scalar()
    ) or 0

    return {
        "total_universities": total_universities,
        "total_majors": total_majors,
        "total_categories": total_categories,
        "total_provinces": total_provinces,
        "syl_count": syl_count,
    }
