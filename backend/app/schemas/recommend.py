"""
推荐相关的请求/响应数据模型
"""

from pydantic import BaseModel
from typing import Optional


class RecommendRequest(BaseModel):
    """推荐请求参数"""
    zydm: str


class RecommendItem(BaseModel):
    """单条推荐结果"""
    dwdm: Optional[str] = None
    dwmc: Optional[str] = None
    szss: Optional[str] = None
    zhx: Optional[str] = None
    bs: Optional[str] = None
    syl: Optional[str] = None
    xxfs: Optional[str] = None
    score: float
    tier: str
    tier_label: str

    model_config = {"from_attributes": True}


class RecommendResponse(BaseModel):
    """推荐结果分组响应"""
    sprint: list[RecommendItem]
    stable: list[RecommendItem]
    safe: list[RecommendItem]
