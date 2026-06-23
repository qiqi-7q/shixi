# from io import BytesIO
# from typing import Dict, List, Optional, Set, Tuple
#
# from fastapi import UploadFile
# from openpyxl import load_workbook
# from sqlalchemy import and_, or_, select
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from app.plugins.vehicle_plugin import models, schemas
# from app.utils.handle_excel_testrecord import (
#     handle_excel_some,
#     is_empty_row,
#     generate_unique_key,
# )
#
# # ============================================================
# # Excel 中文表头 → Pydantic 英文字段名映射
# # ============================================================
# EXCEL_FIELD_MAPPING: Dict[str, str] = {
#     "车型": "model",
#     "组别": "group",
#     "车辆阶段": "vehicle_stage",
#     "车辆配置": "configuration",
#     "车主权限": "owner_name",
#     "车辆编号": "vehicle_code",
#     "停车地点": "parking_location",
#     "使用状态": "vehicle_status",
#     "车辆状态": "test_status",
#     "备注": "remarks",
#     "VIN码": "vin_code",
#     "驱动电机号/发动机号": "engine_num",
#     "车牌号": "plate_number",
#     "临牌到期时间": "temp_plate_expire_date",
#     "临牌已办理次数": "temp_plate_count",
# }
#
# # 重复判定字段（vin_code + vehicle_code 组合唯一）
# REPEAT_VEHICLE_FIELDS = ["vin_code", "vehicle_code"]
#
# # 需要强制转为字符串的字段（Excel 中纯数字列会被 openpyxl 读取为 int/float）
# STRING_FIELDS = (
#     "model",
#     "vehicle_code",
#     "vin_code",
#     "owner_name",
#     "plate_number",
#     "vehicle_stage",
#     "configuration",
#     "parking_location",
#     "engine_num",
#     "remarks",
# )
#
#
#
# # ============================================================
# # 工具函数
# # ============================================================
# def _transform_record(record: dict) -> Optional[dict]:
#     transformed = {}
#
#     for cn_key, en_key in EXCEL_FIELD_MAPPING.items():
#         if cn_key in record:
#             transformed[en_key] = record[cn_key]
#
#     for field in STRING_FIELDS:
#         if field in transformed and transformed[field] is not None:
#             if not isinstance(transformed[field], str):
#                 transformed[field] = str(transformed[field])
#
#     for enum_field, lookup in ENUM_FIELD_LOOKUPS.items():
#         if enum_field in transformed and transformed[enum_field] is not None:
#             raw = str(transformed[enum_field]).strip().upper()
#             if raw in lookup:
#                 transformed[enum_field] = lookup[raw]
#
#     return transformed
#
#
# # ============================================================
# # 核心入口：处理上传的车辆 Excel 文件并存入数据库
# # ============================================================
# async def process_vehicle_excel_upload(
#     file: UploadFile, db: AsyncSession
# ) -> dict | str:
#     # 1. 校验上传
#     if file is None:
#         return {"code": 400, "message": "文件上传失败：未接收到文件", "data": None}
#     if not file.filename:
#         return {"code": 400, "message": "文件上传失败：文件名为空", "data": None}
#
#     filename_lower = file.filename.lower()
#     if not (filename_lower.endswith(".xlsx") or filename_lower.endswith(".xls")):
#         return {
#             "code": 400,
#             "message": "文件上传失败：仅支持 .xlsx 或 .xls 格式",
#             "data": None,
#         }
#
#     # 2. 保存上传的文件到临时目录
#     import tempfile
#     import os
#
#     # 创建临时文件
#     temp_dir = tempfile.gettempdir()
#     temp_file_path = os.path.join(temp_dir, f"temp_import_{file.filename}")
#
#     try:
#         # 保存上传的文件内容到临时文件
#         with open(temp_file_path, "wb") as temp_file:
#             content = await file.read()
#             temp_file.write(content)
#
#         # 2. 读取Excel文件：自动过滤全空行
#         try:
#             excel_records, headers = handle_excel_some(temp_file_path)
#             total_excel_rows = len(excel_records)
#         except Exception as e:
#             return f"Excel数据处理失败：{str(e)}"
#
#         # 3. 单次遍历完成：中文表头映射 + 类型转换 + 枚举转换 + 内存去重
#         transformed_records: List[dict] = []
#         seen_keys: Set[Tuple] = set()
#         excel_duplicate_count = 0
#
#         for record in excel_records:
#             transformed = _transform_record(record)
#             if transformed is None:
#                 continue
#             unique_key = generate_unique_key(transformed, REPEAT_VEHICLE_FIELDS)
#             if unique_key in seen_keys:
#                 excel_duplicate_count += 1
#                 continue
#             seen_keys.add(unique_key)
#             transformed_records.append(transformed)
#
#         if not transformed_records:
#             return {
#                 "code": 200,
#                 "message": "导入完成（所有数据均为 Excel 内部重复）",
#                 "data": {
#                     "msg": "无有效数据可导入",
#                     "total_excel_rows": total_excel_rows,
#                     "excel_duplicate_rows": excel_duplicate_count,
#                     "db_duplicate_rows": 0,
#                     "success_import_rows": 0,
#                     "failed_import_rows": 0,
#                 },
#             }
#
#         # 4. 数据库去重：一次批量查询，避免 N+1
#         query_conditions = []
#         for record in transformed_records:
#             field_conds = []
#             for field in REPEAT_VEHICLE_FIELDS:
#                 value = record.get(field)
#                 if isinstance(value, str):
#                     value = value.strip()
#                 if value is None:
#                     field_conds.append(getattr(models.Vehicle, field).is_(None))
#                 else:
#                     field_conds.append(getattr(models.Vehicle, field) == value)
#             query_conditions.append(and_(*field_conds))
#
#         stmt = select(models.Vehicle).filter(or_(*query_conditions))
#         result = await db.execute(stmt)
#         existing_records = result.scalars().all()
#
#         existing_keys: Set[Tuple] = {
#             generate_unique_key(
#                 {f: getattr(r, f) for f in REPEAT_VEHICLE_FIELDS}, REPEAT_VEHICLE_FIELDS
#             )
#             for r in existing_records
#         }
#
#         final_records: List[dict] = []
#         db_duplicate_count = 0
#         for record in transformed_records:
#             if generate_unique_key(record, REPEAT_VEHICLE_FIELDS) in existing_keys:
#                 db_duplicate_count += 1
#                 continue
#             final_records.append(record)
#
#         if not final_records:
#             return {
#                 "code": 200,
#                 "message": "导入完成（所有数据已在数据库中）",
#                 "data": {
#                     "msg": "所有数据已存在，无需导入",
#                     "total_excel_rows": total_excel_rows,
#                     "excel_duplicate_rows": excel_duplicate_count,
#                     "db_duplicate_rows": db_duplicate_count,
#                     "success_import_rows": 0,
#                     "failed_import_rows": 0,
#                 },
#             }
#
#         # 5. Pydantic 校验
#         valid_records: List[models.Vehicle] = []
#         for idx, item_dict in enumerate(final_records):
#             try:
#                 validated = schemas.VehicleCreate(**item_dict)
#                 valid_records.append(models.Vehicle(**validated.model_dump()))
#             except Exception as e:
#                 return {
#                     "code": 400,
#                     "message": f"第 {idx + 2} 行数据格式错误：{e}",
#                     "data": None,
#                 }
#
#         # 6. 批量写入：单次 add_all + commit，事务安全
#         try:
#             db.add_all(valid_records)
#             await db.commit()
#         except Exception as e:
#             await db.rollback()
#             return {"code": 400, "message": f"数据库写入失败：{e}", "data": None}
#
#         # 7. 返回结果
#         return {
#             "code": 200,
#             "message": "文件上传并导入成功",
#             "data": {
#                 "msg": "批量导入完成",
#                 "total_excel_rows": total_excel_rows,
#                 "excel_duplicate_rows": excel_duplicate_count,
#                 "db_duplicate_rows": db_duplicate_count,
#                 "success_import_rows": len(valid_records),
#                 "failed_import_rows": 0,
#             },
#         }
#     finally:
#         # 清理临时文件
#         if os.path.exists(temp_file_path):
#             try:
#                 os.remove(temp_file_path)
#             except Exception as e:
#                 # 清理失败不影响主流程，仅记录日志
#                 pass
