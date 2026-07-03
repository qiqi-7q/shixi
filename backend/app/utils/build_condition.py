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


def check_comma_separated_in(field, operator: str, value: str):
    """检查是否为逗号分隔多选，如果是则返回 IN/NOT IN 条件，否则返回 None"""
    if "," in value:
        values = [v.strip() for v in value.split(",") if v.strip()]
        if values:
            if operator == "eq":
                return field.in_(values)
            else:
                return ~field.in_(values)
    return None


def build_condition(model_class: Type, field_name: str, operator: str, value: Any):
    field = getattr(model_class, field_name)
    op_func = settings.ADVANCED_OPERATORS_MAP.get(
        operator, settings.ADVANCED_OPERATORS_MAP["eq"]
    )

    # 枚举字段映射表
    ENUM_FIELD_MAP = {
        "test_status": "TestStatus",
        "vehicle_status": "VehicleStatus",
        "group": "VehicleGroup",
    }

    if field_name in ENUM_FIELD_MAP:
        # 多选支持：逗号分隔的值转为 IN/NOT IN 查询
        comma_result = check_comma_separated_in(field, operator, value)
        if comma_result is not None:
            return comma_result
        # 单选：解析枚举值
        enum_class_name = ENUM_FIELD_MAP[field_name]
        if hasattr(models, enum_class_name):
            enum_cls = getattr(models, enum_class_name)
            enum_val = getattr(enum_cls, value, None) or find_enum_by_value(
                enum_cls, value
            )
            if enum_val:
                value = enum_val
    elif (
        operator in ("eq", "not_eq")
        and value is not None
        and not isinstance(value, list)
    ):
        # 多选支持：逗号分隔的字符串转为 IN/NOT IN 查询
        if isinstance(value, str):
            comma_result = check_comma_separated_in(field, operator, value)
            if comma_result is not None:
                return comma_result
        # 等于/不等于统一转字符串，避免 Date/Integer 与字符串类型不匹配
        # between/not_between 的 value 是数组，不转换
        value = str(value)

    return op_func(field, value)