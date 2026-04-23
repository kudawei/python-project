"""
用户相关的请求/响应数据模型
"""

from pydantic import BaseModel
from typing import Optional


class UserRegister(BaseModel):
    """用户注册请求体"""
    username: str
    password: str
    nickname: Optional[str] = None
    email: Optional[str] = None


class UserLogin(BaseModel):
    """用户登录请求体"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """登录成功后返回的 Token 响应"""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    profile_completed: int


class UserProfile(BaseModel):
    """用户画像（考研意向问卷）"""
    target_mldm: Optional[str] = None
    target_mlmc: Optional[str] = None
    target_provinces: Optional[list[str]] = None
    degree_type: Optional[str] = None
    study_mode: Optional[str] = None
    self_rating: Optional[str] = None


class UserInfoResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    nickname: Optional[str] = None
    email: Optional[str] = None
    target_mldm: Optional[str] = None
    target_mlmc: Optional[str] = None
    target_provinces: Optional[list[str]] = None
    degree_type: Optional[str] = None
    study_mode: Optional[str] = None
    self_rating: Optional[str] = None
    profile_completed: int

    model_config = {"from_attributes": True}
