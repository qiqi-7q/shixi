from typing import List, Optional, Set, Tuple

from fastapi import HTTPException
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.plugins.test_record_plugin import models, schemas
from app.plugins.test_record_plugin.models import FunctionMode, EvaluationDimension, KPIType
from app.utils.handle_excel_testrecord import handle_excel_some


# 创建
async def create_test_record(db: AsyncSession, record: schemas.TestRecordCreate):
    if not record:
        return "测试记录数据不能为空"
    if not record.project:
        return "项目名不能为空"
    if not record.car_type:
        return "车型不能为空"
    if not record.problem_time:
        return "问题时间不能为空"
    if not record.vin_code:
        return "车辆VIN号不能为空"
    db_record = models.TestRecord(**record.model_dump())
    db.add(db_record)
    await db.commit()
    await db.refresh(db_record)
    return "success"


# 获取列表
async def get_test_records(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    project: Optional[str] = None,
    car_type: Optional[str] = None,
    function_mode: Optional[FunctionMode] = None,
    problem_category: Optional[EvaluationDimension] = None,
    kpi_type: Optional[KPIType] = None,
):
    stmt = select(models.TestRecord)
    if project:
        stmt = stmt.filter(models.TestRecord.project.contains(project))
    if car_type:
        stmt = stmt.filter(models.TestRecord.car_type == car_type)
    if function_mode:
        stmt = stmt.filter(models.TestRecord.function_mode == function_mode)
    if problem_category:
        stmt = stmt.filter(models.TestRecord.problem_category == problem_category)
    if kpi_type:
        stmt = stmt.filter(models.TestRecord.kpi_type == kpi_type)
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


# 获取单条
async def get_test_record(db: AsyncSession, record_id: int):
    record = await db.get(models.TestRecord, record_id)
    if not record:
        return "测试记录不存在"
    return record


# 更新
async def update_test_record(
    db: AsyncSession, record_id: int, record: schemas.TestRecordUpdate
):

    db_record = await db.get(models.TestRecord, record_id)
    if not db_record:
        return "测试记录不存在"

    update_data = record.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_record, key, value)

    await db.commit()
    await db.refresh(db_record)
    return "success"


# 删除
async def delete_test_record(db: AsyncSession, record_id: int):
    record = await db.get(models.TestRecord, record_id)
    if not record:
        return "测试记录不存在"
    await db.delete(record)
    await db.commit()
    return "success"


# 批量导入
# # def batch_import_records(db: Session, records: List[schemas.TestRecordCreate]):
# def batch_import_records(file_path: str,db: Session):
#     # records,headers = excel_to_dict_list(file_path)
#     # 1. 处理Excel文件，捕获异常
#     try:
#         records, headers = excel_to_dict_list(file_path)
#
#     except Exception as e:
#         # 其他未知异常
#         raise HTTPException(status_code=500, detail=f"数据处理失败：{str(e)}")
#     if not records:
#         raise HTTPException(status_code=400, detail="导入数据不能为空")
#
#     success_count = 0
#     for item_dict in records:
#         try:
#             # 第一步：先把字典转成Pydantic模型，做数据格式/类型校验
#             pydantic_record = schemas.TestRecordCreate(**item_dict)
#             # 第二步：把校验通过的Pydantic模型，转成标准字典（这里才能用.dict()）
#             record_dict = pydantic_record.dict()
#             # 第三步：把字典解包，生成SQLAlchemy数据库模型实例
#             db_record = models.TestRecord(**record_dict)
#             db.add(db_record)
#             success_count += 1
#         except Exception as e:
#             db.rollback()
#             print(f"<UNK>{str(e)}")
#             raise HTTPException(status_code=400, detail=f"导入失败：{str(e)}")
#
#     db.commit()
#     return {
#         "msg": "批量导入完成",
#         "total": len(records),
#         "success": success_count
#     }

# ---------------------- 可自定义配置：重复数据判定字段 ----------------------
# 在这里修改：哪些字段组合起来，判定为重复数据
REPEAT_CHECK_FIELDS = ["vin_code", "problem_time", "problem_desc"]
# -----------------------------------------------------------------------------


# ---------------------- 核心工具函数：生成数据的唯一标识键 ----------------------
def generate_unique_key(data_dict: dict) -> Tuple:
    """
    根据配置的重复判定字段，生成数据的唯一标识元组
    元组可哈希，可用于集合去重、数据库查询
    """
    key_values = []
    for field in REPEAT_CHECK_FIELDS:
        # 处理空值，确保None和空字符串的一致性
        value = data_dict.get(field)
        if isinstance(value, str):
            value = value.strip()
        key_values.append(value)
    # 转成元组（不可变，可哈希）
    return tuple(key_values)


# -----------------------------------------------------------------------------


async def batch_import_records(file_path: str, db: AsyncSession):
    # 1. 入口参数强制校验
    if not isinstance(file_path, str):
        return f"第一个参数必须是文件路径字符串，实际收到：{type(file_path)}"
    if not isinstance(db, AsyncSession):
        return f"第二个参数必须是数据库Session对象，实际收到：{type(db)}"

    # 2. 读取Excel文件：自动过滤全空行
    try:
        excel_records, headers = handle_excel_some(file_path)
        total_excel_rows = len(excel_records)
    # except ExcelHandleError as e:
    #     raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        return f"Excel数据处理失败：{str(e)}"

    # 3. 第一重去重：内存去重，过滤Excel内的重复数据
    unique_records: List[dict] = []
    seen_keys: Set[Tuple] = set()
    excel_duplicate_count = 0

    for record in excel_records:
        # 生成唯一标识键
        unique_key = generate_unique_key(record)
        # 检查是否已经出现过
        if unique_key in seen_keys:
            excel_duplicate_count += 1
            continue
        # 新数据，加入列表和集合
        seen_keys.add(unique_key)
        unique_records.append(record)

    # 4. 第二重去重：数据库去重，过滤已存在的重复数据
    if not unique_records:
        return {
            "msg": "无有效数据可导入",
            "total_excel_rows": total_excel_rows,
            "excel_duplicate_rows": excel_duplicate_count,
            "db_duplicate_rows": 0,
            "success_import_rows": 0,
        }

    # 4.1 批量查询数据库中已存在的重复数据（高性能，无循环请求）
    # 构建查询条件：所有唯一键的组合
    query_conditions = []
    for record in unique_records:
        # 为每条数据构建字段匹配条件
        field_conditions = []
        for field in REPEAT_CHECK_FIELDS:
            value = record.get(field)
            if isinstance(value, str):
                value = value.strip()
            # 处理空值：数据库里的NULL和Python的None匹配
            if value is None:
                field_conditions.append(getattr(models.TestRecord, field).is_(None))
            else:
                field_conditions.append(getattr(models.TestRecord, field) == value)
        # 把单条数据的所有字段条件合并
        query_conditions.append(and_(*field_conditions))

    # 4.2 执行查询：获取所有已存在的重复数据的唯一键
    existing_records = db.query(models.TestRecord).filter(or_(*query_conditions)).all()
    existing_keys: Set[Tuple] = set()
    for record in existing_records:
        # 把数据库里的记录也转成唯一键，和Excel里的对比
        record_dict = {field: getattr(record, field) for field in REPEAT_CHECK_FIELDS}
        existing_key = generate_unique_key(record_dict)
        existing_keys.add(existing_key)

    # 4.3 过滤掉数据库已存在的重复数据，只保留全新的有效数据
    final_import_records: List[dict] = []
    db_duplicate_count = 0
    for record in unique_records:
        unique_key = generate_unique_key(record)
        if unique_key in existing_keys:
            db_duplicate_count += 1
            continue
        final_import_records.append(record)

    # 5. 数据校验：转Pydantic模型，确保格式符合数据库要求
    valid_records: List[schemas.TestRecordCreate] = []
    for idx, item_dict in enumerate(final_import_records):
        try:
            record = schemas.TestRecordCreate(**item_dict)
            valid_records.append(record)
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"第{idx+2}行数据格式错误：{str(e)}"
            )

    # 6. 批量写入数据库：高性能，事务安全
    success_count = 0
    if valid_records:
        try:
            record_dicts = [record.dict() for record in valid_records]
            db.bulk_insert_mappings(models.TestRecord, record_dicts)
            db.commit()
            success_count = len(record_dicts)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"数据库写入失败：{str(e)}")

    # 7. 返回清晰的导入结果（含所有去重统计）
    return {
        "msg": "批量导入完成",
        "total_excel_rows": total_excel_rows,  # Excel读取的有效数据总行数
        "excel_duplicate_rows": excel_duplicate_count,  # Excel内过滤的重复行数
        "db_duplicate_rows": db_duplicate_count,  # 数据库已存在的重复行数
        "success_import_rows": success_count,  # 最终成功上传的新数据行数
        "failed_import_rows": len(valid_records) - success_count,  # 导入失败行数
    }
