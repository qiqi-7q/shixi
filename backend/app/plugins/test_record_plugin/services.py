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
    handle_excel_some,
)
from app.utils.build_condition import build_condition
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


async def get_test_records_adv(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    conditions: Optional[List[dict]] = None,
) -> dict:
    stmt = select(models.TestRecord)
    if conditions:
        get_condition = []

        for cond in conditions:
            field_name = (
                cond.get("advanced_field") or cond.get("field") or cond.get("column")
            )
            operator = (
                cond.get("advanced_operator") or cond.get("operator") or cond.get("op")
            )
            value = cond.get("advanced_value") or cond.get("value")

            condition = build_condition(models.TestRecord, field_name, operator, value)
            if condition is not None:
                get_condition.append(condition)

        stmt = stmt.where(and_(*get_condition))

    total_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(total_stmt)
    total = total_result.scalar_one()

    stmt = stmt.offset(skip).limit(limit).order_by(models.TestRecord.id.desc())
    result = await db.execute(stmt)
    return {
        "items": list(result.scalars().all()),
        "total": total,
        "skip": skip,
        "limit": limit,
    }



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
    software_version: Optional[str] = None
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
    if software_version:
        stmt = stmt.filter(models.TestRecord.software_version == software_version)

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


def clean_string(value) -> str:
    """
    清理字符串中的特殊字符
    - 移除不可见字符（换行符、制表符等）
    - 移除首尾空白
    - 处理全角/半角字符
    """
    if value is None:
        return None

    if not isinstance(value, str):
        value = str(value)

    # 移除不可见字符（保留基本的空白字符）
    import re
    # 移除控制字符（除了换行和制表符）
    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', value)
    # 移除首尾空白和不可见字符
    cleaned = cleaned.strip()
    # 移除首尾的特殊符号（如全角空格等）
    cleaned = re.sub(r'^[\s\u3000]+|[\s\u3000]+$', '', cleaned)

    return cleaned


def convert_chinese_date(date_value) -> str:
    """
    将各种日期格式转换为标准格式
    支持：
    - 中文日期：2026年6月22日 → 2026-06-22 00:00:00
    - datetime对象：直接格式化
    - Excel日期序列号：转换为日期
    - 标准字符串：保持原样
    """
    import re
    from datetime import datetime, date, timedelta

    # 如果是None，返回None
    if date_value is None:
        return None

    # 如果是datetime/date对象，直接格式化
    if isinstance(date_value, (datetime, date)):
        return date_value.strftime("%Y-%m-%d %H:%M:%S")

    # 如果是数字（Excel日期序列号），转换为datetime
    if isinstance(date_value, (int, float)):
        try:
            # Excel日期序列号转换（1900年基准）
            dt = datetime(1899, 12, 30) + timedelta(days=date_value)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            pass

    # 如果是字符串，处理各种格式
    date_str = str(date_value).strip()

    # 清理特殊字符
    date_str = clean_string(date_str)

    # 尝试匹配中文日期
    match = re.match(r'(\d{4})年(\d{1,2})月(\d{1,2})日', date_str)
    if match:
        year = match.group(1)
        month = match.group(2).zfill(2)
        day = match.group(3).zfill(2)
        return f"{year}-{month}-{day} 00:00:00"

    # 尝试匹配标准日期格式
    standard_formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M",
        "%Y-%m-%d",
        "%Y/%m/%d"
    ]
    for fmt in standard_formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue

    # 无法识别的格式，返回原值（由后续Pydantic验证处理）
    return date_str


def transform_chinese_headers(excel_records: List[dict]) -> List[dict]:
    """
    将中文表头转换为英文字段名
    :param excel_records: 原始Excel数据（可能包含中文或英文字段名）
    :return: 转换后的数据（统一使用英文字段名）
    """
    transformed_records = []
    for record in excel_records:
        transformed = {}
        for cn_header, en_field in CHINESE_FIELD_MAPPING.items():
            # 优先查找中文表头
            if cn_header in record:
                value = record[cn_header]
                # 清理字符串字段中的特殊字符（用于去重匹配）
                if isinstance(value, str):
                    value = clean_string(value)
                # 特殊处理：software_version 字段确保为字符串类型
                if en_field == 'software_version' and value is not None:
                    value = str(value)
                # 特殊处理：problem_time 字段，转换各种日期格式
                if en_field == 'problem_time' and value is not None:
                    value = convert_chinese_date(value)
                transformed[en_field] = value
            # 其次查找英文表头（保持向后兼容）
            elif en_field in record:
                value = record[en_field]
                # 清理字符串字段中的特殊字符（用于去重匹配）
                if isinstance(value, str):
                    value = clean_string(value)
                # 特殊处理：software_version 字段确保为字符串类型
                if en_field == 'software_version' and value is not None:
                    value = str(value)
                # 特殊处理：problem_time 字段，转换各种日期格式
                if en_field == 'problem_time' and value is not None:
                    value = convert_chinese_date(value)
                transformed[en_field] = value
        # 保留原始行号信息
        if '_original_row_num' in record:
            transformed['_original_row_num'] = record['_original_row_num']
        transformed_records.append(transformed)
    return transformed_records


# -----------------------------------------------------------------------------


async def batch_import_records(file, db: AsyncSession):
    # 1. 入口参数强制校验
    # 使用 duck typing 检查，避免类型导入问题
    if not hasattr(file, 'filename') or not hasattr(file, 'read'):
        return f"第一个参数必须是UploadFile对象，实际收到：{type(file)}"
    if not isinstance(db, AsyncSession):
        return f"第二个参数必须是数据库Session对象，实际收到：{type(db)}"

    # 2. 保存上传的文件到临时目录
    import tempfile
    import os
    from pathlib import Path

    # 创建临时文件
    temp_dir = tempfile.gettempdir()
    temp_file_path = os.path.join(temp_dir, f"temp_import_{file.filename}")

    try:
        # 保存上传的文件内容到临时文件
        with open(temp_file_path, "wb") as temp_file:
            content = await file.read()
            temp_file.write(content)

        # 2. 读取Excel文件：自动过滤全空行
        try:
            excel_records, headers = handle_excel_some(temp_file_path)
            total_excel_rows = len(excel_records)
        except Exception as e:
            return f"Excel数据处理失败：{str(e)}"

        # 2.5 中文表头转换：支持中文表头导入（保持向后兼容）
        excel_records = transform_chinese_headers(excel_records)

        # 2.6 转换枚举字段：支持中英文输入，统一转换为中文值（Pydantic需要中文值进行验证）
        # - 英文枚举名（如 RELIABILITY）→ 转换为中文值（如 可靠性）
        # - 中文值（如 可靠性）→ 直接使用（保持不变）
        for record in excel_records:
            # 转换 problem_category（评价维度）
            if 'problem_category' in record and record['problem_category']:
                pc_value = record['problem_category'].strip()
                # 先检查是否已经是英文枚举名，转换为中文值
                pc_upper = pc_value.upper()
                if pc_upper in EvaluationDimension.__members__:
                    record['problem_category'] = EvaluationDimension[pc_upper].value  # 获取中文值
                # 再检查是否已经是有效的中文值（保持不变）
                elif pc_value not in [e.value for e in EvaluationDimension]:
                    # 既不是英文枚举名也不是有效中文值，清空字段（由后续Pydantic验证报错）
                    record['problem_category'] = None

            # 转换 kpi_type（KPI项）
            if 'kpi_type' in record and record['kpi_type']:
                kt_value = record['kpi_type'].strip()
                # 先检查是否已经是英文枚举名，转换为中文值
                kt_upper = kt_value.upper()
                if kt_upper in KPIType.__members__:
                    record['kpi_type'] = KPIType[kt_upper].value  # 获取中文值
                # 再检查是否已经是有效的中文值（保持不变）
                elif kt_value not in [e.value for e in KPIType]:
                    # 既不是英文枚举名也不是有效中文值，清空字段（由后续Pydantic验证报错）
                    record['kpi_type'] = None

        # 3. 第一重去重：内存去重，过滤Excel内的重复数据
        unique_records: List[dict] = []
        seen_keys: Set[Tuple] = set()
        excel_duplicate_count = 0

        for record in excel_records:
            # 生成唯一标识键
            unique_key = generate_unique_key(record, REPEAT_CHECK_FIELDS)
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

        # 4.1 批量查询数据库中已存在的重复数据（高性能，使用IN查询）
        # 构建查询条件：基于去重字段进行高效查询
        field_conditions = []

        # 分别收集每个去重字段的所有值
        field_values = {field: set() for field in REPEAT_CHECK_FIELDS}
        for record in unique_records:
            for field in REPEAT_CHECK_FIELDS:
                value = record.get(field)
                if isinstance(value, str):
                    value = value.strip()
                if value is not None:  # 跳过None值，避免IN查询问题
                    field_values[field].add(value)

        # 构建组合查询：任一去重字段匹配就作为候选（后续再精确过滤）
        for field, values in field_values.items():
            if values:
                field_conditions.append(getattr(models.TestRecord, field).in_(values))
        
        # 执行查询：获取所有可能的候选记录
        if field_conditions:
            stmt = select(models.TestRecord).filter(or_(*field_conditions))
        else:
            stmt = select(models.TestRecord)  # 如果没有有效条件，查询所有（边缘情况）
        
        result = await db.execute(stmt)
        existing_records = result.scalars().all()

        existing_keys: Set[Tuple] = set()
        for record in existing_records:
            # 把数据库里的记录也转成唯一键，和Excel里的对比
            record_dict = {field: getattr(record, field) for field in REPEAT_CHECK_FIELDS}
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
                original_row_num = item_dict.get('_original_row_num', idx + 2)
                raise HTTPException(
                    status_code=400, detail=f"第{original_row_num}行数据格式错误：{str(e)}"
                )

        # 6. 批量写入数据库：使用异步方法，事务安全
        success_count = 0
        if valid_records:
            try:
                for record in valid_records:
                    db.add(models.TestRecord(**record.dict()))
                await db.commit()
                success_count = len(valid_records)
            except Exception as e:
                await db.rollback()
                raise HTTPException(status_code=400, detail=f"数据库写入失败：{str(e)}")

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
    finally:
        # 清理临时文件
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as e:
                # 清理失败不影响主流程，仅记录日志
                pass

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
        "项目", "车型", "功能模式", "问题描述",
        "评价维度", "KPI项", "问题场景", "问题分类",
        "问题现象", "接管类型", "问题时间", "车辆VIN号",
        "数据链接", "Wetrack链接", "分析结果", "分析人员",
        "分析附件", "软件版本", "备注", "创建时间", "更新时间"
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

    # 转换记录为字典列表（将枚举值转换为中文值）
    record_dicts = []
    for record in records:
        record_dict = {}
        for cn_header in headers:
            field_name = field_mapping[cn_header]
            value = getattr(record, field_name)
            # 如果是枚举类型，转换为中文值（显示给用户看）
            if isinstance(value, (FunctionMode, EvaluationDimension, KPIType)):
                record_dict[cn_header] = value.value  # 获取中文值
            # 如果是日期时间类型，转换为字符串格式
            elif isinstance(value, (datetime, date, time)):
                record_dict[cn_header] = value.strftime("%Y-%m-%d %H:%M:%S")
            else:
                record_dict[cn_header] = value
        record_dicts.append(record_dict)

    return {"headers": headers, "records": record_dicts}
