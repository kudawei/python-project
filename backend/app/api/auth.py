"""
用户认证与画像管理 API
提供注册、登录、获取/更新用户画像等接口。
"""

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, get_current_user
from app.models.user import User
from app.schemas.user import (
    UserRegister,
    UserLogin,
    TokenResponse,
    UserProfile,
    UserInfoResponse,
)

router = APIRouter(prefix="/auth", tags=["用户认证"])


@router.post("/register", response_model=TokenResponse, summary="用户注册")
def register(body: UserRegister, db: Session = Depends(get_db)):
    """
    用户注册接口
    1. 检查用户名是否已被注册
    2. 对密码进行 bcrypt 哈希
    3. 创建用户记录
    4. 返回 JWT Token
    """
    # 检查用户名是否已存在
    existing = db.query(User).filter(User.username == body.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户名已被注册",
        )

    # 创建新用户
    user = User(
        username=body.username,
        hashed_password=hash_password(body.password),
        nickname=body.nickname,
        email=body.email,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # 生成 JWT Token
    token = create_access_token(data={"sub": user.username})

    return TokenResponse(
        access_token=token,
        user_id=user.id,
        username=user.username,
        profile_completed=user.profile_completed,
    )


@router.post("/login", response_model=TokenResponse, summary="用户登录")
def login(body: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录接口
    1. 根据用户名查找用户
    2. 验证密码
    3. 返回 JWT Token
    """
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    token = create_access_token(data={"sub": user.username})

    return TokenResponse(
        access_token=token,
        user_id=user.id,
        username=user.username,
        profile_completed=user.profile_completed,
    )


@router.get("/me", response_model=UserInfoResponse, summary="获取当前用户信息")
def get_user_info(current_user: User = Depends(get_current_user)):
    """获取当前登录用户的详细信息，包含画像数据"""
    # 解析 JSON 字符串类型的省市列表
    provinces = None
    if current_user.target_provinces:
        try:
            provinces = json.loads(current_user.target_provinces)
        except (json.JSONDecodeError, TypeError):
            provinces = None

    return UserInfoResponse(
        id=current_user.id,
        username=current_user.username,
        nickname=current_user.nickname,
        email=current_user.email,
        target_mldm=current_user.target_mldm,
        target_mlmc=current_user.target_mlmc,
        target_provinces=provinces,
        degree_type=current_user.degree_type,
        study_mode=current_user.study_mode,
        self_rating=current_user.self_rating,
        profile_completed=current_user.profile_completed,
    )


@router.put("/profile", summary="更新用户考研意向画像")
def update_profile(
    body: UserProfile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    更新用户考研意向画像
    用户初次登录时或在个人中心修改考研意向。
    """
    current_user.target_mldm = body.target_mldm
    current_user.target_mlmc = body.target_mlmc
    current_user.degree_type = body.degree_type
    current_user.study_mode = body.study_mode
    current_user.self_rating = body.self_rating

    # 将省市列表序列化为 JSON 字符串存储
    if body.target_provinces is not None:
        current_user.target_provinces = json.dumps(body.target_provinces, ensure_ascii=False)

    # 标记画像已完成
    current_user.profile_completed = 1

    db.commit()
    return {"message": "画像更新成功"}
