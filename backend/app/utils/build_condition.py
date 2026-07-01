from typing import Any, Type

from app.core.config import settings
from app.plugins.vehicle_plugin import models

# ========================高级搜索条件构建========================


def find_enum_by_value(enum_class, value: str):
    """根据值查找枚举成员（支持中文值查找）"""
    for member in enum_class:
        if member.value == value:
            return member
    return None


def build_condition(model_class: Type, field_name: str, operator: str, value: Any):
    field = getattr(model_class, field_name)
    op_func = settings.ADVANCED_OPERATORS_MAP.get(
        operator, settings.ADVANCED_OPERATORS_MAP["eq"]
    )

    # 枚举字段：支持英文枚举名和中文值
    if field_name == "test_status" and hasattr(models, "TestStatus"):
        enum_val = getattr(models.TestStatus, value, None) or find_enum_by_value(
            models.TestStatus, value
        )
        if enum_val:
            value = enum_val
    elif field_name == "vehicle_status" and hasattr(models, "VehicleStatus"):
        enum_val = getattr(models.VehicleStatus, value, None) or find_enum_by_value(
            models.VehicleStatus, value
        )
        if enum_val:
            value = enum_val
    elif field_name == "group" and hasattr(models, "VehicleGroup"):
        enum_val = getattr(models.VehicleGroup, value, None) or find_enum_by_value(
            models.VehicleGroup, value
        )
        if enum_val:
            value = enum_val
    elif (
        operator in ("eq", "not_eq")
        and value is not None
        and not isinstance(value, list)
    ):
        # 等于/不等于统一转字符串，避免 Date/Integer 与字符串类型不匹配
        # between/not_between 的 value 是数组，不转换
        value = str(value)

    return op_func(field, value)
