# 模块标签接口文档

## 概述

模块标签接口用于管理前端下拉选择框的标签数据，数据持久化存储在 `app/static/module_labels/module_labels.json` 文件中。

模块名（`module_name`）对应数据库中的表名，字段名（`field_name`）对应该表的字段名。合法的模块名和字段名由系统启动时通过 `init_model_meta_cache()` 从 SQLAlchemy 模型中自动扫描生成。

**Base URL**: `/label`

**JSON 文件数据结构** (`module_labels.json`):

```json
[
  {
    "test_record": [
      { "field": "scene_type", "labels": ["红绿灯", "匝道", "车道"] },
      { "field": "analyze_user", "labels": ["张三", "李四"] }
    ]
  },
  {
    "vehicle": [
      { "field": "vehicle_type", "labels": ["轿车", "SUV", "MPV"] }
    ]
  }
]
```

---

## 接口列表

### 1. 获取全部数据表字段注释缓存

**`GET api/label/field`**

获取field表对应的字段注释映射。

**请求参数**：

- `table_name` str: 数据表名，例如 `test_record` 或 `vehicle`。

**响应格式**：

```json
{ "field_1": "注释1", "field_2": "注释2" }
```

**响应示例**：

```json
  table_name = "test_record"时：
  {
    "id": "主键ID",
    "scene_type": "场景类型",
    "analyze_user": "分析人员",
    "create_time": "创建时间"
  }
```

**错误码**：该接口无错误返回，始终返回内存缓存数据。
