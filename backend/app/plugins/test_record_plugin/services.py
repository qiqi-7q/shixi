from typing import List, Optional, Set, Tuple
import os
import json
from fastapi import HTTPException, UploadFile
from sqlalchemy import and_, or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.plugins.test_record_plugin import models, schemas
from app.plugins.test_record_plugin.models import (
    FunctionMode,
    EvaluationDimension,
    KPIType,
)
from app.plugins.test_record_plugin.client import APIClient
from app.utils.handle_excel_testrecord import (
    build_enum_lookup,
    generate_unique_key,
    handle_excel_from_bytes,
)
from datetime import datetime, date, time, timezone, timedelta


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

    total_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(total_stmt)
    total = total_result.scalar_one()

    stmt = stmt.offset(skip).limit(limit).order_by(models.TestRecord.id.desc())
    result = await db.execute(stmt)
    return {
        "items": result.scalars().all(),
        "total": total,
        "skip": skip,
        "limit": limit,
    }


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


# ---------------------- 可自定义配置：重复数据判定字段 ----------------------
# 在这里修改：哪些字段组合起来，判定为重复数据
REPEAT_CHECK_FIELDS = ["vin_code", "problem_time", "problem_desc"]
# -----------------------------------------------------------------------------
# ---------------------- 中文表头到英文字段名的映射 ----------------------
CHINESE_FIELD_MAPPING = {
    "项目": "project",
    "车型": "car_type",
    "功能模式": "function_mode",
    "问题描述": "problem_desc",
    "评价维度": "problem_category",
    "KPI项": "kpi_type",
    "问题场景": "problem_scene",
    "问题分类": "problem_type",
    "问题现象": "problem_phenomenon",
    "接管类型": "takeover_type",
    "问题时间": "problem_time",
    "车辆VIN号": "vin_code",
    "数据链接": "data_link",
    "Wetrack链接": "wetrack_link",
    "分析结果": "analyze_result",
    "分析人员": "analyze_user",
    "分析附件": "analyze_attach",
    "软件版本": "software_version",
    "备注": "remarks",
}
# -----------------------------------------------------------------------------


def transform_chinese_headers(record: dict) -> dict:

    transformed = {}
    FunctionMode_LOOKUP = build_enum_lookup(models.FunctionMode)
    EvaluationDimension_LOOKUP = build_enum_lookup(models.EvaluationDimension)
    KPIType_LOOKUP = build_enum_lookup(models.KPIType)

    ENUM_FIELD_LOOKUPS = {
        "function_mode": FunctionMode_LOOKUP,
        "problem_category": EvaluationDimension_LOOKUP,
        "kpi_type": KPIType_LOOKUP,
    }

    for cn_key, en_key in CHINESE_FIELD_MAPPING.items():
        if cn_key in record:
            transformed[en_key] = record[cn_key]

    # for field in STRING_FIELDS:
    #     if field in transformed and transformed[field] is not None:
    #         if not isinstance(transformed[field], str):
    #             transformed[field] = str(transformed[field])

    for enum_field, lookup in ENUM_FIELD_LOOKUPS.items():
        if enum_field in transformed and transformed[enum_field] is not None:
            raw = str(transformed[enum_field]).strip().upper()
            if raw in lookup:
                transformed[enum_field] = lookup[raw]

    return transformed


# -----------------------------------------------------------------------------


async def batch_import_records(file, db: AsyncSession):
    # 1. 校验上传
    if file is None:
        return {"code": 400, "message": "文件上传失败：未接收到文件", "data": None}
    if not file.filename:
        return {"code": 400, "message": "文件上传失败：文件名为空", "data": None}

    filename_lower = file.filename.lower()
    if not (filename_lower.endswith(".xlsx") or filename_lower.endswith(".xls")):
        return {
            "code": 400,
            "message": "文件上传失败：仅支持 .xlsx 或 .xls 格式",
            "data": None,
        }

    # 2. 从内存读取Excel文件内容
    content = await file.read()

    try:
        # 读取Excel文件：自动过滤全空行
        try:
            excel_records, headers = handle_excel_from_bytes(content)
            total_excel_rows = len(excel_records)
        except Exception as e:
            return {
                "message": f"Excel数据处理失败：{str(e)}",
                "code": 400,
                "data": None,
            }
            # 3. 单次遍历完成：中文表头映射 + 类型转换 + 枚举转换 + 内存去重
        transformed_records: List[dict] = []
        seen_keys: Set[Tuple] = set()
        excel_duplicate_count = 0

        for record in excel_records:
            transformed = transform_chinese_headers(record)
            if transformed is None:
                continue
            unique_key = generate_unique_key(transformed, REPEAT_CHECK_FIELDS)
            if unique_key in seen_keys:
                excel_duplicate_count += 1
                continue
            seen_keys.add(unique_key)
            transformed_records.append(transformed)

        if not transformed_records:
            return {
                "code": 200,
                "message": "导入完成（所有数据均为 Excel 内部重复）",
                "data": {
                    "msg": "无有效数据可导入",
                    "total_excel_rows": total_excel_rows,
                    "excel_duplicate_rows": excel_duplicate_count,
                    "db_duplicate_rows": 0,
                    "success_import_rows": 0,
                    "failed_import_rows": 0,
                },
            }

        # 3. 第一重去重已在上面完成（transformed_records），直接使用
        unique_records = transformed_records

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
                    # 处理时间字段：Excel中是字符串，数据库中是datetime，需要转换后比较
                    # 使用func.date_format将数据库datetime转换为字符串格式进行比较
                    if field == "problem_time" and isinstance(value, str):
                        field_conditions.append(
                            func.date_format(
                                getattr(models.TestRecord, field), "%Y-%m-%d %H:%i:%s"
                            )
                            == value
                        )
                    else:
                        field_conditions.append(
                            getattr(models.TestRecord, field) == value
                        )
            # 把单条数据的所有字段条件合并
            query_conditions.append(and_(*field_conditions))

        # 4.2 执行查询：获取所有已存在的重复数据的唯一键（使用异步方法）
        stmt = select(models.TestRecord).filter(or_(*query_conditions))
        result = await db.execute(stmt)
        existing_records = result.scalars().all()

        existing_keys: Set[Tuple] = set()
        for record in existing_records:
            # 把数据库里的记录也转成唯一键，和Excel里的对比
            record_dict = {
                field: getattr(record, field) for field in REPEAT_CHECK_FIELDS
            }
            existing_key = generate_unique_key(record_dict, REPEAT_CHECK_FIELDS)
            existing_keys.add(existing_key)

        # 4.3 过滤掉数据库已存在的重复数据，只保留全新的有效数据
        final_import_records: List[dict] = []
        db_duplicate_count = 0
        for record in unique_records:
            unique_key = generate_unique_key(record, REPEAT_CHECK_FIELDS)
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
                # 获取原始Excel行号（如果记录中保存了的话），否则显示当前索引
                original_row_num = item_dict.get("_original_row_num", idx + 2)
                return {
                    "code": 400,
                    "message": f"第{original_row_num}行数据格式错误：{str(e)}",
                    "data": None,
                }

        # 6. 批量写入数据库：使用异步方法，事务安全
        success_count = 0
        if valid_records:
            try:
                for record in valid_records:
                    db.add(models.TestRecord(**record.model_dump()))
                await db.commit()
                success_count = len(valid_records)
            except Exception as e:
                await db.rollback()
                return {
                    "code": 400,
                    "message": f"数据库写入失败：{str(e)}",
                    "data": None,
                }

        # 7. 根据导入结果返回清晰的消息
        if success_count == total_excel_rows:
            msg = "全部数据导入成功"
        elif success_count > 0 and db_duplicate_count > 0:
            msg = f"导入完成，新增{success_count}条，{db_duplicate_count}条重复已跳过"
        elif success_count == 0 and db_duplicate_count > 0:
            msg = "所有数据均已存在，未导入新数据"
        elif success_count == 0 and total_excel_rows > 0:
            msg = "数据导入失败，请检查数据格式"
        else:
            msg = "批量导入完成"

        # 7. 返回清晰的导入结果（含所有去重统计）
        return {
            "msg": msg,
            "total_excel_rows": total_excel_rows,  # Excel读取的有效数据总行数
            "excel_duplicate_rows": excel_duplicate_count,  # Excel内过滤的重复行数
            "db_duplicate_rows": db_duplicate_count,  # 数据库已存在的重复行数
            "success_import_rows": success_count,  # 最终成功上传的新数据行数
            "failed_import_rows": len(valid_records) - success_count,  # 导入失败行数
        }
    except Exception as e:
        return {"code": 400, "message": f"导入失败：{e}", "data": None}


###################### 刷新数据链接


def convert_to_timestamp(date_obj):
    """将日期时间转换为秒级时间戳"""
    if isinstance(date_obj, datetime):
        beijing_tz = timezone(timedelta(hours=8))
        if date_obj.tzinfo is None:
            date_obj = date_obj.replace(tzinfo=beijing_tz)
        return int(date_obj.timestamp())
    elif isinstance(date_obj, str):
        beijing_tz = timezone(timedelta(hours=8))
        formats = [
            "%Y年%m月%d日 %H:%M",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M",
            "%Y/%m/%d %H:%M:%S",
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(date_obj, fmt)
                dt = dt.replace(tzinfo=beijing_tz)
                return int(dt.timestamp())
            except ValueError:
                continue
    raise ValueError(f"无法解析日期时间: {date_obj}")


def get_bag_list(set_id, size):
    """获取 bag 列表并按 VIN 分组"""
    base_url = "https://leapai.leapmotor.com"
    api_client = APIClient(base_url, token=None, debug=True)
    response = api_client.list_bags(set_id, start=0, size=size)

    if "error" in response:
        raise ValueError(f"API错误: {response['error']['message']}")

    result = response["result"]["infos"]
    grouped_data = {}
    for item in result:
        vin = item["vin"]
        if vin not in grouped_data:
            grouped_data[vin] = []
        grouped_data[vin].append(
            {
                "bagId": item["bagId"],
                "setId": item["setId"],
                "startTime": item["startTime"],
                "endTime": item["endTime"],
            }
        )
    return grouped_data


def find_bag_url(target_vin, target_time, grouped_data, set_id):
    """根据 VIN 和时间匹配 bag 链接"""
    target_timestamp = convert_to_timestamp(target_time)
    bag_url = []

    if target_vin in grouped_data:
        for record in grouped_data[target_vin]:
            mid_seconds = (
                record["startTime"] + (record["endTime"] - record["startTime"]) / 2
            )
            mid_seconds = mid_seconds / 1000000
            time_error = abs(target_timestamp - mid_seconds)

            if set_id == 6868888 and time_error < 30:
                url = f"https://leapai.leapmotor.com/#/dataSet?setId={record['setId']}&bagId={record['bagId']}"
                bag_url.append(url)
            elif set_id == 1963 and time_error < 80:
                url = f"https://leapai.leapmotor.com/#/dataSet?setId={record['setId']}&bagId={record['bagId']}"
                bag_url.append(url)

    return ", ".join(bag_url) if bag_url else None


async def refresh_link(db: AsyncSession):
    stmt = select(models.TestRecord).filter(
        models.TestRecord.vin_code.isnot(None),
        models.TestRecord.problem_time.isnot(None),
    )
    result = await db.execute(stmt)
    records = result.scalars().all()

    if not records:
        return "未找到需要刷新链接的记录（需要有VIN号和问题时间）"

    try:
        size = 2000
        set_id_1963 = 1963
        set_id_6868 = 6868888

        # 分别拉取两个数据集的bag缓存
        group_1963 = get_bag_list(set_id_1963, size)
        group_6868 = get_bag_list(set_id_6868, size)

        # 校验数据集拉取结果
        err_list = []
        if not group_1963:
            err_list.append(f"数据集{set_id_1963}未获取到bag数据")
        if not group_6868:
            err_list.append(f"数据集{set_id_6868}未获取到bag数据")
        if err_list:
            return "；".join(err_list)

        success_count = 0
        fail_count = 0
        no_match_count = 0

        for db_record in records:
            if not db_record.vin_code or not db_record.problem_time:
                fail_count += 1
                continue

            try:
                # 第一步：原有逻辑，先匹配1963数据集链接
                link_1963 = find_bag_url(
                    db_record.vin_code, db_record.problem_time, group_1963, set_id_1963
                )

                # 第二步：匹配6868888数据集链接
                link_6868 = find_bag_url(
                    db_record.vin_code, db_record.problem_time, group_6868, set_id_6868
                )

                # 拼接两个链接，逗号分隔
                link_list = []
                if link_1963:
                    link_list.append(link_1963)
                if link_6868:
                    link_list.append(link_6868)

                if link_list:
                    # 多个链接逗号拼接存入原data_link
                    db_record.data_link = ", ".join(link_list)
                    success_count += 1
                else:
                    db_record.data_link = None
                    no_match_count += 1

            except Exception as e:
                print(f"匹配链接异常 VIN:{db_record.vin_code} 错误：{str(e)}")
                fail_count += 1
                continue

        await db.commit()

        return {
            "success": True,
            "total_records": len(records),
            "success_count": success_count,
            "fail_count": fail_count,
            "no_match_count": no_match_count,
        }

    except Exception as e:
        await db.rollback()
        return f"刷新数据链接失败: {str(e)}"


# 批量导出测试记录
async def batch_export_records(
    db: AsyncSession,
    project: Optional[str] = None,
    car_type: Optional[str] = None,
    function_mode: Optional[FunctionMode] = None,
    problem_category: Optional[EvaluationDimension] = None,
    kpi_type: Optional[KPIType] = None,
    record_ids: Optional[List[int]] = None,
):
    """
    批量导出测试记录到Excel
    :param db: 数据库会话
    :param project: 项目筛选条件
    :param car_type: 车型筛选条件
    :param function_mode: 功能模式筛选条件
    :param problem_category: 评价维度筛选条件
    :param kpi_type: KPI类型筛选条件
    :param record_ids: 指定记录ID列表
    :return: Excel文件字节流
    """
    # 构建查询
    stmt = select(models.TestRecord)

    # 如果提供了record_ids，在筛选结果中进一步按ID列表过滤
    if record_ids:
        stmt = stmt.filter(models.TestRecord.id.in_(record_ids))

    # 先应用筛选条件（始终生效）
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

    # 执行查询
    result = await db.execute(stmt)
    records = result.scalars().all()

    if not records:
        return None

    # 定义Excel表头（中文表头，与导入时的表头一致）
    headers = [
        "项目",
        "车型",
        "功能模式",
        "问题描述",
        "评价维度",
        "KPI项",
        "问题场景",
        "问题分类",
        "问题现象",
        "接管类型",
        "问题时间",
        "车辆VIN号",
        "数据链接",
        "Wetrack链接",
        "分析结果",
        "分析人员",
        "分析附件",
        "软件版本",
        "备注",
        "创建时间",
        "更新时间",
    ]

    # 字段名映射：中文表头到英文字段名
    field_mapping = {
        "项目": "project",
        "车型": "car_type",
        "功能模式": "function_mode",
        "问题描述": "problem_desc",
        "评价维度": "problem_category",
        "KPI项": "kpi_type",
        "问题场景": "problem_scene",
        "问题分类": "problem_type",
        "问题现象": "problem_phenomenon",
        "接管类型": "takeover_type",
        "问题时间": "problem_time",
        "车辆VIN号": "vin_code",
        "数据链接": "data_link",
        "Wetrack链接": "wetrack_link",
        "分析结果": "analyze_result",
        "分析人员": "analyze_user",
        "分析附件": "analyze_attach",
        "软件版本": "software_version",
        "备注": "remarks",
        "创建时间": "created_at",
        "更新时间": "updated_at",
    }

    # # 转换记录为字典列表（将枚举值转换为中文值）
    # record_dicts = []
    # for record in records:
    #     record_dict = {}
    #     for cn_header in headers:
    #         field_name = field_mapping[cn_header]
    #         value = getattr(record, field_name)
    #         # 如果是枚举类型，转换为中文值（显示给用户看）
    #         if isinstance(value, (FunctionMode, EvaluationDimension, KPIType)):
    #             record_dict[cn_header] = value.value  # 获取中文值
    #         # 如果是日期时间类型，转换为字符串格式
    #         elif isinstance(value, (datetime, date, time)):
    #             record_dict[cn_header] = value.strftime("%Y-%m-%d %H:%M:%S")
    #         else:
    #             record_dict[cn_header] = value
    #     record_dicts.append(record_dict)
    #
    # return {"headers": headers, "records": record_dicts}

    # 预计算枚举字段集合，避免每条记录逐字段 isinstance 判断
    enum_fields = {"function_mode", "problem_category", "kpi_type"}

    # 转换记录为字典列表（列表推导式，一次构建）
    record_dicts = [
        # 外层：遍历每条数据库记录
        {
            # 内层：遍历每个中文表头，构建 {中文表头: 值} 的字典
            cn_header: (
                # 1. 枚举字段：取 .value 获取中文值（如 "功能模式" -> "领航"）
                getattr(record, field_mapping[cn_header]).value
                if field_mapping[cn_header] in enum_fields
                and getattr(record, field_mapping[cn_header]) is not None
                else (
                    # 2. 日期时间字段：格式化为字符串 "2026-01-15 10:30:00"
                    getattr(record, field_mapping[cn_header]).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    if isinstance(
                        getattr(record, field_mapping[cn_header]),
                        (datetime, date, time),
                    )
                    # 3. 普通字段：直接取值（字符串、数字、None 等）
                    else getattr(record, field_mapping[cn_header])
                )
            )
            for cn_header in headers  # 遍历所有表头列
        }
        for record in records  # 遍历所有记录行
    ]

    return {"headers": headers, "records": record_dicts}