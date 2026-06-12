from typing import Any, Type

from app.core.config import settings
from app.plugins.vehicle_plugin import models


def _find_enum_by_value(enum_class, value: str):
    """根据值查找枚举成员（支持中文值查找）"""
    for member in enum_class:
        if member.value == value:
            return member
    return None


def build_condition(model_class: Type, field_name: str, operator: str, value: Any):
    # 构建查询条件
    field = getattr(model_class, field_name)
    op_func = settings.ADVANCED_OPERATORS_MAP.get(
        operator, settings.ADVANCED_OPERATORS_MAP["eq"]
    )
    
    # 处理枚举字段：支持英文枚举名和中文值两种方式
    if field_name == "test_status" and hasattr(models, "TestStatus"):
        # 先尝试按英文枚举名查找
        test_status_enum = getattr(models.TestStatus, value, None)
        if not test_status_enum:
            # 再尝试按中文值查找
            test_status_enum = _find_enum_by_value(models.TestStatus, value)
        if test_status_enum:
            value = test_status_enum
            
    elif field_name == "vehicle_status" and hasattr(models, "VehicleStatus"):
        # 先尝试按英文枚举名查找
        vehicle_status_enum = getattr(models.VehicleStatus, value, None)
        if not vehicle_status_enum:
            # 再尝试按中文值查找
            vehicle_status_enum = _find_enum_by_value(models.VehicleStatus, value)
        if vehicle_status_enum:
            value = vehicle_status_enum
            
    elif field_name == "group" and hasattr(models, "VehicleGroup"):
        # 先尝试按英文枚举名查找
        group_enum = getattr(models.VehicleGroup, value, None)
        if not group_enum:
            # 再尝试按中文值查找
            group_enum = _find_enum_by_value(models.VehicleGroup, value)
        if group_enum:
            value = group_enum
    
    return op_func(field, value)
