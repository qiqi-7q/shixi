# 测试里程模块 (Test Miles Plugin) API 文档

**基础路径 Base URL**: `/api/test_miles`
**模块标签**: 测试里程

## 数据模型参考

### TestMiles 对象 (返回值)
前端获取到的测试里程数据通常包含以下字段：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `id` | Integer | 主键唯一标识 (ID) |
| `project` | String | 项目 |
| `test_version` | String / null | 测试版本 |
| `test_time` | Datetime (ISO 8601) | 测试时间 |
| `vin_code` | String | 测试车辆VIN号 |
| `test_function` | String / null | 测试功能 |
| `mileage` | Float / null | 功能测试里程 |
| `driving_mileage` | Float / null | 车辆行驶里程 |
| `is_kpi` | Boolean | 是否用于KPI统计 (默认 false) |
| `remarks` | String / null | 备注 |
| `created_at` | Datetime (ISO 8601) | 创建时间 |
| `updated_at` | Datetime (ISO 8601) | 更新时间 |

---

## 接口详情

### 1. 新增测试里程 (Create Miles)
- **请求方式**: `POST`
- **路径**: `/api/test_miles/`
- **请求体 (JSON格式)**:

| 字段名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `project` | String | **是** | 项目 |
| `test_time` | Datetime | **是** | 测试时间 |
| `vin_code` | String | **是** | 车辆VIN号 |
| `test_version` | String | 否 | 测试版本 |
| `test_function` | String | 否 | 测试功能 |
| `mileage` | Float | 否 | 功能测试里程 |
| `driving_mileage` | Float | 否 | 车辆行驶里程 |
| `is_kpi` | Boolean | 否 | 是否用于KPI统计 |
| `remarks` | String | 否 | 备注 |

- **响应格式**: `200 OK`，返回 `{"code": 200, "data": TestMiles对象, "message": null}` 格式的数据。

#### 示例
**请求 (Request):**
```json
{
  "project": "Project-A",
  "test_time": "2026-06-04T10:00:00Z",
  "vin_code": "VIN1234567890ABCD",
  "test_version": "v1.0.0",
  "test_function": "自动驾驶测试",
  "mileage": 150.5,
  "driving_mileage": 200.0,
  "is_kpi": true,
  "remarks": "正常完成"
}
```

**响应 (Response - 200 OK):**
```json
{
  "code": 200,
  "message": null,
  "data": {
    "project": "Project-A",
    "test_version": "v1.0.0",
    "test_time": "2026-06-04T10:00:00Z",
    "vin_code": "VIN1234567890ABCD",
    "test_function": "自动驾驶测试",
    "mileage": 150.5,
    "driving_mileage": 200.0,
    "is_kpi": true,
    "remarks": "正常完成",
    "id": 1,
    "created_at": "2026-06-04T10:00:00Z",
    "updated_at": "2026-06-04T10:00:00Z"
  }
}
```

---

### 2. 获取测试里程列表 (Get Miles List)
- **请求方式**: `GET`
- **路径**: `/api/test_miles/`
- **Query 参数 (URL Params)**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `skip` | Integer | 否 | 0 | 分页跳过数量（用于翻页） |
| `limit` | Integer | 否 | 10 | 每页获取的最大数量 |
| `project` | String | 否 | null | 按项目筛选 (精确匹配) |
| `test_version` | String | 否 | null | 按测试版本筛选 (模糊匹配) |
| `test_function` | String | 否 | null | 按测试功能筛选 (模糊匹配) |
| `test_start_date` | String | 否 | null | 按测试开始时间筛选 (格式: YYYY-MM-DD) |
| `test_end_date` | String | 否 | null | 按测试结束时间筛选 (格式: YYYY-MM-DD) |

- **响应格式**: `200 OK`，返回 `{"code": 200, "data": {"items": [TestMiles对象, ...], "total": 总数, "skip": 跳过数, "limit": 每页大小}, "message": "获取里程记录列表成功"}` 格式的数据。

#### 示例
**请求 (Request):**
`GET /api/test_miles/?skip=0&limit=10&project=Project-A&test_function=自动驾驶`

**响应 (Response - 200 OK):**
```json
{
  "code": 200,
  "data": {
    "items": [
      {
        "project": "Project-A",
        "test_version": "v1.0.0",
        "test_time": "2026-06-04T10:00:00Z",
        "vin_code": "VIN1234567890ABCD",
        "test_function": "自动驾驶测试",
        "mileage": 150.5,
        "is_kpi": true,
        "remarks": "正常完成",
        "id": 1,
        "created_at": "2026-06-04T10:00:00Z",
        "updated_at": "2026-06-04T10:00:00Z"
      }
    ],
    "total": 1,
    "skip": 0,
    "limit": 10
  },
  "message": "获取里程记录列表成功"
}
```

---

### 3. 获取测试里程详情 (Get Miles)
- **请求方式**: `GET`
- **路径**: `/api/test_miles/{miles_id}`
- **Path 路径参数**:
  - `miles_id` (Integer): 测试里程 ID，必填。
- **响应格式**: `200 OK`，返回 `{"code": 200, "data": TestMiles对象, "message": null}` 格式的数据。
- **异常响应**: `200 OK`，当记录不存在时返回 `{"code": 404, "data": null, "message": "里程记录不存在"}`。

#### 示例
**请求 (Request):**
`GET /api/test_miles/1`

**响应 (Response - 200 OK):**
```json
{
  "code": 200,
  "message": null,
  "data": {
    "project": "Project-A",
    "test_version": "v1.0.0",
    "test_time": "2026-06-04T10:00:00Z",
    "vin_code": "VIN1234567890ABCD",
    "test_function": "自动驾驶测试",
    "mileage": 150.5,
    "driving_mileage": 200.0,
    "is_kpi": true,
    "remarks": "正常完成",
    "id": 1,
    "created_at": "2026-06-04T10:00:00Z",
    "updated_at": "2026-06-04T10:00:00Z"
  }
}
```

---

### 4. 更新测试里程信息 (Update Miles)
- **请求方式**: `PUT`
- **路径**: `/api/test_miles/{miles_id}`
- **Path 路径参数**:
  - `miles_id` (Integer): 测试里程 ID，必填。
- **请求体 JSON**: *(字典级别部分更新，只传入需要更新的字段即可)*

| 字段名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `project` | String | 否 | 新的项目 |
| `test_time` | Datetime | 否 | 新的测试时间 |
| `vin_code` | String | 否 | 新的车辆VIN号 |
| `test_version` | String | 否 | 新的测试版本 |
| `test_function` | String | 否 | 新的测试功能 |
| `mileage` | Float | 否 | 新的功能测试里程 |
| `driving_mileage` | Float | 否 | 新的车辆行驶里程 |
| `is_kpi` | Boolean | 否 | 新的KPI统计状态 |
| `remarks` | String | 否 | 新的备注 |

- **响应格式**: `200 OK`，返回 `{"code": 200, "data": TestMiles对象, "message": null}` 格式的数据。
- **异常响应**: `200 OK`，当记录不存在时返回 `{"code": 404, "data": null, "message": "里程记录不存在"}`。

#### 示例
**请求 (Request):**
`PUT /api/test_miles/1`
```json
{
  "mileage": 200.0,
  "remarks": "追加里程"
}
```

**响应 (Response - 200 OK):**
```json
{
  "code": 200,
  "message": null,
  "data": {
    "project": "Project-A",
    "test_version": "v1.0.0",
    "test_time": "2026-06-04T10:00:00Z",
    "vin_code": "VIN1234567890ABCD",
    "test_function": "自动驾驶测试",
    "mileage": 200.0,
    "is_kpi": true,
    "remarks": "追加里程",
    "id": 1,
    "created_at": "2026-06-04T10:00:00Z",
    "updated_at": "2026-06-04T12:00:00Z"
  }
}
```

---

### 5. 删除测试里程 (Delete Miles)
- **请求方式**: `DELETE`
- **路径**: `/api/test_miles/{miles_id}`
- **Path 路径参数**:
  - `miles_id` (Integer): 测试里程 ID，必填。
- **响应格式**: `200 OK`，成功时返回 `{"code": 200, "data": {"msg": "删除成功"}, "message": null}` 格式的数据（`services.delete_test_miles` 返回 `{"msg": "删除成功"}`）。
- **异常响应**: `200 OK`，当记录不存在时返回 `{"code": 404, "data": null, "message": "里程记录不存在"}`。

#### 示例
**请求 (Request):**
`DELETE /api/test_miles/1`

**响应 (Response - 200 OK):**
```json
{
  "code": 200,
  "message": null,
  "data": {
    "msg": "删除成功"
  }
}
```

---

## 统计接口

### 6. 获取里程统计数据 (Get Mileage Stats)
- **请求方式**: `GET`
- **路径**: `/api/test_miles/stats/`
- **Query 参数 (URL Params)**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `start_date` | String | 否 | 统计开始日期（格式：YYYY-MM-DD） |
| `end_date` | String | 否 | 统计结束日期（格式：YYYY-MM-DD） |
| `project` | String | 否 | 按项目筛选 |

- **响应格式**: `200 OK`，返回 `{"code": 200, "data": {"overview": {...}, "version_mileage": [...], "daily_mileage": [...], "function_mileage": [...]}, "message": "获取里程统计数据成功"}` 格式。

#### 示例
**请求 (Request):**
`GET /api/test_miles/stats/?project=Project-A`

**响应 (Response - 200 OK):**
```json
{
  "code": 200,
  "data": {
    "overview": {
      "total_records": 26,
      "total_mileage": 901.3,
      "nap": 2.0,
      "cnap": 899.3
    },
    "version_mileage": [{"version": "v1.0.0", "total_mileage": 150.5}],
    "daily_mileage": [{"date": "2026-06-04", "total_mileage": 150.5}],
    "function_mileage": [{"function": "自动驾驶测试", "total_mileage": 150.5}]
  },
  "message": "获取里程统计数据成功"
}
```

> **说明**: 
> - `overview`: 总览统计，包含总记录数、总里程、NAP里程（KPI）、CNAP里程（非KPI）
> - `version_mileage` 与 `function_mileage` 的分组若为空值，则展示为 `"未分类"`（由 `services.get_version_mileage` / `get_function_mileage` 处理）

---

### 7. 获取版本里程统计 (Get Version Mileage)
- **请求方式**: `GET`
- **路径**: `/api/test_miles/stats/version`
- **Query 参数 (URL Params)**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `project` | String | 否 | 按项目筛选 |

- **响应格式**: `200 OK`，返回 `{"code": 200, "data": {"version_mileage": [...]}, "message": null}` 格式，`data.version_mileage` 中每项包含 `version` 与 `total_mileage`。`version` 为空时展示为 `"未分类"`。

---

### 8. 获取每日里程统计 (Get Daily Mileage)
- **请求方式**: `GET`
- **路径**: `/api/test_miles/stats/daily`
- **Query 参数 (URL Params)**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `start_date` | String | 否 | 统计开始日期（格式：YYYY-MM-DD） |
| `end_date` | String | 否 | 统计结束日期（格式：YYYY-MM-DD） |
| `project` | String | 否 | 按项目筛选 |

- **响应格式**: `200 OK`，返回 `{"code": 200, "data": {"daily_mileage": [...]}, "message": null}` 格式，`data.daily_mileage` 中每项包含 `date` 与 `total_mileage`。

---

### 9. 获取功能里程统计 (Get Function Mileage)
- **请求方式**: `GET`
- **路径**: `/api/test_miles/stats/function`
- **Query 参数 (URL Params)**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `project` | String | 否 | 按项目筛选 |

- **响应格式**: `200 OK`，返回 `{"code": 200, "data": {"function_mileage": [...]}, "message": null}` 格式，`data.function_mileage` 中每项包含 `function` 与 `total_mileage`。`function` 为空时展示为 `"未分类"`。
