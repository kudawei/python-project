"""
研究生专业信息模型 (Major)
对应数据库表 `major`，存储所有研究生专业的基础信息，
包括专业代码、名称、所属门类、一级学科、学位类型等。
"""

from sqlalchemy import Column, Integer, String, UniqueConstraint
from app.core.database import Base


class Major(Base):
    """研究生专业信息表"""

    __tablename__ = "major"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    zydm = Column(String(20), nullable=False, comment="专业代码")
    zymc = Column(String(100), nullable=False, comment="专业名称")
    mldm = Column(String(10), nullable=True, comment="门类代码")
    mlmc = Column(String(50), nullable=True, comment="门类名称")
    yjxkdm = Column(String(20), nullable=True, comment="一级学科代码")
    yjxkmc = Column(String(100), nullable=True, comment="一级学科名称")
    xwlx = Column(String(10), nullable=True, comment="学位类型: xs=学术学位, zy=专业学位")
    xwlxmc = Column(String(20), nullable=True, comment="学位类型名称")

    __table_args__ = (
        UniqueConstraint("zydm", "xwlx", name="uk_zydm_xwlx"),
        {"comment": "研究生专业信息表"},
    )
