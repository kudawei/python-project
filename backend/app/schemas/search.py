"""
检索相关的请求/响应数据模型
"""

from pydantic import BaseModel
from typing import Optional


class CascadeOption(BaseModel):
    """级联选择器的选项"""
    value: str
    label: str


class UniversityItem(BaseModel):
    """院校列表项"""
    id: int
    dwdm: Optional[str] = None
    dwmc: Optional[str] = None
    szss: Optional[str] = None
    zhx: Optional[str] = None
    bs: Optional[str] = None
    syl: Optional[str] = None
    xxfs: Optional[str] = None
    tydxs: Optional[str] = None
    jsggjh: Optional[str] = None
    zydm: Optional[str] = None
    zymc: Optional[str] = None

    model_config = {"from_attributes": True}


class SearchRequest(BaseModel):
    """高级检索请求参数"""
    zydm: str
    szss: Optional[list[str]] = None
    syl: Optional[bool] = None
    zhx: Optional[bool] = None
    bs: Optional[bool] = None
    xxfs: Optional[str] = None
    page: int = 1
    page_size: int = 10


class SearchResponse(BaseModel):
    """检索结果分页响应"""
    total: int
    page: int
    page_size: int
    items: list[UniversityItem]
