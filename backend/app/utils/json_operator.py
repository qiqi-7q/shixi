import json
from typing import List, Dict, Any, Optional, Type
from pathlib import Path

from pydantic import BaseModel

from fastapi import APIRouter
from sqlalchemy import inspect
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings
from app.plugins import auto_import_plugin_models

labels_router = APIRouter(prefix="/label", tags=["模块标签操作"])

JSON_LABELS_DIR: Path = settings.STATIC_DIR / "module_labels"
JSON_LABELS_DIR.mkdir(exist_ok=True, parents=True)

JSON_FILE_PATH: Path = JSON_LABELS_DIR / "module_labels.json"

DEFAULT_MODULE_NAME = "test_record"

# 不需要缓存的表名
IGNORE_TABLE = ["users","kpi_main","kpi_module","kpi_item","driver_monitors","test_tasks"]
# 数据表中文名映射
TABLE_CN = {
    "test_records": "测试记录表",
    "borrow_records": "车辆借用表",
    "test_routes": "路线管理",
    "test_miles": "测试里程表",
    "employees": "人员管理",
    "vehicles": "车辆资源表",
    "vehicle_monitors": "车辆监控表",
}

# 全局内存缓存：key=数据表名，value={字段名:字段注释}
ALL_MODEL_FIELD_COMMENTS: Dict[str, Dict[str, str]] = {}


def init_model_meta_cache(base_cls: Type[DeclarativeBase]):
    global ALL_MODEL_FIELD_COMMENTS
    ALL_MODEL_FIELD_COMMENTS.clear()

    auto_import_plugin_models()

    sub_models = base_cls.__subclasses__()

    for model_cls in sub_models:
        if model_cls.__dict__.get("__abstract__", False):
            continue
        table_name = model_cls.__tablename__
        if table_name in IGNORE_TABLE:
            continue
        mapper = inspect(model_cls)
        field_dict = {col.name: col.comment or "" for col in mapper.columns}
        ALL_MODEL_FIELD_COMMENTS[table_name] = field_dict


    print(f"缓存初始化完成，共加载 {len(ALL_MODEL_FIELD_COMMENTS)} 张表")


def get_table_field(table_name: str) -> Dict[str, str]:
    """根据表名获取字段注释映射"""
    return ALL_MODEL_FIELD_COMMENTS.get(table_name, {})

# 对外只读缓存API
@labels_router.get("/field")
def get_table_field_comments(table_name: str) -> Dict[str, str]:
    """根据表名获取字段注释映射"""
    return get_table_field(table_name)



@labels_router.get("/all")
def get_all_model_meta() -> Dict[str, str]:
    """获取全部数据表注释缓存"""
    return {table_name: TABLE_CN.get(table_name, table_name) for table_name in ALL_MODEL_FIELD_COMMENTS.keys()}


def _read_all() -> List[Dict[str, Any]]:
    """读取整个 module_labels.json，文件不存在或为空则返回空列表"""
    if not JSON_FILE_PATH.exists():
        return []
    try:
        with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError):
        return []


def _write_all(data: List[Dict[str, Any]]) -> bool:
    """写入整个 module_labels.json"""
    try:
        with open(JSON_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except IOError:
        return False


def _find_module_index(data: List[Dict[str, Any]], module_name: str) -> int:
    """在数据列表中查找模块的索引，未找到返回 -1"""
    for i, item in enumerate(data):
        if module_name in item:
            return i
    return -1


def _get_field_list(data: List[Dict[str, Any]], module_name: str) -> Optional[List[Dict[str, Any]]]:
    """获取指定模块的字段列表"""
    idx = _find_module_index(data, module_name)
    if idx == -1:
        return None
    return data[idx][module_name]


@labels_router.get("/query")
def query_labels(module_name: Optional[str] = None, field_name: Optional[str] = None) -> Dict[str, Any]:
    """
    查询指定模块的标签
    :param module_name: 模块名，为空时默认 test_record
    :param field_name: 字段名，传了则返回该字段的标签，不传则返回该模块所有字段
    """
    module_name = module_name.strip() if module_name else None
    field_name = field_name.strip() if field_name else None

    all_data = _read_all()
    if not module_name:
        return {"code": 200, "message": "查询成功", "data": all_data}
    if module_name not in ALL_MODEL_FIELD_COMMENTS.keys():
        return {"code": 200, "message": "查询成功", "data": []}

    field_list = _get_field_list(all_data, module_name)
    if field_list is None:
        return {"code": 200, "message": "查询成功", "data": []}

    if not field_name:
        return {"code": 200, "message": "查询成功", "data": field_list}
    fields = get_table_field(module_name)
    if field_name and field_name not in fields.keys():
        return {"code": 200, "message": "查询成功", "data": []}

    for item in field_list:
        if item.get("field") == field_name:
            return {"code": 200, "message": "查询成功", "data": item}
    return {"code": 200, "message": "查询成功", "data": []}


class SaveLabelsRequest(BaseModel):
    module_name: Optional[str] = None
    field_name: Optional[str] = None
    labels: Optional[list] = None


@labels_router.post("/save")
def save_labels(req: SaveLabelsRequest) -> Dict[str, Any]:
    """
    新增或更新指定模块指定字段的标签列表，文件不存在自动创建
    :param req.module_name: 模块名，为空时默认 test_record
    :param req.field_name: 字段名
    :param req.labels: 标签数组
    """
    module_name = req.module_name.strip() if req.module_name else DEFAULT_MODULE_NAME
    field_name = req.field_name.strip() if req.field_name else None
    labels = req.labels

    if module_name not in ALL_MODEL_FIELD_COMMENTS.keys():
        return {"code": 400, "message": "module_name 不存在", "data": None}

    if not field_name:
        return {"code": 400, "message": "field_name 不能为空", "data": None}

    fields = get_table_field(module_name)
    if field_name not in fields.keys():
        return {"code": 400, "message": "field_name 不存在", "data": None}

    all_data = _read_all()
    idx = _find_module_index(all_data, module_name)

    if idx == -1:
        all_data.append({module_name: [{"field": field_name, "labels": labels}]})
        success = _write_all(all_data)
        if success:
            return {"code": 200, "message": "新增成功", "data": {"field": field_name, "labels": labels}}
        else:
            return {"code": 400, "message": "写入文件失败", "data": None}

    field_list = all_data[idx][module_name]
    for item in field_list:
        if item.get("field") == field_name:
            item["labels"] = labels
            success = _write_all(all_data)
            if success:
                return {"code": 200, "message": "更新成功", "data": {"field": field_name, "labels": labels}}
            else:
                return {"code": 400, "message": "写入文件失败", "data": None}

    field_list.append({"field": field_name, "labels": labels})
    success = _write_all(all_data)
    if success:
        return {"code": 200, "message": "新增成功", "data": {"field": field_name, "labels": labels}}
    else:
        return {"code": 400, "message": "写入文件失败", "data": None}


@labels_router.delete("/delete")
def delete_labels(module_name: str, field_name: Optional[str] = None) -> Dict[str, Any]:
    """
    删除指定模块的标签
    :param module_name: 模块名，为空时默认 test_record
    :param field_name: 字段名，传了则删除该字段，不传则删除整个模块
    """
    module_name = module_name.strip() or DEFAULT_MODULE_NAME
    field_name = field_name.strip() if field_name else None

    if not JSON_FILE_PATH.exists():
        return {"code": 400, "message": "文件不存在", "data": None}

    all_data = _read_all()
    idx = _find_module_index(all_data, module_name)
    if idx == -1:
        return {"code": 400, "message": f"未找到模块 {module_name}", "data": None}

    if not field_name:
        all_data.pop(idx)
        success = _write_all(all_data)
        if success:
            return {"code": 200, "message": f"已删除模块 {module_name}", "data": None}
        else:
            return {"code": 400, "message": "写入文件失败", "data": None}

    field_list = all_data[idx][module_name]
    original_len = len(field_list)
    field_list[:] = [item for item in field_list if item.get("field") != field_name]
    if len(field_list) == original_len:
        return {"code": 400, "message": f"未找到字段 {field_name} 的记录", "data": None}

    success = _write_all(all_data)
    if success:
        return {"code": 200, "message": "删除成功", "data": {"field": field_name}}
    else:
        return {"code": 400, "message": "写入文件失败", "data": None}