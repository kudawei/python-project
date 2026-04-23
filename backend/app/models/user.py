"""
用户模型 (User)
存储注册用户的基本信息和考研意向画像数据。
画像字段用于智能推荐算法的个性化匹配。
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, func
from app.core.database import Base


class User(Base):
    """用户表 —— 包含认证信息与考研意向画像"""

    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    hashed_password = Column(String(255), nullable=False, comment="哈希后的密码")
    nickname = Column(String(50), nullable=True, comment="昵称")
    email = Column(String(100), nullable=True, comment="邮箱")

    # -------- 考研意向画像字段 --------
    target_mldm = Column(String(10), nullable=True, comment="意向门类代码")
    target_mlmc = Column(String(50), nullable=True, comment="意向门类名称")
    target_provinces = Column(Text, nullable=True, comment="意向省市列表(JSON数组，如[\"北京\",\"上海\"])")
    degree_type = Column(String(10), nullable=True, comment="学位期望: xs=学术学位, zy=专业学位")
    study_mode = Column(String(10), nullable=True, comment="学习方式期望: 1=全日制, 2=非全日制")
    self_rating = Column(String(10), nullable=True, comment="自身实力自评: weak=弱, medium=中等, strong=强")
    profile_completed = Column(Integer, default=0, comment="画像是否已完成: 0=未完成, 1=已完成")

    created_at = Column(DateTime, server_default=func.now(), comment="注册时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    __table_args__ = ({"comment": "用户表"},)
