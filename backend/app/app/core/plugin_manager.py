from importlib import import_module
from typing import Any, Dict, List

from fastapi import FastAPI


class PluginManager:
    def __init__(self):
        self.plugins: Dict[str, Any] = {}
        self.app: FastAPI = None  # type: ignore

    def init_app(self, app: FastAPI):
        """初始化插件管理器"""
        self.app = app

    async def register_plugin(self, plugin_name: str, plugin_module: str):
        """注册插件"""
        try:
            module = import_module(plugin_module)
            if "_" in plugin_name:
                # 按下划线分割成列表: ['test', 'record']
                words = plugin_name.split("_")
                # 每个单词首字母大写: ['Test', 'Record']
                capitalized_words = [word.capitalize() for word in words]
                # 拼接
                plugin_name = "".join(capitalized_words)
            else:
                plugin_name = plugin_name.capitalize()

            plugin_class = getattr(module, f"{plugin_name}Plugin")
            plugin_instance = plugin_class()

            if hasattr(plugin_instance, "register"):
                await plugin_instance.register(self.app)

            self.plugins[plugin_name] = plugin_instance
            print(f"Plugin '{plugin_name}' registered successfully")
        except Exception as e:
            print(f"Failed to register plugin '{plugin_name}': {e}")

    def get_plugin(self, plugin_name: str):
        """获取插件实例"""
        return self.plugins.get(plugin_name)

    def list_plugins(self) -> List[str]:
        """列出所有已注册的插件"""
        return list(self.plugins.keys())


plugin_manager = PluginManager()
