import time

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.plugins.employee_plugin import schemas, services
from typing import Optional

router = APIRouter()


@router.post("/")
async def create_employee(
    data: schemas.EmployeeCreate, db: AsyncSession = Depends(get_db)
):
    result = await services.create_employee(db=db, data=data)
    return {"code": 200, "data": result, "message": "员工创建成功"}


@router.get("/fixsearch")
async def get_employees_simple(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    name: Optional[str] = None,
    module_name: Optional[str] = None,
    sort_by: Optional[str] = Query(None, description="排序字段名（不提供则不排序）"),
    sort_order: Optional[str] = Query(
        "asc", description="排序方向：asc（升序，默认）/ desc（降序）"
    ),
    db: AsyncSession = Depends(get_db),
):
    """获取员工列表（固定字段查询，支持排序）"""
    start_time = time.time()
    employeeData = await services.get_employees_simple(
        db,
        skip=skip,
        limit=limit,
        name=name,
        module_name=module_name,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    end_time = time.time()
    print(f"{sort_by}:{sort_order} 接口时间:",end_time-start_time)

    return {"data": employeeData, "message": "success", "code": 200}


@router.get("/{employee_id}")
async def get_employee(employee_id: int, db: AsyncSession = Depends(get_db)):
    result = await services.get_employee(db, employee_id=employee_id)
    if result:
        return {"code": 200, "data": result, "message": "获取员工成功"}
    return {"code": 404, "data": None, "message": "员工不存在"}


@router.put("/{employee_id}")
async def update_employee(
    employee_id: int, data: schemas.EmployeeUpdate, db: AsyncSession = Depends(get_db)
):
    result = await services.update_employee(db, employee_id=employee_id, data=data)
    if result:
        return {"code": 200, "data": result, "message": "更新员工成功"}
    return {"code": 404, "data": None, "message": "员工不存在"}


@router.delete("/{employee_id}")
async def delete_employee(employee_id: int, db: AsyncSession = Depends(get_db)):
    result = await services.delete_employee(db, employee_id=employee_id)
    if result:
        return {"code": 200, "data": result, "message": "删除成功"}
    return {"code": 404, "data": None, "message": "员工不存在"}
