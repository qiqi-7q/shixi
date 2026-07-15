from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import case, select, func
from app.plugins.employee_plugin import models, schemas
from typing import Optional
from app.utils.build_condition import ENUM_FIELD_MAP


async def create_employee(db: AsyncSession, data: schemas.EmployeeCreate):
    # Literal 类型会在 Pydantic 层自动验证，此处无需额外检查
    db_employee = models.Employee(**data.dict())
    db.add(db_employee)
    await db.commit()
    await db.refresh(db_employee)
    return db_employee


async def get_employees_simple(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    name: str = None,
    module_name: str = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None,
):
    stmt = select(models.Employee)
    if name:
        stmt = stmt.where(models.Employee.name.icontains(name))
    if module_name:
        stmt = stmt.where(models.Employee.module_name.icontains(module_name))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt) or 0

    default_sort = "id"
    default_desc = True
    sort_expr = None

    # 处理空排序场景
    if not sort_by:
        sort_by = default_sort
        is_desc = default_desc
    else:
        # 字段白名单校验
        if sort_by not in schemas.EMPLOYEE_WHITELIST:
            sort_by = "id"
        # 校验排序方向
        valid_order = sort_order.lower() if sort_order else "asc"
        is_desc = valid_order == "desc" if valid_order in ("asc", "desc") else False

    # 2. 统一构建排序表达式（消除if/else分页重复代码）
    if sort_by in ENUM_FIELD_MAP:
        # 枚举CASE WHEN排序
        enum_cls = getattr(models, ENUM_FIELD_MAP[sort_by])
        field_col = getattr(models.Employee, sort_by)
        whens = [(field_col == m.value, i) for i, m in enumerate(enum_cls)]
        sort_expr = case(*whens)
    else:
        # 普通字段原生排序
        sort_expr = getattr(models.Employee, sort_by)

    # 升降序统一处理
    order_clause = sort_expr.desc() if is_desc else sort_expr.asc()
    stmt = stmt.order_by(order_clause).offset(skip).limit(limit)

    # 3. 查询逻辑全局只写一次，无重复
    result = await db.execute(stmt)
    data_list = list(result.scalars().all())

    return {"items": data_list, "total": total, "skip": skip, "limit": limit}


async def get_employee(db: AsyncSession, employee_id: int):
    stmt = select(models.Employee).where(models.Employee.id == employee_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    return item


async def update_employee(
    db: AsyncSession, employee_id: int, data: schemas.EmployeeUpdate
):
    # Literal 类型会在 Pydantic 层自动验证，此处无需额外检查
    stmt = select(models.Employee).where(models.Employee.id == employee_id)
    result = await db.execute(stmt)
    db_employee = result.scalar_one_or_none()
    if not db_employee:
        return None

    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_employee, key, value)

    await db.commit()
    await db.refresh(db_employee)
    return db_employee


async def delete_employee(db: AsyncSession, employee_id: int):
    stmt = select(models.Employee).where(models.Employee.id == employee_id)
    result = await db.execute(stmt)
    db_employee = result.scalar_one_or_none()
    if not db_employee:
        return None

    await db.delete(db_employee)
    await db.commit()
    return {"msg": "删除成功"}
