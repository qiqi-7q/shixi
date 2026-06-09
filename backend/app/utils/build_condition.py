from typing import Any, Type

from app.core.config import settings


def build_condition(model_class: Type, field_name: str, operator: str, value: Any):
    # 构建查询条件
    field = getattr(model_class, field_name)
    op_func = settings.ADVANCED_OPERATORS_MAP.get(
        operator, settings.ADVANCED_OPERATORS_MAP["eq"]
    )
    return op_func(field, value)
