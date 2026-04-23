"""
推荐记录模型 (RecommendLog)
记录每次推荐算法的执行结果，用于后续分析推荐效果和调优。
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, func
from app.core.database import Base


class RecommendLog(Base):
    """推荐记录表"""

    __tablename__ = "recommend_log"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    zydm = Column(String(20), nullable=False, comment="推荐使用的专业代码")
    dwdm = Column(String(20), nullable=False, comment="被推荐的院校代码")
    dwmc = Column(String(200), nullable=True, comment="被推荐的院校名称")
    score = Column(Float, nullable=True, comment="推荐得分")
    tier = Column(String(20), nullable=True, comment="推荐层级: sprint=冲刺, stable=稳妥, safe=保底")
    created_at = Column(DateTime, server_default=func.now(), comment="推荐时间")
    request_params = Column(Text, nullable=True, comment="请求参数快照(JSON)")

    __table_args__ = ({"comment": "推荐记录表"},)
