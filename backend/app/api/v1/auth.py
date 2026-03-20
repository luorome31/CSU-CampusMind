"""
认证 API - 登录/登出接口
"""
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel

from app.config import settings
from app.core.security import jwt_manager
from app.core.session.manager import UnifiedSessionManager, NeedReLoginError
from app.core.session.factory import get_session_manager
from app.core.session.rate_limiter import LoginRateLimiter
from app.api.dependencies import get_current_user
from app.database.session import async_session_dependency

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["认证"])


# ============ Helper Functions ============

async def _ensure_user_exists(user_id: str) -> None:
    """
    如果用户不存在则创建

    Args:
        user_id: 用户 ID (CAS username)
    """
    from app.database.models import User

    session = async_session_dependency()
    existing = await session.get(User, user_id)
    if not existing:
        user = User(id=user_id, username=user_id)
        session.add(user)
        await session.commit()


# ============ Request/Response Models ============

class LoginRequest(BaseModel):
    """登录请求"""
    username: str  # 学号
    password: str


class LoginResponse(BaseModel):
    """登录响应"""
    token: str
    user_id: str
    expires_in: int  # 秒


class LogoutRequest(BaseModel):
    """登出请求"""
    user_id: str


# ============ 速率限制器 ============

_rate_limiter = LoginRateLimiter()


# ============ API Endpoints ============

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    用户登录接口

    流程：
    1. 检查登录频率
    2. 调用 CAS 登录获取 CASTGC
    3. 存储 CASTGC
    4. 生成 JWT 返回
    """
    # 1. 登录频率检查
    if not _rate_limiter.can_login(request.username):
        wait_time = _rate_limiter.get_wait_time(request.username)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"登录过于频繁，请等待 {wait_time:.0f} 秒后再试"
        )

    # 2. 获取 session manager
    session_manager = get_session_manager()

    # 3. CAS 登录获取 CASTGC
    try:
        await session_manager.login(
            user_id=request.username,
            username=request.username,
            password=request.password
        )
    except AccountLockedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"登录失败: {str(e)}"
        )
    except CASLoginError as e:
        logger.error(f"CAS login failed for {request.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"登录失败: {str(e)}"
        )

    # 登录成功后确保用户存在
    await _ensure_user_exists(request.username)

    # 4. 生成 JWT
    token = jwt_manager.create_token({"user_id": request.username})

    logger.info(f"User {request.username} logged in successfully")

    return LoginResponse(
        token=token,
        user_id=request.username,
        expires_in=settings.jwt_expire_hours * 3600
    )


# 导入异常类供本模块使用
from app.core.session.cas_login import AccountLockedError, CASLoginError


@router.post("/logout")
async def logout(
    request: LogoutRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    用户登出接口

    清除用户的 CASTGC 和所有子系统 session
    """
    # 验证权限：只能登出自己的账号
    if current_user.get("user_id") != request.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限操作"
        )

    # 清除 session（包括 CASTGC）
    session_manager = get_session_manager()
    session_manager.invalidate_session(request.user_id)

    logger.info(f"User {request.user_id} logged out")

    return {"message": "登出成功"}


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """
    刷新 JWT token

    注意：刷新 token 不需要重新登录 CAS，CASTGC 仍然有效
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录"
        )

    user_id = current_user["user_id"]
    new_token = jwt_manager.create_token({"user_id": user_id})

    return LoginResponse(
        token=new_token,
        user_id=user_id,
        expires_in=settings.jwt_expire_hours * 3600
    )
