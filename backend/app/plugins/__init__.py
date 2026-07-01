from pathlib import Path

app_root = Path(__file__).parent.parent


# 2. 动态扫描 plugins 下所有插件的 models.py
def auto_import_plugin_models():
    plugins_dir = app_root / "plugins"
    if not plugins_dir.exists():
        return
    # 遍历插件文件夹
    for plugin_dir in plugins_dir.iterdir():
        if not plugin_dir.is_dir():
            continue
        models_file = plugin_dir / "models.py"
        if models_file.exists():
            # 拼接模块路径 app.plugins.xxx_plugin.models
            module_name = f"app.plugins.{plugin_dir.name}.models"
            __import__(module_name)
