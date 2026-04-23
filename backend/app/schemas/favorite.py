"""
收藏与对比相关的请求/响应数据模型
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FavoriteCreate(BaseModel):
    """添加收藏请求体"""
    dwdm: str
    dwmc: Optional[str] = None
    zydm: str
    zymc: Optional[str] = None


class FavoriteItem(BaseModel):
    """收藏列表项"""
    id: int
    dwdm: str
    dwmc: Optional[str] = None
    zydm: str
    zymc: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CompareRequest(BaseModel):
    """院校对比请求：传入 2-3 个院校代码"""
    dwdm_list: list[str]
    zydm: str


class CompareItem(BaseModel):
    """对比项数据"""
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
    b985: Optional[str] = None
    b211: Optional[str] = None
    yjsy: Optional[str] = None
    yxsmc: Optional[str] = None
    yjfxmc: Optional[str] = None
    zdjs: Optional[str] = None
    nzsrs: Optional[int] = None
    km1mc: Optional[str] = None
    km2mc: Optional[str] = None
    km3mc: Optional[str] = None
    km4mc: Optional[str] = None

    model_config = {"from_attributes": True}
