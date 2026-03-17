"""
认证 API - 登录/登出接口
"""
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel

from app.config import settings
from app.core.security import jwt_manager
from app.core.session.manager import UnifiedSessionManager
from app.core.session.factory import get_session_manager
from app.core.session.rate_limiter import LoginRateLimiter
from app.api.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["认证"])


# ============ Request/Response Models ============

class LoginRequest(BaseModel):
    """登录请求"""
    username: str  # 学号
    password: str
    subsystem: str = "jwc"  # 默认教务系统


class LoginResponse(BaseModel):
    """登录响应"""
    token: str
    user_id: str
    expires_in: int  # 秒


class LogoutRequest(BaseModel):
    """登出请求"""
    user_id: str


class RefreshRequest(BaseModel):
    """刷新 token 请求"""
    pass


# ============ 速率限制器 ============

_rate_limiter = LoginRateLimiter()


# ============ API Endpoints ============

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    用户登录接口

    流程：
    1. 检查登录频率
    2. 调用 CAS 登录获取子系统 session
    3. 存储 subsystem session
    4. 生成 JWT 返回
    """
    # 1. 登录频率检查
    try:
        _rate_limiter.check(request.username)
    except Exception as e:
        logger.warning(f"Login rate limit exceeded for {request.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"登录过于频繁，请稍后再试: {str(e)}"
        )

    # 2. 获取 session manager
    session_manager = get_session_manager()

    # 3. 调用 CAS 登录
    try:
        from app.core.session import cas_login
        from app.core.session.manager import SUBSYSTEM_SERVICE_URLS

        service_url = SUBSYSTEM_SERVICE_URLS.get(request.subsystem)
        if not service_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"未知的子系统: {request.subsystem}"
            )

        session = cas_login.cas_login(
            request.username,
            request.password,
            service_url,
            _rate_limiter
        )
    except Exception as e:
        logger.error(f"CAS login failed for {request.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"登录失败: {str(e)}"
        )

    # 4. 存储 subsystem session
    try:
        session_manager._cache.set(request.username, request.subsystem, session)
        session_manager._persistence.save(
            request.username,
            request.subsystem,
            session,
            settings.session_ttl_seconds
        )
    except Exception as e:
        logger.error(f"Failed to save session for {request.username}: {e}")
        # 不阻塞登录成功，只是警告

    # 5. 生成 JWT
    token = jwt_manager.create_token({"user_id": request.username})

    logger.info(f"User {request.username} logged in successfully")

    return LoginResponse(
        token=token,
        user_id=request.username,
        expires_in=settings.jwt_expire_hours * 3600
    )


@router.post("/logout")
async def logout(
    request: LogoutRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    用户登出接口

    清除用户的 subsystem session
    """
    # 验证权限：只能登出自己的账号
    if current_user.get("user_id") != request.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限操作"
        )

    # 清除 session
    session_manager = get_session_manager()
    session_manager.invalidate_session(request.user_id)

    logger.info(f"User {request.user_id} logged out")

    return {"message": "登出成功"}


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """
    刷新 JWT token
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
