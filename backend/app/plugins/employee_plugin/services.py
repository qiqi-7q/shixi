from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException
from app.plugins.employee_plugin import models, schemas


async def create_employee(db: AsyncSession, data: schemas.EmployeeCreate):
    db_employee = models.Employee(**data.dict())
    db.add(db_employee)
    await db.commit()
    await db.refresh(db_employee)
    return db_employee


async def get_employees(db: AsyncSession, skip: int = 0, limit: int = 100, name: str = None, company: str = None):
    stmt = select(models.Employee)
    if name:
        stmt = stmt.where(models.Employee.name.like(f"%{name}%"))
    if company:
        stmt = stmt.where(models.Employee.third_party_company.like(f"%{company}%"))
    
    total_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(total_stmt)
    total = total_result.scalar_one()
    
    stmt = stmt.offset(skip).limit(limit).order_by(models.Employee.id.desc())
    result = await db.execute(stmt)
    
    return {
        "items": result.scalars().all(),
        "total": total,
        "skip": skip,
        "limit": limit
    }


async def get_employee(db: AsyncSession, employee_id: int):
    stmt = select(models.Employee).where(models.Employee.id == employee_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    return item


async def update_employee(db: AsyncSession, employee_id: int, data: schemas.EmployeeUpdate):
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
