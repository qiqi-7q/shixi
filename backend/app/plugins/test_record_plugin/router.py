import asyncio
import io
from typing import Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import xlsxwriter
from app.core.config import settings
from app.core.database import get_db
from app.plugins.auth_plugin.models import User
from app.plugins.auth_plugin.router import get_current_user
from app.plugins.test_record_plugin import schemas, services
from app.plugins.test_record_plugin.models import (
    FunctionMode,
    EvaluationDimension,
    KPIType,
)

router = APIRouter()


# 1. 创建单条记录
@router.post("/createrecord")
async def create_record(
    record: schemas.TestRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user:
        return {"message": "用户未登录", "code": 401, "data": None}
    result = await services.create_test_record(
        db=db, record=record, current_user=current_user
    )
    if result == "success":
        return {"message": "测试记录创建成功", "code": 200, "data": None}
    else:
        return {"message": result, "code": 400, "data": None}


# 2. 获取列表
@router.get("/fixsearch")
async def get_records(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    project: Optional[str] = None,
    car_type: Optional[str] = None,
    function_mode: Optional[FunctionMode] = None,
    problem_category: Optional[EvaluationDimension] = None,
    kpi_type: Optional[KPIType] = None,
    software_version: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    if not current_user:
        return {"message": "用户未登录", "code": 401, "data": None}

    result = await services.get_test_records(
        db,
        skip=skip,
        limit=limit,
        project=project,
        car_type=car_type,
        function_mode=function_mode,
        problem_category=problem_category,
        kpi_type=kpi_type,
        software_version=software_version,
        current_user=current_user,
    )
    return {"code": 200, "data": result, "message": "获取测试记录列表成功"}


TIME_FIELDS = {"created_at", "updated_at", "problem_time"}


@router.post("/advsearch")
async def get_records_advanced(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="每页返回的记录数"),
    conditions: Optional[List[dict]] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    获取测试记录列表（高级查询）

    """
    if conditions:
        for cond in conditions:
            field_name = (
                cond.get("advanced_field") or cond.get("field") or cond.get("column")
            )
            operator = (
                cond.get("advanced_operator") or cond.get("operator") or cond.get("op")
            )
            field_value = cond.get("advanced_value") or cond.get("value")

            if not field_name:
                return {
                    "message": "条件中缺少字段名（advanced_field/field/column）",
                    "code": 400,
                }
            if not operator:
                return {
                    "message": f"字段 {field_name} 缺少操作符（advanced_operator/operator/op）",
                    "code": 400,
                }

            # 时间字段只支持 between/not_between 操作符
            if field_name in TIME_FIELDS and operator not in ("between", "not_between"):
                return {
                    "message": f"时间字段 {field_name} 只支持 between/not_between 操作符",
                    "code": 400,
                }

            # between/not_between 的值必须是数组
            if operator in ("between", "not_between"):
                if not isinstance(field_value, list) or len(field_value) != 2:
                    return {
                        "message": f"操作符 {operator} 的值必须是包含两个元素的数组",
                        "code": 400,
                    }

                # 时间字段特殊处理：将结束日期调整为当天的 23:59:59
                if field_name in TIME_FIELDS:

                    start_value = field_value[0]
                    end_value = field_value[1]

                    # 处理开始时间：如果是纯日期，添加 00:00:00
                    if isinstance(start_value, str) and len(start_value) == 10:
                        start_value = f"{start_value} 00:00:00"

                    # 处理结束时间：如果是纯日期，添加 23:59:59
                    if isinstance(end_value, str) and len(end_value) == 10:
                        end_value = f"{end_value} 23:59:59"

                    # 更新条件中的值
                    cond["value"] = [start_value, end_value]
                    # 如果使用的是 advanced_value，也需要更新
                    if "advanced_value" in cond:
                        cond["advanced_value"] = [start_value, end_value]

            if field_name not in schemas.TEST_RECORD_WHITELIST:
                return {
                    "message": f"无效的字段: {field_name} ",
                    "code": 400,
                }
            if operator not in settings.ADVANCED_OPERATORS:
                return {
                    "message": f"无效的操作: {operator} ",
                    "code": 400,
                }

    records = await services.get_test_records_adv(
        db,
        skip=skip,
        limit=limit,
        conditions=conditions,
    )
    return {"data": records, "message": "success", "code": 200}


############################


# 3. 获取单条详情
@router.get("/getrecord/{record_id}")
async def get_record(record_id: int, db: AsyncSession = Depends(get_db)):
    record = await services.get_test_record(db, record_id=record_id)
    if isinstance(record, str):
        return {"message": record, "code": 400, "data": None}
    return {"message": "success", "code": 200, "data": record}


# 4. 更新
@router.put("/updaterecord/{record_id}")
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
    file: UploadFile = File(..., description="Excel文件（.xlsx格式）"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    批量导入测试记录（文件上传）
    上传Excel文件，批量导入测试记录数据。自动进行数据去重、格式校验和批量写入。
    """
    if not current_user:
        return {"message": "token已失效，请重新登录", "code": 401, "data": None}
    result = await services.batch_import_records(file, db, current_user)
    return result


# 7. 批量导出测试记录
@router.get("/batch_export")
async def batch_export(
    db: AsyncSession = Depends(get_db),
    project: Optional[str] = Query(None, description="项目筛选"),
    car_type: Optional[str] = Query(None, description="车型筛选"),
    function_mode: Optional[FunctionMode] = Query(None, description="功能模式筛选"),
    problem_category: Optional[EvaluationDimension] = Query(
        None, description="评价维度筛选"
    ),
    kpi_type: Optional[KPIType] = Query(None, description="KPI类型筛选"),
    record_ids: Optional[str] = Query(
        None, description="指定记录ID列表，用逗号分隔，如: 1,2,3"
    ),
):
    """
    批量导出测试记录到Excel文件
    :param project: 项目筛选条件（模糊匹配）
    :param car_type: 车型筛选条件
    :param function_mode: 功能模式筛选条件
    :param problem_category: 评价维度筛选条件
    :param kpi_type: KPI类型筛选条件
    :param record_ids: 指定记录ID列表（优先使用），逗号分隔
    :return: Excel文件流
    """

    # 解析record_ids参数
    id_list = None
    if record_ids:
        try:
            id_list = [
                int(id_str.strip())
                for id_str in record_ids.split(",")
                if id_str.strip()
            ]
        except ValueError:
            return {
                "message": "record_ids参数格式错误，应为逗号分隔的数字列表",
                "code": 400,
                "data": None,
            }

    # 查询数据
    export_data = await services.batch_export_records(
        db,
        project=project,
        car_type=car_type,
        function_mode=function_mode,
        problem_category=problem_category,
        kpi_type=kpi_type,
        record_ids=id_list,
    )

    if not export_data:
        return {"message": "没有找到符合条件的数据", "code": 400, "data": None}

    # # 创建Excel文件
    # output = io.BytesIO()
    # workbook = xlsxwriter.Workbook(output)
    # worksheet = workbook.add_worksheet("测试记录")
    #
    # # 写入表头
    # headers = export_data["headers"]
    # for col, header in enumerate(headers):
    #     worksheet.write(0, col, header)
    #
    # # 写入数据
    # records = export_data["records"]
    # for row, record in enumerate(records, start=1):
    #     for col, header in enumerate(headers):
    #         worksheet.write(row, col, record.get(header, ""))
    #
    # workbook.close()
    # output.seek(0)
    #
    # # 返回Excel文件流
    # return StreamingResponse(
    #     output,
    #     media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    #     headers={
    #         "Content-Disposition": "attachment; filename=test_records_export.xlsx"
    #     },
    # )

    # 限制最多同时3个导出任务
    EXPORT_SEM = asyncio.Semaphore(3)
    EXPORT_TIMEOUT = 30  # 30秒超时

    # 在后台线程中生成Excel文件（避免阻塞事件循环）
    def _build_excel():
        output1 = io.BytesIO()
        workbook = xlsxwriter.Workbook(output1, {"constant_memory": True})
        worksheet = workbook.add_worksheet("测试记录")

        headers = export_data["headers"]
        records = export_data["records"]

        # 写入表头（整行写入）
        worksheet.write_row(0, 0, headers)

        # 写入数据（逐行写入，每次一行，比逐格写入快 N 倍）
        for row, record in enumerate(records, start=1):
            worksheet.write_row(row, 0, [record.get(h, "") for h in headers])

        workbook.close()
        output1.seek(0)
        return output1

    # 信号量控制并发导出任务，最多3个
    async def run_export():
        async with EXPORT_SEM:
            return await asyncio.to_thread(_build_excel)

    try:
        # 等待导出任务完成，超时30秒
        output = await asyncio.wait_for(run_export(), timeout=EXPORT_TIMEOUT)
    except asyncio.TimeoutError:
        return {"message": "导出超时", "code": 408, "data": None}

    # 返回Excel文件流
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=test_records_export.xlsx"
        },
    )


# 7. 刷新数据链接
@router.post("/refresh_link")
async def refresh_link(db: AsyncSession = Depends(get_db)):
    result = await services.refresh_link(db)
    if isinstance(result, dict) and result.get("success"):
        return {"message": "刷新成功", "code": 200, "data": result}
    else:
        return {
            "message": result if isinstance(result, str) else "刷新失败",
            "code": 400,
            "data": None,
        }
