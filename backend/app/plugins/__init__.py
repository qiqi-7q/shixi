from pathlib import Path
import importlib



# 当前文件往上两级为项目根目录
app_root = Path(__file__).parent.parent


def auto_import_plugin_models():
    """自动扫描plugins下所有插件的models.py并导入，注册ORM模型"""
    plugins_dir = app_root / "plugins"
    if not plugins_dir.exists():
        return

    # 遍历插件目录
    for plugin_dir in plugins_dir.iterdir():
        # 跳过非文件夹、隐藏目录、缓存目录
        if not plugin_dir.is_dir() or plugin_dir.name.startswith((".", "__")):
            continue

        models_file = plugin_dir / "models.py"
        if not models_file.exists():
            continue

        module_name = f"app.plugins.{plugin_dir.name}.models"
        try:
            # 标准动态导入
            importlib.import_module(module_name)
        except Exception as e:
            # 捕获插件模型加载异常，不阻断整体启动
            print(f"插件 {plugin_dir.name} models.py 导入失败: {str(e)}")