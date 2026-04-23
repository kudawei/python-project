"""
专业-院校关联模型 (MajorUniversity)
对应数据库表 `major_university`，记录每个专业在各院校的招生信息，
包括院校属性（双一流、自划线、博士点等）和招生政策。
"""

from sqlalchemy import Column, Integer, String, Index
from app.core.database import Base


class MajorUniversity(Base):
    """专业-院校关联表"""

    __tablename__ = "major_university"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    zydm = Column(String(20), nullable=False, comment="专业代码")
    zymc = Column(String(100), nullable=True, comment="专业名称")
    mldm = Column(String(10), nullable=True, comment="门类代码")
    mlmc = Column(String(50), nullable=True, comment="门类名称")
    yjxkdm = Column(String(20), nullable=True, comment="一级学科代码")
    yjxkmc = Column(String(100), nullable=True, comment="一级学科名称")
    xwlx = Column(String(10), nullable=True, comment="学位类型")
    xwlxmc = Column(String(20), nullable=True, comment="学位类型名称")
    sch_id = Column(String(20), nullable=True, comment="院校ID")
    dwdm = Column(String(20), nullable=True, comment="院校代码")
    dwmc = Column(String(200), nullable=True, comment="院校名称")
    szssm = Column(String(10), nullable=True, comment="省市代码")
    szss = Column(String(50), nullable=True, comment="省市名称")
    zhx = Column(String(5), nullable=True, comment="是否自划线院校(是/否)")
    bs = Column(String(5), nullable=True, comment="是否有博士点(是/否)")
    syl = Column(String(5), nullable=True, comment="是否双一流(是/否)")
    xxfs = Column(String(20), nullable=True, comment="学习方式(全日制/非全日制)")
    tydxs = Column(String(5), nullable=True, comment="是否接收退役大学生士兵计划")
    jsggjh = Column(String(5), nullable=True, comment="是否接收少数民族骨干计划")

    __table_args__ = (
        Index("idx_zydm", "zydm"),
        Index("idx_dwdm", "dwdm"),
        Index("idx_dwmc", "dwmc"),
        {"comment": "专业-院校关联表"},
    )
