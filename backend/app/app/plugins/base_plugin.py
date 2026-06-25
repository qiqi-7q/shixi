from abc import ABC, abstractmethod
from fastapi import FastAPI


class BasePlugin(ABC):
    """插件基类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """插件名称"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """插件版本"""
        pass

    @abstractmethod
    def register(self, app: FastAPI):
        """注册插件路由和功能"""
        pass

    def on_startup(self):
        """插件启动时的操作"""
        pass

    def on_shutdown(self):
        """插件关闭时的操作"""
        pass