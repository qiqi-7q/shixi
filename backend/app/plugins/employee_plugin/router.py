from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.plugins.employee_plugin import schemas, services

router = APIRouter()


@router.post("/")
async def create_employee(data: schemas.EmployeeCreate, db: AsyncSession = Depends(get_db)):
    result = await services.create_employee(db=db, data=data)
    return {"code": 200, "data": result, "message": "员工创建成功"}


@router.get("/")
async def get_employees_list(
    skip: int = Query(0, description="跳过的记录数，用于分页"),
    limit: int = Query(10, description="每页显示的记录数"),
    name: str = Query(None, description="按姓名模糊筛选"),
    module_name: str = Query(None, description="按模块名称模糊筛选"),
    db: AsyncSession = Depends(get_db)
):
    result = await services.get_employees(db, skip=skip, limit=limit, name=name, module_name=module_name)
    return {"code": 200, "data": result, "message": "获取员工列表成功"}


@router.get("/{employee_id}")
async def get_employee(employee_id: int, db: AsyncSession = Depends(get_db)):
    result = await services.get_employee(db, employee_id=employee_id)
    if result:
        return {"code": 200, "data": result, "message": "获取员工成功"}
    return {"code": 404, "data": None, "message": "员工不存在"}


@router.put("/{employee_id}")
async def update_employee(employee_id: int, data: schemas.EmployeeUpdate, db: AsyncSession = Depends(get_db)):
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
