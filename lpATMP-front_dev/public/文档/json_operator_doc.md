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

**`GET /label/all`**

获取系统启动时从 SQLAlchemy 模型扫描得到的所有表字段注释映射。

**请求参数**：无

**响应格式**：

```json
{
  "table_name_1": { "field_1": "注释1", "field_2": "注释2" },
  "table_name_2": { "field_a": "注释A" }
}
```

**响应示例**：

```json
{
  "test_record": {
    "id": "主键ID",
    "scene_type": "场景类型",
    "analyze_user": "分析人员",
    "create_time": "创建时间"
  },
  "vehicle": {
    "id": "主键ID",
    "vehicle_type": "车辆类型",
    "plate_number": "车牌号"
  }
}
```

**错误码**：该接口无错误返回，始终返回内存缓存数据。

---

### 2. 查询标签

**`GET /label/query`**

查询指定模块的标签数据。支持查询全部模块、指定模块全部字段或指定模块的单个字段。

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `module_name` | string | 否 | 模块名（对应数据表名）。不传时返回全部模块数据 |
| `field_name` | string | 否 | 字段名。传入时需同时传入 `module_name`；不传时返回该模块所有字段的标签 |

**响应示例**：

```json
// 1) 不传 module_name：返回全部模块数据
{
  "code": 200,
  "message": "查询成功",
  "data": [
    {
      "test_record": [
        { "field": "scene_type", "labels": ["红绿灯", "匝道", "车道"] },
        { "field": "analyze_user", "labels": ["张三", "李四"] }
      ]
    }
  ]
}

// 2) 传 module_name 但不传 field_name：返回该模块所有字段标签
{
  "code": 200,
  "message": "查询成功",
  "data": [
    { "field": "scene_type", "labels": ["红绿灯", "匝道", "车道"] },
    { "field": "analyze_user", "labels": ["张三", "李四"] }
  ]
}

// 3) 同时传 module_name 和 field_name：返回该字段标签
{
  "code": 200,
  "message": "查询成功",
  "data": { "field": "analyze_user", "labels": ["张三", "李四"] }
}

// 4) module_name 不在缓存中 / 模块无标签数据 / 字段不存在
{ "code": 200, "message": "查询成功", "data": [] }
```

---

### 3. 新增/更新标签

**`POST /label/save`**

新增或更新指定模块下指定字段的标签列表。文件不存在时自动创建。

**请求体** (`application/json`)：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `module_name` | string | 否 | 模块名（对应数据表名）。不传时默认为 `test_record` |
| `field_name` | string | 是 | 字段名，必须存在于对应数据表中 |
| `labels` | array | 否 | 标签数组，如 `["张三", "李四"]` |

**请求示例**：

```json
{
  "module_name": "test_record",
  "field_name": "analyze_user",
  "labels": ["张三", "李四", "王五"]
}
```

**响应示例**：

```json
// 新增成功（模块或字段之前不存在）
{
  "code": 200,
  "message": "新增成功",
  "data": { "field": "analyze_user", "labels": ["张三", "李四", "王五"] }
}

// 更新成功（模块和字段都已存在）
{
  "code": 200,
  "message": "更新成功",
  "data": { "field": "analyze_user", "labels": ["张三", "李四", "王五"] }
}

// module_name 不存在于缓存中
{ "code": 400, "message": "module_name 不存在", "data": null }

// field_name 为空
{ "code": 400, "message": "field_name 不能为空", "data": null }

// field_name 不存在于该表中
{ "code": 400, "message": "field_name 不存在", "data": null }

// 写入文件失败
{ "code": 400, "message": "写入文件失败", "data": null }
```

---

### 4. 删除标签

**`DELETE /label/delete`**

删除指定模块或模块下指定字段的标签。删除整个模块时需指定 `module_name`；删除单个字段时需同时指定 `module_name` 和 `field_name`。

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `module_name` | string | 是 | 模块名（对应数据表名）。为空时默认为 `test_record` |
| `field_name` | string | 否 | 字段名。不传则删除整个模块的标签数据 |

**响应示例**：

```json
// 删除整个模块成功
{ "code": 200, "message": "已删除模块 test_record", "data": null }

// 删除单个字段成功
{ "code": 200, "message": "删除成功", "data": { "field": "analyze_user" } }

// JSON 文件不存在
{ "code": 400, "message": "文件不存在", "data": null }

// 模块不存在
{ "code": 400, "message": "未找到模块 xxx", "data": null }

// 字段不存在
{ "code": 400, "message": "未找到字段 xxx 的记录", "data": null }

// 写入文件失败
{ "code": 400, "message": "写入文件失败", "data": null }
```

---

## 辅助函数

### `init_model_meta_cache(base_cls)`

初始化全局字段注释缓存。系统启动时调用，扫描所有 SQLAlchemy 模型（排除抽象模型和 `IGNORE_TABLE` 中配置的表），将 `{表名: {字段名: 注释}}` 映射存入全局变量 `ALL_MODEL_FIELD_COMMENTS`。

| 参数 | 类型 | 说明 |
|------|------|------|
| `base_cls` | `Type[DeclarativeBase]` | SQLAlchemy 声明式基类 |

### `get_table_field_comments(table_name)`

根据表名获取字段注释映射，从全局缓存中读取。

| 参数 | 类型 | 说明 |
|------|------|------|
| `table_name` | `str` | 数据表名 |

| 返回值 | 类型 | 说明 |
|------|------|------|
| 字段注释映射 | `Dict[str, str]` | `{字段名: 注释}`，表不存在时返回空字典 |

---

## 内部常量

| 常量 | 值 | 说明 |
|------|------|------|
| `DEFAULT_MODULE_NAME` | `"test_record"` | 当 `module_name` 为空时的默认模块名 |
| `IGNORE_TABLE` | `["users", "kpi_main", "kpi_module", "kpi_item", "driver_monitors", "test_tasks"]` | 缓存初始化时忽略的数据表，这些表不会出现在合法模块名校验中 |
| `JSON_FILE_PATH` | `app/static/module_labels/module_labels.json` | 标签数据持久化文件路径 |

---

## 错误码

| code | 说明 |
|------|------|
| 200 | 操作成功 |
| 400 | 参数校验失败 / 文件不存在 / 写入失败 / 模块或字段不存在 |

---

---

# 车辆管理接口文档

## 概述

车辆管理接口提供车辆信息的查询、统计功能，数据来源于 MySQL 数据库中的 `vehicles` 表。接口注册在 `vehicle_plugin` 插件下。

**Base URL**: `/api/vehicle`

---

## 接口列表

### 1. 获取车型分布

**`GET /api/vehicle/model_distribution`**

查询所有车型及其对应的车辆数量，按车辆数量降序排列。用于前端展示车型分布统计图表。

**功能描述**：

- 从 `vehicles` 表中按 `model` 字段分组统计
- 返回每种车型的车辆数量
- 结果按 `count` 降序排列，数量最多的车型排在最前

**请求参数**：无

**请求示例**：

```
GET /api/vehicle/model_distribution
```

**响应数据结构**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | int | 状态码，成功时为 `200` |
| `message` | string | 提示信息，成功时为 `"success"` |
| `data` | array | 车型分布数据列表 |

**`data` 数组中每个元素的结构**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `model` | string | 车型名称，如 `"C11"`, `"C10"`, `"T03"` |
| `count` | int | 该车型对应的车辆数量 |

**响应示例**：

```json
// 正常返回
{
  "code": 200,
  "message": "success",
  "data": [
    { "model": "C11", "count": 15 },
    { "model": "C10", "count": 10 },
    { "model": "T03", "count": 8 },
    { "model": "C01", "count": 5 }
  ]
}

// 数据库中无车辆数据
{
  "code": 200,
  "message": "success",
  "data": []
}
```

**错误码**：

| code | 说明 |
|------|------|
| 200 | 查询成功（包括数据为空的情况） |

**实现说明**：

该接口对应的服务层方法为 `VehicleService.model_distribution()`，通过以下 SQL 逻辑实现：

```sql
SELECT model, COUNT(id) AS count
FROM vehicles
GROUP BY model
ORDER BY count DESC
```
