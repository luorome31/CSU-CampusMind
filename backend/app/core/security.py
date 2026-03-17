"""
JWT 令牌管理模块
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import jwt

from app.config import settings

logger = logging.getLogger(__name__)


class JWTManager:
    """JWT 令牌管理类"""

    def __init__(
        self,
        secret_key: Optional[str] = None,
        algorithm: str = "HS256"
    ):
        self.secret_key = secret_key or settings.jwt_secret_key
        self.algorithm = algorithm

        # 检查是否使用默认密钥，用于开发环境
        default_secret = "your-secret-key-change-in-production"
        if self.secret_key == default_secret:
            logger.warning(
                "安全警告: 使用默认 JWT 密钥，请在生产环境中设置自定义密钥!"
            )

    def create_token(
        self,
        payload: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """创建 JWT token"""
        to_encode = payload.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=settings.jwt_expire_hours)

        to_encode.update({"exp": expire})

        try:
            encoded = jwt.encode(
                to_encode,
                self.secret_key,
                algorithm=self.algorithm
            )
        except Exception as e:
            logger.error(f"创建 JWT token 失败: {e}")
            raise

        return encoded

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """解码 JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token 已过期")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"JWT token 无效: {e}")
            return None

    def verify_token(self, token: str) -> bool:
        """验证 token 是否有效"""
        return self.decode_token(token) is not None


# 全局实例
jwt_manager = JWTManager()
