"""
用户收藏模型 (Favorite)
记录用户收藏的院校-专业组合，用于"我的工作台"中的收藏夹功能。
"""

from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint, func
from app.core.database import Base


class Favorite(Base):
    """用户收藏表"""

    __tablename__ = "favorite"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    dwdm = Column(String(20), nullable=False, comment="院校代码")
    dwmc = Column(String(200), nullable=True, comment="院校名称")
    zydm = Column(String(20), nullable=False, comment="专业代码")
    zymc = Column(String(100), nullable=True, comment="专业名称")
    created_at = Column(DateTime, server_default=func.now(), comment="收藏时间")

    __table_args__ = (
        UniqueConstraint("user_id", "dwdm", "zydm", name="uk_user_fav"),
        {"comment": "用户收藏表"},
    )
