# backend/app/core/session/providers/base.py
from abc import ABC, abstractmethod
from typing import ClassVar, Dict, Type
import requests


class SubsystemSessionProvider(ABC):
    """
    子系统 Session 获取策略基类（自动注册）

    使用方式:
    class JWCSessionProvider(SubsystemSessionProvider, subsystem_name="jwc"):
        def fetch_session(self, castgc: str) -> requests.Session:
            ...
    """

    _registry: ClassVar[Dict[str, Type["SubsystemSessionProvider"]]] = {}

    def __init_subclass__(cls, subsystem_name: str = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if subsystem_name:
            cls._registry[subsystem_name] = cls

    @classmethod
    def get_provider(cls, subsystem_name: str) -> "SubsystemSessionProvider":
        """获取指定子系统的 session provider"""
        provider_class = cls._registry.get(subsystem_name)
        if not provider_class:
            raise ValueError(f"未找到子系统 {subsystem_name} 的处理策略，请检查是否已注册")
        return provider_class()

    @classmethod
    def list_registered_providers(cls) -> list:
        """列出所有已注册的子系统"""
        return list(cls._registry.keys())

    @abstractmethod
    def fetch_session(self, castgc: str) -> requests.Session:
        """
        核心抽象方法：输入 CASTGC，输出带着子系统有效凭证的 requests.Session

        Args:
            castgc: CAS 登录成功后获取的 CASTGC cookie

        Returns:
            带着子系统有效 session 的 requests.Session
        """
        pass
