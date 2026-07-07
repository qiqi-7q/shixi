from pathlib import Path

app_root = Path(__file__).parent.parent


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

            module_name = f"app.plugins.{plugin_dir.name}.models"
            __import__(module_name)
