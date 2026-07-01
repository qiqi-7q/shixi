from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException
from app.plugins.employee_plugin import models, schemas
from typing import Optional
from app.utils.all_orderby import universal_sort


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

    stmt = stmt.offset(skip).limit(limit).order_by(models.Employee.id.desc())
    result = await db.execute(stmt)

    if not sort_by:
        data_stmt = stmt.order_by(models.Employee.id.desc()).offset(skip).limit(limit)

        result = await db.execute(data_stmt)
        data_list = list(result.scalars().all())

    else:
        result = await db.execute(stmt)
        data_list = list(result.scalars().all())

        # 排序处理：在数据查询完成后、返回响应前执行
        if sort_by and data_list:
            # 校验排序字段是否在员工模型白名单中, 默认按 id 排序
            if sort_by not in schemas.EMPLOYEE_WHITELIST:
                sort_by = "id"

            # 校验排序方向，无效值默认使用 id 排序
            valid_order = sort_order.lower() if sort_order else "asc"
            if valid_order not in ("asc", "desc"):
                valid_order = "asc"
            data_list = universal_sort(data_list, sort_by, valid_order)
            # 分页处理：在数据查询完成后、返回响应前执行
        data_list = data_list[skip : skip + limit]

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
