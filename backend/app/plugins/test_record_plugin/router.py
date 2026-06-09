from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.plugins.test_record_plugin import schemas, services
from app.plugins.test_record_plugin.models import FunctionMode

router = APIRouter()


# 1. 创建单条记录
@router.post("/createrecord")
async def create_record(
    record: schemas.TestRecordCreate, db: AsyncSession = Depends(get_db)
):
    result = await services.create_test_record(db=db, record=record)
    if result == "success":
        return {"message": "record created successfully", "code": 200, "data": None}
    else:
        return {"message": result, "code": 400, "data": None}


# 2. 获取列表
@router.get("/fixsearch", response_model=list[schemas.TestRecord])
async def get_records(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    project: Optional[str] = None,
    car_type: Optional[str] = None,
    function_mode: Optional[FunctionMode] = None,
):
    records = await services.get_test_records(
        db,
        skip=skip,
        limit=limit,
        project=project,
        car_type=car_type,
        function_mode=function_mode,
    )
    return {"message": "records retrieved successfully", "code": 200, "data": records}


# 3. 获取单条详情
@router.get("/getrecord/{record_id}", response_model=schemas.TestRecord)
async def get_record(record_id: int, db: AsyncSession = Depends(get_db)):
    record = await services.get_test_record(db, record_id=record_id)
    if isinstance(record, str):
        return {"message": record, "code": 400, "data": None}
    return {"message": "record retrieved successfully", "code": 200, "data": record}


# 4. 更新
@router.put("/updaterecord/{record_id}", response_model=schemas.TestRecord)
async def update_record(
    record_id: int, record: schemas.TestRecordUpdate, db: AsyncSession = Depends(get_db)
):
    result = await services.update_test_record(db, record_id=record_id, record=record)
    if result == "success":
        return {"message": "record updated successfully", "code": 200, "data": None}
    else:
        return {"message": result, "code": 400, "data": None}


# 5. 删除
@router.delete("/delrecord/{record_id}")
async def delete_record(record_id: int, db: AsyncSession = Depends(get_db)):
    result = await services.delete_test_record(db, record_id=record_id)
    if result == "success":
        return {"message": "record deleted successfully", "code": 200, "data": None}
    else:
        return {"message": result, "code": 400, "data": None}


# 6. 批量本地数据导入（核心功能）
@router.post("/batch_import")
async def batch_import(
    # data: schemas.TestRecordBatchImport,
    path: str = Query(..., description="Excel文件的本地绝对路径"),
    db: AsyncSession = Depends(get_db),
):
    """
    批量本地数据导入
    请求体：{"records": [测试记录对象1, 测试记录对象2...]}
    """
    # return services.batch_import_records(db, data.records)
    result = await services.batch_import_records(path, db)
    return result
