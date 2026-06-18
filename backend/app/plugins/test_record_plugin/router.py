import io
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import xlsxwriter

from app.core.database import get_db
from app.plugins.test_record_plugin import schemas, services
from app.plugins.test_record_plugin.models import FunctionMode, EvaluationDimension, KPIType

router = APIRouter()


# 1. 创建单条记录
@router.post("/createrecord")
async def create_record(
    record: schemas.TestRecordCreate, db: AsyncSession = Depends(get_db)
):
    result = await services.create_test_record(db=db, record=record)
    if result == "success":
        return {"message": "测试记录创建成功", "code": 200, "data": None}
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
    problem_category: Optional[EvaluationDimension] = None,
    kpi_type: Optional[KPIType] = None,
):
    records = await services.get_test_records(
        db,
        skip=skip,
        limit=limit,
        project=project,
        car_type=car_type,
        function_mode=function_mode,
        problem_category=problem_category,
        kpi_type=kpi_type,
    )
    return {"message": "success", "code": 200, "data": records}


# 3. 获取单条详情
@router.get("/getrecord/{record_id}", response_model=schemas.TestRecord)
async def get_record(record_id: int, db: AsyncSession = Depends(get_db)):
    record = await services.get_test_record(db, record_id=record_id)
    if isinstance(record, str):
        return {"message": record, "code": 400, "data": None}
    return {"message": "success", "code": 200, "data": record}


# 4. 更新
@router.put("/updaterecord/{record_id}", response_model=schemas.TestRecord)
async def update_record(
    record_id: int, record: schemas.TestRecordUpdate, db: AsyncSession = Depends(get_db)
):
    result = await services.update_test_record(db, record_id=record_id, record=record)
    if result == "success":
        return {"message": "测试记录更新成功", "code": 200, "data": None}
    else:
        return {"message": result, "code": 400, "data": None}


# 5. 删除
@router.delete("/delrecord/{record_id}")
async def delete_record(record_id: int, db: AsyncSession = Depends(get_db)):
    result = await services.delete_test_record(db, record_id=record_id)
    if result == "success":
        return {"message": "测试记录删除成功", "code": 200, "data": None}
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


# 7. 批量导出测试记录
@router.get("/batch_export")
async def batch_export(
    db: AsyncSession = Depends(get_db),
    project: Optional[str] = Query(None, description="项目筛选"),
    car_type: Optional[str] = Query(None, description="车型筛选"),
    function_mode: Optional[FunctionMode] = Query(None, description="功能模式筛选"),
    problem_category: Optional[EvaluationDimension] = Query(None, description="评价维度筛选"),
    kpi_type: Optional[KPIType] = Query(None, description="KPI类型筛选"),
):
    """
    批量导出测试记录到Excel文件
    :param project: 项目筛选条件（模糊匹配）
    :param car_type: 车型筛选条件
    :param function_mode: 功能模式筛选条件
    :param problem_category: 评价维度筛选条件
    :param kpi_type: KPI类型筛选条件
    :return: Excel文件流
    """
    # 查询数据
    export_data = await services.batch_export_records(
        db,
        project=project,
        car_type=car_type,
        function_mode=function_mode,
        problem_category=problem_category,
        kpi_type=kpi_type,
    )
    
    if not export_data:
        return {"message": "没有找到符合条件的数据", "code": 400, "data": None}
    
    # 创建Excel文件
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet("测试记录")
    
    # 写入表头
    headers = export_data["headers"]
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)
    
    # 写入数据
    records = export_data["records"]
    for row, record in enumerate(records, start=1):
        for col, header in enumerate(headers):
            worksheet.write(row, col, record.get(header, ""))
    
    workbook.close()
    output.seek(0)
    
    # 返回Excel文件流
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=test_records_export.xlsx"
        }
    )