"""
智能推荐算法服务模块 —— 【核心算法】
基于内容的推荐（Content-Based Recommendation）

算法思路：
1. 从 major_university 表中获取目标专业(zydm)对应的所有院校
2. 结合用户画像（意向省市、学习方式期望、实力自评）对每所院校进行多维度打分
3. 打分维度包括：
   - 难度系数：自划线(+5)、双一流(+3)、博士点(+1)
   - 匹配度：省市匹配(+10)、学习方式匹配(+5)
4. 根据用户"实力自评"设定阈值，将院校分为冲刺/稳妥/保底三个梯度

该模块使用 Pandas 进行批量数据处理，使用 NumPy 进行高效的数值计算。
"""

import json
from typing import Optional

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from app.models.major_university import MajorUniversity
from app.models.recommend_log import RecommendLog
from app.models.user import User


def _is_yes(value: Optional[str]) -> bool:
    """判断字段值是否为"是" —— 数据库中用"是/否"字符串表示布尔"""
    return value is not None and value.strip() == "是"


def calculate_recommendation(
    db: Session,
    user: User,
    zydm: str,
) -> dict:
    """
    核心推荐算法函数

    :param db: 数据库会话
    :param user: 当前登录用户（包含画像信息）
    :param zydm: 目标专业代码
    :return: 分组后的推荐结果字典 {sprint, stable, safe}
    """

    # ========== 第一步：获取该专业的所有招生院校 ==========
    records = (
        db.query(MajorUniversity)
        .filter(MajorUniversity.zydm == zydm)
        .all()
    )
    if not records:
        return {"sprint": [], "stable": [], "safe": []}

    # ========== 第二步：构建 DataFrame 用于批量计算 ==========
    data = []
    for r in records:
        data.append({
            "dwdm": r.dwdm,
            "dwmc": r.dwmc,
            "szss": r.szss,
            "zhx": r.zhx,
            "bs": r.bs,
            "syl": r.syl,
            "xxfs": r.xxfs,
            "tydxs": r.tydxs,
            "jsggjh": r.jsggjh,
            "zydm": r.zydm,
            "zymc": r.zymc,
        })
    df = pd.DataFrame(data)

    # 去重：同一院校同一专业只保留一条
    df = df.drop_duplicates(subset=["dwdm"], keep="first").reset_index(drop=True)

    # ========== 第三步：计算难度系数 ==========
    # 自划线院校 +5 分（自划线院校有自主划定分数线的权力，竞争更激烈）
    df["difficulty"] = df["zhx"].apply(lambda x: 5.0 if _is_yes(x) else 0.0)
    # 双一流院校 +3 分（国家重点建设高校，整体实力较强）
    df["difficulty"] += df["syl"].apply(lambda x: 3.0 if _is_yes(x) else 0.0)
    # 有博士点 +1 分（有博士授权点的学科科研实力相对更强）
    df["difficulty"] += df["bs"].apply(lambda x: 1.0 if _is_yes(x) else 0.0)

    # ========== 第四步：计算匹配度得分 ==========
    # 解析用户画像中的意向省市
    user_provinces: list[str] = []
    if user.target_provinces:
        try:
            user_provinces = json.loads(user.target_provinces)
        except (json.JSONDecodeError, TypeError):
            user_provinces = []

    # 省市匹配：如果院校所在省市在用户意向列表中，+10 分
    df["match_score"] = df["szss"].apply(
        lambda x: 10.0 if x and x in user_provinces else 0.0
    )

    # 学习方式匹配：如果院校学习方式与用户期望一致，+5 分
    user_study_mode = user.study_mode  # "1"=全日制, "2"=非全日制
    if user_study_mode:
        study_mode_map = {"1": "全日制", "2": "非全日制"}
        expected = study_mode_map.get(user_study_mode, "")
        df["match_score"] += df["xxfs"].apply(
            lambda x: 5.0 if x and expected in str(x) else 0.0
        )

    # ========== 第五步：计算综合得分 ==========
    # 综合得分 = 难度系数 + 匹配度得分
    df["total_score"] = df["difficulty"] + df["match_score"]

    # ========== 第六步：根据用户实力自评，划分三个梯度 ==========
    # 实力等级决定了"稳妥区"的难度系数范围
    # strong（强）：难度系数 5-9 为稳妥区
    # medium（中等）：难度系数 3-5 为稳妥区
    # weak（弱）：难度系数 0-3 为稳妥区
    self_rating = user.self_rating or "medium"

    # 定义各实力等级对应的难度阈值
    thresholds = {
        "strong": {"sprint_min": 8, "stable_min": 4, "stable_max": 8},
        "medium": {"sprint_min": 6, "stable_min": 2, "stable_max": 6},
        "weak":   {"sprint_min": 4, "stable_min": 1, "stable_max": 4},
    }
    t = thresholds.get(self_rating, thresholds["medium"])

    def assign_tier(row: pd.Series) -> str:
        """根据难度系数将院校分配到冲刺/稳妥/保底梯度"""
        d = row["difficulty"]
        if d >= t["sprint_min"]:
            return "sprint"      # 冲刺院校：难度系数高于上限
        elif t["stable_min"] <= d < t["stable_max"]:
            return "stable"      # 稳妥院校：难度系数在中间区间
        else:
            return "safe"        # 保底院校：难度系数低于下限

    df["tier"] = df.apply(assign_tier, axis=1)

    # 梯度中文标签映射
    tier_labels = {
        "sprint": "冲刺院校",
        "stable": "稳妥院校",
        "safe": "保底院校",
    }
    df["tier_label"] = df["tier"].map(tier_labels)

    # ========== 第七步：按综合得分排序并分组输出 ==========
    df = df.sort_values("total_score", ascending=False)

    result: dict[str, list] = {"sprint": [], "stable": [], "safe": []}
    for _, row in df.iterrows():
        item = {
            "dwdm": row["dwdm"],
            "dwmc": row["dwmc"],
            "szss": row["szss"],
            "zhx": row["zhx"],
            "bs": row["bs"],
            "syl": row["syl"],
            "xxfs": row["xxfs"],
            "score": round(float(row["total_score"]), 2),
            "tier": row["tier"],
            "tier_label": row["tier_label"],
        }
        result[row["tier"]].append(item)

    # ========== 第八步：保存推荐记录到数据库 ==========
    for tier_name, items in result.items():
        for item in items:
            log = RecommendLog(
                user_id=user.id,
                zydm=zydm,
                dwdm=item["dwdm"] or "",
                dwmc=item["dwmc"],
                score=item["score"],
                tier=tier_name,
                request_params=json.dumps(
                    {"zydm": zydm, "self_rating": self_rating},
                    ensure_ascii=False,
                ),
            )
            db.add(log)
    db.commit()

    return result
