"""
API 依赖注入
"""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.security import jwt_manager

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> dict:
    """
    从 JWT 获取当前用户信息（必需认证）

    如果 token 无效或过期，返回 401 错误
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = jwt_manager.decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """
    可选的用户认证

    有 token 则解析，无 token 则返回 None
    适用于公开接口但支持登录用户获取更多功能
    """
    if credentials is None:
        return None

    token = credentials.credentials
    return jwt_manager.decode_token(token)
