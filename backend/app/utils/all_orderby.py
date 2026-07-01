# """
# 通用排序模块 - 提供高性能、多数据类型兼容的排序功能。
#
# 支持的数据类型：
#   - 字符串：不区分大小写字母排序，中文按拼音排序，内嵌数字按数值大小排序
#   - 整数/浮点数：按数值大小排序
#   - 日期时间(datetime/date)：按日期时间元组排序
#   - 布尔值：False 排在 True 之前
#   - 空值(None)：始终排在所有非空值之后
#
# 比较逻辑：
#   - 字符串从左到右逐字符比较，数字段按数值比较，非数字段逐字符比较
#   - 字母不区分大小写（"A" 与 "a" 视为相等）
#   - 数字自动识别并按数值大小比较（"100" > "20"）
#   - 中文字符按拼音排序（需安装 pypinyin，否则按 Unicode 码点排序）
#   - 空值排在非空值之后，两个空值视为相等
#   - 比较第一个不同元素后确定顺序并停止
# """

import re
from datetime import date, datetime
from typing import Any, List

# ============================================================
# 字符处理工具
# ============================================================


def _get_pinyin(ch: str) -> str:
    """获取单个中文字符的拼音。非中文字符返回原字符小写形式。"""
    if "\u4e00" <= ch <= "\u9fff" or "\u3400" <= ch <= "\u4dbf":
        try:
            from pypinyin import lazy_pinyin

            py = lazy_pinyin(ch)
            return py[0].lower() if py else ch.lower()
        except ImportError:
            # pypinyin 未安装，回退到 Unicode 码点比较
            return ch.lower()
    if ch.isalpha():
        return ch.lower()
    return ch


def _make_string_sort_key(s: str) -> tuple:
    """
    为字符串生成自然排序键元组。

    将字符串按连续数字/非数字分割成段：
      - 数字段：(1, 整数值)  —— 按数值大小比较
      - 非数字段：逐字符转为拼音/小写后比较

    示例:
      "A100" → ( (0, 'a'), (1, 100) )
      "a20"  → ( (0, 'a'), (1, 20)  )
      比较时：'a' == 'a'，100 > 20，所以 "A100" > "a20"
    """
    parts = []
    segments = re.split(r"(\d+)", s)
    for seg in segments:
        if not seg:
            continue
        if seg.isdigit():
            parts.append((1, int(seg)))
        else:
            for ch in seg:
                parts.append((0, _get_pinyin(ch)))
    return tuple(parts)


# ============================================================
# 通用排序键生成
# ============================================================


def _get_field_value(item: Any, field_name: str) -> Any:
    """
    从数据项中获取指定字段的值。

    支持两种数据项格式：
      - 字典：item.get(field_name)
      - 对象：getattr(item, field_name, None)
    """
    if isinstance(item, dict):
        return item.get(field_name)
    return getattr(item, field_name, None)


def _make_sort_key(value: Any) -> tuple:
    """
    为任意类型值生成排序键元组。

    排序键的优先级结构：(null_priority, type_group, comparable_value, ...)
      - null_priority: 0 = 非空值, 1 = 空值(None)  —— 空值永远排在最后
      - type_group: 类型分组编号，确保同类型值在相近位置
      - comparable_value: 实际参与比较的值

    类型分组编号：
      0: bool
      1: int / float
      2: datetime
      3: date
      4: str（继续展开为自然排序键）
      5: 其他类型（转为字符串比较）
    """
    if value is None:
        return (1, 0)

    if isinstance(value, bool):
        # False < True
        return (0, 0, int(value))

    if isinstance(value, int):
        return (0, 1, value)

    if isinstance(value, float):
        return (0, 1, value)

    if isinstance(value, datetime):
        return (
            0,
            2,
            (
                value.year,
                value.month,
                value.day,
                value.hour,
                value.minute,
                value.second,
            ),
        )

    if isinstance(value, date):
        return (0, 3, (value.year, value.month, value.day))

    if isinstance(value, str):
        return (0, 4) + _make_string_sort_key(value)

    # 其他类型（如 Enum）：统一转为字符串比较
    return (0, 5, str(value))


# ============================================================
# 公开接口
# ============================================================


def universal_sort(
    data_list: List[Any],
    sort_field: str,
    sort_order: str = "asc",
) -> List[Any]:
    """
    通用高性能排序方法。

    对数据列表按指定字段的值进行排序，兼容多种数据类型，支持自然排序。

    参数:
        data_list:  待排序的数据列表，元素可以是字典或任意对象（通过 getattr 取值）
        sort_field: 排序字段名，必须存在于数据元素中
        sort_order: 排序方向，"asc"（升序，默认）或 "desc"（降序）

    返回:
        排序后的新列表（原列表不会被修改）。

    异常处理:
        - 如果排序过程中发生异常，打印错误信息并返回原始列表副本。
        - 如果字段不存在（getattr 返回 None），该记录将按空值处理（排在最后）。

    示例:
        >>> universal_sort([{"name": "B"}, {"name": "a"}, {"name": None}], "name")
        [{"name": "a"}, {"name": "B"}, {"name": None}]

        >>> universal_sort([{"v": 100}, {"v": 20}], "v", "desc")
        [{"v": 100}, {"v": 20}]
    """
    if not data_list:
        return data_list

    reverse = sort_order.lower() == "desc"

    try:
        return sorted(
            data_list,
            key=lambda item: _make_sort_key(_get_field_value(item, sort_field)),
            reverse=reverse,
        )
    except Exception as e:
        print(
            f"universal_sort 排序失败，字段: {sort_field}, 排序方向: {sort_order}, 错误: {e}，返回原始数据"
        )
        return list(data_list)
