"""
数据看板 API
提供 9 个统计图表所需的数据接口，数据主要来源于 major_detail 表（万级数据量）。
其中第 9 个接口使用 K-Means 聚类算法对院校竞争力进行数据分析。

注意：major_detail 表中 zhx/bs/syl/b985/b211/yjsy 字段取值为 "1"/"0"，
      xxfs 字段取值为 "1"(全日制)/"2"(非全日制)。
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case, distinct, or_

import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from app.core.database import get_db
from app.models.major import Major
from app.models.major_detail import MajorDetail
from app.models.major_university import MajorUniversity

router = APIRouter(prefix="/dashboard", tags=["数据看板"])


def _is_true(column):
    """兼容 '1' 和 '是' 两种取值的布尔判断条件"""
    return or_(column == "1", column == "是")


# ==================== 汇总统计概览 ====================

@router.get("/overview", summary="数据概览统计")
def overview(db: Session = Depends(get_db)):
    """
    返回系统核心统计数据概览，用于看板顶部的数字卡片展示。
    包含数据总量(major_detail)、院校数、专业数、门类数、覆盖省市、双一流数。
    """
    # 数据总量：major_detail 表的记录数（体现万级数据规模）
    total_records = db.query(func.count(MajorDetail.id)).scalar() or 0
    total_universities = db.query(func.count(distinct(MajorDetail.dwdm))).scalar() or 0
    total_majors = db.query(func.count(distinct(MajorDetail.zydm))).scalar() or 0
    total_categories = db.query(func.count(distinct(MajorDetail.mldm))).scalar() or 0
    total_provinces = db.query(func.count(distinct(MajorDetail.szss))).filter(MajorDetail.szss.isnot(None), MajorDetail.szss != "").scalar() or 0
    syl_count = (
        db.query(func.count(distinct(MajorDetail.dwdm)))
        .filter(_is_true(MajorDetail.syl))
        .scalar()
    ) or 0

    return {
        "total_records": total_records,
        "total_universities": total_universities,
        "total_majors": total_majors,
        "total_categories": total_categories,
        "total_provinces": total_provinces,
        "syl_count": syl_count,
    }


# ==================== 图表1：各省市院校数量分布（柱状图） ====================

@router.get("/province_university_count", summary="各省市院校数量分布")
def province_university_count(db: Session = Depends(get_db)):
    """
    统计每个省市有多少所不同院校，用于柱状图展示。
    """
    rows = (
        db.query(
            MajorDetail.szss,
            func.count(distinct(MajorDetail.dwdm)).label("count"),
        )
        .filter(MajorDetail.szss.isnot(None), MajorDetail.szss != "")
        .group_by(MajorDetail.szss)
        .order_by(func.count(distinct(MajorDetail.dwdm)).desc())
        .all()
    )
    return {
        "categories": [r[0] for r in rows],
        "values": [r[1] for r in rows],
    }


# ==================== 图表2：重点院校数量对比（柱状图） ====================

@router.get("/elite_university_ratio", summary="重点院校数量对比")
def elite_university_ratio(db: Session = Depends(get_db)):
    """
    统计双一流、985、211、自划线、博士点院校各自的数量。
    注意：这些类别存在重叠（如985院校一定是211院校），
    因此使用柱状图展示各类别的独立计数，而非饼图。
    """
    total = db.query(func.count(distinct(MajorDetail.dwdm))).scalar() or 0

    syl_count = (
        db.query(func.count(distinct(MajorDetail.dwdm)))
        .filter(_is_true(MajorDetail.syl))
        .scalar()
    ) or 0
    b985_count = (
        db.query(func.count(distinct(MajorDetail.dwdm)))
        .filter(_is_true(MajorDetail.b985))
        .scalar()
    ) or 0
    b211_count = (
        db.query(func.count(distinct(MajorDetail.dwdm)))
        .filter(_is_true(MajorDetail.b211))
        .scalar()
    ) or 0
    zhx_count = (
        db.query(func.count(distinct(MajorDetail.dwdm)))
        .filter(_is_true(MajorDetail.zhx))
        .scalar()
    ) or 0
    bs_count = (
        db.query(func.count(distinct(MajorDetail.dwdm)))
        .filter(_is_true(MajorDetail.bs))
        .scalar()
    ) or 0

    return {
        "categories": ["院校总数", "双一流", "985", "211", "自划线", "博士点"],
        "values": [total, syl_count, b985_count, b211_count, zhx_count, bs_count],
    }


# ==================== 图表3：学位类型分布（饼图） ====================

@router.get("/degree_type_distribution", summary="学位类型分布")
def degree_type_distribution(db: Session = Depends(get_db)):
    """
    统计学术学位与专业学位的招生方向数量分布，用于饼图展示。
    xwlx 字段取值: "xs"=学术学位, "zy"=专业学位。
    xwlxmc 可能为空，因此同时兼容两个字段。
    """
    type_map = {"xs": "学术学位", "zy": "专业学位"}
    rows = (
        db.query(
            MajorDetail.xwlx,
            func.count(MajorDetail.id).label("count"),
        )
        .filter(MajorDetail.xwlx.isnot(None), MajorDetail.xwlx != "")
        .group_by(MajorDetail.xwlx)
        .all()
    )
    return {
        "items": [{"name": type_map.get(r[0], r[0]), "value": r[1]} for r in rows],
    }


# ==================== 图表4：学习方式分布（饼图） ====================

@router.get("/study_mode_distribution", summary="学习方式分布")
def study_mode_distribution(db: Session = Depends(get_db)):
    """
    统计全日制与非全日制招生方向数量。
    xxfs 字段: "1"=全日制, "2"=非全日制。
    """
    mode_map = {"1": "全日制", "2": "非全日制"}
    rows = (
        db.query(
            MajorDetail.xxfs,
            func.count(MajorDetail.id).label("count"),
        )
        .filter(MajorDetail.xxfs.isnot(None), MajorDetail.xxfs != "")
        .group_by(MajorDetail.xxfs)
        .all()
    )
    return {
        "items": [{"name": mode_map.get(r[0], r[0]), "value": r[1]} for r in rows],
    }


# ==================== 图表5：自划线院校招生专业数 TOP15（条形图） ====================

@router.get("/zhx_university_major_count", summary="自划线院校招生专业数排名")
def zhx_university_major_count(db: Session = Depends(get_db)):
    """
    统计自划线（34所）院校各自的招生专业数量，按数量降序排列。
    展示自划线院校的学科覆盖广度。
    """
    rows = (
        db.query(
            MajorDetail.dwmc,
            func.count(distinct(MajorDetail.zydm)).label("major_count"),
        )
        .filter(_is_true(MajorDetail.zhx))
        .group_by(MajorDetail.dwdm, MajorDetail.dwmc)
        .order_by(func.count(distinct(MajorDetail.zydm)).desc())
        .limit(15)
        .all()
    )
    return {
        "categories": [r[0] for r in rows],
        "values": [r[1] for r in rows],
    }


# ==================== 图表6：各门类招生方向数量分布（柱状图） ====================

@router.get("/category_direction_count", summary="各门类招生方向数量分布")
def category_direction_count(db: Session = Depends(get_db)):
    """
    统计每个门类下有多少个招生方向（major_detail记录数），
    反映各门类的招生规模。
    """
    rows = (
        db.query(
            MajorDetail.mlmc,
            func.count(MajorDetail.id).label("count"),
        )
        .filter(MajorDetail.mlmc.isnot(None), MajorDetail.mlmc != "")
        .group_by(MajorDetail.mlmc)
        .order_by(func.count(MajorDetail.id).desc())
        .all()
    )
    return {
        "categories": [r[0] for r in rows],
        "values": [r[1] for r in rows],
    }


# ==================== 图表7：各省市招生人数统计（柱状图） ====================

@router.get("/province_enrollment", summary="各省市拟招生总人数")
def province_enrollment(db: Session = Depends(get_db)):
    """
    统计各省市的拟招生总人数（nzsrs字段求和），
    反映各地区的研究生招生规模。
    """
    rows = (
        db.query(
            MajorDetail.szss,
            func.sum(MajorDetail.nzsrs).label("total"),
        )
        .filter(
            MajorDetail.szss.isnot(None),
            MajorDetail.szss != "",
            MajorDetail.nzsrs.isnot(None),
        )
        .group_by(MajorDetail.szss)
        .order_by(func.sum(MajorDetail.nzsrs).desc())
        .all()
    )
    return {
        "categories": [r[0] for r in rows],
        "values": [int(r[1]) if r[1] else 0 for r in rows],
    }


# ==================== 图表8：院校推免占比 TOP15（柱状图） ====================

@router.get("/university_tuimian_ratio", summary="院校推免占比排名TOP15")
def university_tuimian_ratio(db: Session = Depends(get_db)):
    """
    统计各院校的推免人数占总招生人数的比例，取 TOP 15。
    推免占比 = 推免人数(ssjstmrs) / 拟招生人数(nzsrs)。
    反映院校的选拔竞争程度。
    """
    rows = (
        db.query(
            MajorDetail.dwmc,
            func.sum(MajorDetail.ssjstmrs).label("tuimian"),
            func.sum(MajorDetail.nzsrs).label("total"),
        )
        .filter(
            MajorDetail.nzsrs.isnot(None),
            MajorDetail.nzsrs > 0,
            MajorDetail.ssjstmrs.isnot(None),
        )
        .group_by(MajorDetail.dwdm, MajorDetail.dwmc)
        .having(func.sum(MajorDetail.nzsrs) > 0)
        .order_by((func.sum(MajorDetail.ssjstmrs) * 100.0 / func.sum(MajorDetail.nzsrs)).desc())
        .limit(15)
        .all()
    )
    return {
        "categories": [r[0] for r in rows],
        "tuimian_values": [int(r[1]) if r[1] else 0 for r in rows],
        "total_values": [int(r[2]) if r[2] else 0 for r in rows],
        "ratio_values": [
            round(float(r[1]) / float(r[2]) * 100, 1) if r[2] and r[2] > 0 else 0
            for r in rows
        ],
    }


# ==================== 图表9：【数据分析算法】K-Means 院校竞争力聚类分析（散点图） ====================

@router.get("/university_cluster_analysis", summary="院校竞争力聚类分析")
def university_cluster_analysis(db: Session = Depends(get_db)):
    """
    【核心数据分析算法 —— K-Means 聚类】

    算法思路：
    1. 从 major_detail 表中按院校聚合，提取每所院校的多维特征：
       - 招生专业数量（反映学科覆盖广度）
       - 拟招生总人数（反映招生规模）
       - 是否双一流（0/1）
       - 是否985（0/1）
       - 是否211（0/1）
       - 是否自划线（0/1）
       - 是否有博士点（0/1）
    2. 使用 StandardScaler 对特征进行标准化（消除量纲影响）
    3. 使用 K-Means 算法将院校聚为 3 类：
       - 高竞争力院校（985+自划线+博士点+招生多）
       - 中等竞争力院校
       - 一般竞争力院校
    4. 返回每所院校的聚类标签及特征值，前端用散点图可视化

    该算法使用 Scikit-learn 的 KMeans 实现，适用于毕业论文中的
    "基于聚类算法的院校竞争力分析"章节。
    """

    # 第一步：按院校聚合特征数据
    rows = (
        db.query(
            MajorDetail.dwdm,
            MajorDetail.dwmc,
            func.count(distinct(MajorDetail.zydm)).label("major_count"),
            func.coalesce(func.sum(MajorDetail.nzsrs), 0).label("total_enrollment"),
            func.max(case((_is_true(MajorDetail.syl), 1), else_=0)).label("is_syl"),
            func.max(case((_is_true(MajorDetail.b985), 1), else_=0)).label("is_985"),
            func.max(case((_is_true(MajorDetail.b211), 1), else_=0)).label("is_211"),
            func.max(case((_is_true(MajorDetail.zhx), 1), else_=0)).label("is_zhx"),
            func.max(case((_is_true(MajorDetail.bs), 1), else_=0)).label("is_bs"),
        )
        .filter(MajorDetail.dwdm.isnot(None))
        .group_by(MajorDetail.dwdm, MajorDetail.dwmc)
        .all()
    )

    if len(rows) < 3:
        return {"clusters": [], "centers": [], "labels": ["高竞争力", "中等竞争力", "一般竞争力"]}

    # 第二步：构建特征矩阵
    # 特征：[招生专业数, 拟招生总人数, 双一流, 985, 211, 自划线, 博士点]
    data = []
    uni_info = []
    for r in rows:
        data.append([
            r.major_count,
            int(r.total_enrollment),
            r.is_syl,
            r.is_985,
            r.is_211,
            r.is_zhx,
            r.is_bs,
        ])
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
    cluster_scores = []
    for i in range(n_clusters):
        mask = labels == i
        mean_features = X[mask].mean(axis=0)
        # 综合得分 = 专业数*0.2 + 招生数*0.01 + 双一流*3 + 985*5 + 211*2 + 自划线*5 + 博士点*1
        score = (mean_features[0] * 0.2 + mean_features[1] * 0.01 +
                 mean_features[2] * 3 + mean_features[3] * 5 +
                 mean_features[4] * 2 + mean_features[5] * 5 +
                 mean_features[6] * 1)
        cluster_scores.append((i, score))

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
            "major_count": int(X[i][0]),
            "enrollment": int(X[i][1]),
            "is_syl": int(X[i][2]),
            "is_985": int(X[i][3]),
            "is_211": int(X[i][4]),
            "is_zhx": int(X[i][5]),
            "is_bs": int(X[i][6]),
            "cluster": cluster_id,
            "tier": tier_map[cluster_id],
        })

    # 聚类中心（反标准化回原始尺度）
    centers_original = scaler.inverse_transform(kmeans.cluster_centers_)
    centers = []
    for i in range(n_clusters):
        centers.append({
            "cluster": i,
            "tier": tier_map[i],
            "major_count_avg": round(float(centers_original[i][0]), 1),
            "enrollment_avg": round(float(centers_original[i][1]), 1),
            "syl_ratio": round(float(centers_original[i][2]), 2),
            "b985_ratio": round(float(centers_original[i][3]), 2),
            "b211_ratio": round(float(centers_original[i][4]), 2),
            "zhx_ratio": round(float(centers_original[i][5]), 2),
            "bs_ratio": round(float(centers_original[i][6]), 2),
        })

    return {
        "clusters": clusters,
        "centers": centers,
        "labels": tier_names,
    }
