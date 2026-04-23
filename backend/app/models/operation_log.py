"""
操作日志模型 (OperationLog)
记录用户在系统中的关键操作，便于追踪和审计。
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, func
from app.core.database import Base


class OperationLog(Base):
    """操作日志表"""

    __tablename__ = "operation_log"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    username = Column(String(50), nullable=True, comment="用户名")
    action = Column(String(50), nullable=False, comment="操作类型: login/search/recommend/favorite/compare/export等")
    detail = Column(Text, nullable=True, comment="操作详情(JSON)")
    ip_address = Column(String(50), nullable=True, comment="操作IP地址")
    created_at = Column(DateTime, server_default=func.now(), comment="操作时间")

    __table_args__ = ({"comment": "操作日志表"},)
