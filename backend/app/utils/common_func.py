def format_plugin_name(plugin_name: str) -> str:
    """
    将 test_record → TestRecord
    1. 按下划线分割
    2. 每个单词首字母大写
    3. 拼接
    """
    if "_" in plugin_name:
        # 按下划线分割成列表: ['test', 'record']
        words = plugin_name.split("_")
        # 每个单词首字母大写: ['Test', 'Record']
        capitalized_words = [word.capitalize() for word in words]
        # 拼接
        return "".join(capitalized_words)
    # 没有下划线则首字母大写
    return plugin_name.capitalize()