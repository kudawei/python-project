"""
专业研究方向详情模型 (MajorDetail)
对应数据库表 `major_detail`，存储每个专业在每个院校下的详细招生信息，
包括研究方向、考试科目、招生人数、指导教师等细节。
"""

from sqlalchemy import Column, Integer, String, Text, UniqueConstraint, Index
from app.core.database import Base


class MajorDetail(Base):
    """专业研究方向详情表"""

    __tablename__ = "major_detail"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    zyyjfxdm = Column(String(50), nullable=True, comment="专业研究方向代码")
    zydm = Column(String(20), nullable=False, comment="专业代码")
    zymc = Column(String(100), nullable=True, comment="专业名称")
    mldm = Column(String(10), nullable=True, comment="门类代码")
    mlmc = Column(String(50), nullable=True, comment="门类名称")
    yjxkdm = Column(String(20), nullable=True, comment="一级学科代码")
    yjxkmc = Column(String(100), nullable=True, comment="一级学科名称")
    xwlx = Column(String(10), nullable=True, comment="学位类型 xs/zy")
    xwlxmc = Column(String(20), nullable=True, comment="学位类型名称")
    dwdm = Column(String(20), nullable=False, comment="院校代码")
    dwmc = Column(String(200), nullable=True, comment="院校名称")
    sch_id = Column(String(20), nullable=True, comment="schId")
    szssm = Column(String(10), nullable=True, comment="省市码")
    szss = Column(String(50), nullable=True, comment="省市")
    zhx = Column(String(5), nullable=True, comment="自划线")
    bs = Column(String(5), nullable=True, comment="博士点")
    syl = Column(String(5), nullable=True, comment="双一流")
    b985 = Column(String(5), nullable=True, comment="985")
    b211 = Column(String(5), nullable=True, comment="211")
    yjsy = Column(String(5), nullable=True, comment="研究生院")
    ksfsdm = Column(String(10), nullable=True, comment="考试方式代码")
    ksfsmc = Column(String(50), nullable=True, comment="考试方式名称")
    yxsdm = Column(String(20), nullable=True, comment="院系所代码")
    yxsmc = Column(String(200), nullable=True, comment="院系所名称")
    yjfxdm = Column(String(20), nullable=True, comment="研究方向代码")
    yjfxmc = Column(String(200), nullable=True, comment="研究方向名称")
    zdjs = Column(String(500), nullable=True, comment="指导教师")
    nzsrs = Column(Integer, nullable=True, comment="拟招生人数")
    nzsrsstr = Column(String(200), nullable=True, comment="拟招生人数说明")
    xxfs = Column(String(10), nullable=True, comment="学习方式 1全日制 2非全日制")
    gbfs = Column(String(10), nullable=True, comment="公布方式")
    tydxs = Column(String(10), nullable=True, comment="退役大学生士兵计划")
    jsggjh = Column(String(10), nullable=True, comment="少骨计划")
    ssjstmrs = Column(Integer, nullable=True, comment="招收推免人数")
    ssncszjh = Column(Integer, nullable=True, comment="少骨计划人数")
    cxzrs = Column(Integer, nullable=True, comment="从校招生人数")
    zybz = Column(Text, nullable=True, comment="专业备注")
    km1dm = Column(String(20), nullable=True, comment="科目1代码")
    km1mc = Column(String(100), nullable=True, comment="科目1名称")
    km2dm = Column(String(20), nullable=True, comment="科目2代码")
    km2mc = Column(String(100), nullable=True, comment="科目2名称")
    km3dm = Column(String(20), nullable=True, comment="科目3代码")
    km3mc = Column(String(100), nullable=True, comment="科目3名称")
    km4dm = Column(String(20), nullable=True, comment="科目4代码")
    km4mc = Column(String(100), nullable=True, comment="科目4名称")

    __table_args__ = (
        UniqueConstraint("zyyjfxdm", name="uk_detail"),
        Index("idx_zydm", "zydm"),
        Index("idx_dwdm", "dwdm"),
        Index("idx_dwmc", "dwmc"),
        Index("idx_yxsmc", "yxsmc"),
        Index("idx_yjfxmc", "yjfxmc"),
        {"comment": "专业研究方向详情表"},
    )
