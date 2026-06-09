# 测试任务模块 (Test Task Plugin) API 文档

**基础路径 Base URL**: `/api/test_task`
**模块标签**: 测试任务

## 数据模型参考

### TestTask 对象 (返回值)
前端获取到的测试任务数据通常包含以下字段：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `id` | Integer | 主键唯一标识 (ID) |
| `project` | String | 项目 |
| `test_version` | String / null | 测试版本 |
| `test_time` | Datetime (ISO 8601) | 测试时间 |
| `vin_code` | String | 测试车辆VIN号 |
| `test_function` | String / null | 测试功能 |
| `task_desc` | String / null | 任务描述 |
| `task_publisher` | String / null | 任务发布人 |
| `test_mileage` | Float / null | 测试里程 |
| `test_person` | String / null | 测试人员 |
| `actual_mileage` | Float / null | 实际完成里程 |
| `task_achievement_rate` | Float / null | 任务达成率 |
| `task_status` | String | 任务状态（完成/进行中/未开始/未达标/挂起） |
| `reason_desc` | String / null | 原因说明 |
| `remarks` | String / null | 备注 |
| `created_at` | Datetime (ISO 8601) | 创建时间 |
| `updated_at` | Datetime (ISO 8601) | 更新时间 |

---

## 接口详情

### 1. 新增测试任务 (Create Task)
- **请求方式**: `POST`
- **路径**: `/api/test_task/`
- **请求体 (JSON格式)**:

| 字段名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `project` | String | **是** | 项目 |
| `test_time` | Datetime | **是** | 测试时间 |
| `vin_code` | String | **是** | 车辆VIN号 |
| `test_version` | String | 否 | 测试版本 |
| `test_function` | String | 否 | 测试功能 |
| `task_desc` | String | 否 | 任务描述 |
| `task_publisher` | String | 否 | 任务发布人 |
| `test_mileage` | Float | 否 | 测试里程 |
| `test_person` | String | 否 | 测试人员 |
| `actual_mileage` | Float | 否 | 实际完成里程 |
| `task_status` | String | 否 | 任务状态（默认：未开始） |
| `reason_desc` | String | 否 | 原因说明 |
| `remarks` | String | 否 | 备注 |

- **响应格式**: `200 OK`，返回 `{"code": 200, "data": TestTask对象, "message": "任务获取成功"}` 格式的数据。

#### 示例
**请求 (Request):**
```json
{
  "project": "Project-B",
  "test_time": "2026-06-04T10:00:00Z",
  "vin_code": "VIN0987654321WXYZ",
  "task_publisher": "王工",
  "test_person": "李工",
  "test_mileage": 500.0,
  "actual_mileage": 450.0,
  "task_status": "进行中",
  "remarks": "任务基本达成"
}
```

**响应 (Response - 200 OK):**
```json
{
  "code": 200,
  "data": {
    "project": "Project-B",
    "test_version": null,
    "test_time": "2026-06-04T10:00:00Z",
    "vin_code": "VIN0987654321WXYZ",
    "test_function": null,
    "task_desc": null,
    "task_publisher": "王工",
    "test_mileage": 500.0,
    "test_person": "李工",
    "actual_mileage": 450.0,
    "task_achievement_rate": 90.0,
    "task_status": "进行中",
    "reason_desc": null,
    "remarks": "任务基本达成",
    "id": 1,
    "created_at": "2026-06-04T10:00:00Z",
    "updated_at": "2026-06-04T10:00:00Z"
  },
  "message": null
}
```

---

### 2. 获取测试任务列表 (Get Tasks List)
- **请求方式**: `GET`
- **路径**: `/api/test_task/`
- **Query 参数 (URL Params)**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `skip` | Integer | 否 | 0 | 分页跳过数量（用于翻页） |
| `limit` | Integer | 否 | 10 | 每页获取的最大数量 |
| `project` | String | 否 | null | 按项目筛选 (精确匹配) |
| `test_start_date` | String | 否 | null | 按测试开始时间筛选 (格式: YYYY-MM-DD) |
| `test_end_date` | String | 否 | null | 按测试结束时间筛选 (格式: YYYY-MM-DD) |
| `test_function` | String | 否 | null | 按测试功能筛选 (模糊匹配) |
| `task_publisher` | String | 否 | null | 按任务发布人筛选 (精确匹配) |
| `test_person` | String | 否 | null | 按测试人员筛选 (精确匹配) |
| `task_status` | String | 否 | null | 按任务状态筛选 (精确匹配) |

- **响应格式**: `200 OK`，返回 `{"code": 200, "data": {"items": [TestTask对象, ...], "total": 总数, "skip": 跳过数, "limit": 每页大小}, "message": "任务列表获取成功"}` 格式的数据。

#### 示例
**请求 (Request):**
`GET /api/test_task/?skip=0&limit=10&task_publisher=王工&task_status=进行中`

**响应 (Response - 200 OK):**
```json
{
  "code": 200,
  "data": {
    "items": [
      {
        "project": "Project-B",
        "test_version": null,
        "test_time": "2026-06-04T10:00:00Z",
        "vin_code": "VIN0987654321WXYZ",
        "test_function": null,
        "task_desc": null,
        "task_publisher": "王工",
        "test_mileage": 500.0,
        "test_person": "李工",
        "actual_mileage": 450.0,
        "task_achievement_rate": 90.0,
        "task_status": "进行中",
        "reason_desc": null,
        "remarks": "任务基本达成",
        "id": 1,
        "created_at": "2026-06-04T10:00:00Z",
        "updated_at": "2026-06-04T10:00:00Z"
      }
    ],
    "total": 1,
    "skip": 0,
    "limit": 10
  },
  "message": "任务列表获取成功"
}
```

---

### 3. 获取测试任务详情 (Get Task)
- **请求方式**: `GET`
- **路径**: `/api/test_task/{task_id}`
- **Path 路径参数**:
  - `task_id` (Integer): 测试任务 ID，必填。
- **响应格式**: `200 OK`，返回 `{"code": 200, "data": TestTask对象, "message": "任务获取成功"}` 格式的数据。
- **异常响应**: `200 OK`，当任务不存在时返回 `{"code": 404, "data": null, "message": "任务不存在"}`。

#### 示例
**请求 (Request):**
`GET /api/test_task/1`

**响应 (Response - 200 OK):**
```json
{
  "code": 200,
  "data": {
    "project": "Project-B",
    "test_version": null,
    "test_time": "2026-06-04T10:00:00Z",
    "vin_code": "VIN0987654321WXYZ",
    "test_function": null,
    "task_desc": null,
    "task_publisher": "王工",
    "test_mileage": 500.0,
    "test_person": "李工",
    "actual_mileage": 450.0,
    "task_achievement_rate": 90.0,
    "task_status": "进行中",
    "reason_desc": null,
    "remarks": "任务基本达成",
    "id": 1,
    "created_at": "2026-06-04T10:00:00Z",
    "updated_at": "2026-06-04T10:00:00Z"
  },
  "message": null
}
```

---

### 4. 更新测试任务信息 (Update Task)
- **请求方式**: `PUT`
- **路径**: `/api/test_task/{task_id}`
- **Path 路径参数**:
  - `task_id` (Integer): 测试任务 ID，必填。
- **请求体 JSON**: *(字典级别部分更新，只传入需要更新的字段即可)*

| 字段名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `project` | String | 否 | 新的项目 |
| `test_time` | Datetime | 否 | 新的测试时间 |
| `vin_code` | String | 否 | 新的车辆VIN号 |
| `test_version` | String | 否 | 新的测试版本 |
| `test_function` | String | 否 | 新的测试功能 |
| `task_desc` | String | 否 | 新的任务描述 |
| `task_publisher` | String | 否 | 新的任务发布人 |
| `test_mileage` | Float | 否 | 新的测试里程 |
| `test_person` | String | 否 | 新的测试人员 |
| `actual_mileage` | Float | 否 | 新的实际完成里程 |
| `task_status` | String | 否 | 新的任务状态 |
| `reason_desc` | String | 否 | 新的原因说明 |
| `remarks` | String | 否 | 新的备注 |

> **注意**: `task_achievement_rate`（任务达成率）会在更新时由后端自动重新计算，不需要前端传入。

- **响应格式**: `200 OK`，返回 `{"code": 200, "data": TestTask对象, "message": "任务获取成功"}` 格式的数据。
- **异常响应**: `200 OK`，当任务不存在时返回 `{"code": 404, "data": null, "message": "任务不存在"}`。

> **同步说明**: 更新成功后，会按 `project + vin_code + test_time` 匹配并同步更新 `TestMiles` 表中对应的记录（详见末尾「数据同步说明」）。

#### 示例
**请求 (Request):**
`PUT /api/test_task/1`
```json
{
  "actual_mileage": 500.0,
  "task_status": "完成",
  "remarks": "已全部完成"
}
```

**响应 (Response - 200 OK):**
```json
{
  "code": 200,
  "data": {
    "project": "Project-B",
    "test_version": null,
    "test_time": "2026-06-04T10:00:00Z",
    "vin_code": "VIN0987654321WXYZ",
    "test_function": null,
    "task_desc": null,
    "task_publisher": "王工",
    "test_mileage": 500.0,
    "test_person": "李工",
    "actual_mileage": 500.0,
    "task_achievement_rate": 100.0,
    "task_status": "完成",
    "reason_desc": null,
    "remarks": "已全部完成",
    "id": 1,
    "created_at": "2026-06-04T10:00:00Z",
    "updated_at": "2026-06-04T12:00:00Z"
  },
  "message": null
}
```

---

### 5. 删除测试任务 (Delete Task)
- **请求方式**: `DELETE`
- **路径**: `/api/test_task/{task_id}`
- **Path 路径参数**:
  - `task_id` (Integer): 测试任务 ID，必填。
- **响应格式**: `200 OK`，成功时返回 `{"code": 200, "data": {"msg": "删除成功"}, "message": "任务删除成功"}` 格式的数据。
- **异常响应**: `200 OK`，当任务不存在时返回 `{"code": 404, "data": null, "message": "任务不存在"}`。

> **同步说明**: 删除成功时，会按 `project + vin_code + test_time` 匹配并删除 `TestMiles` 表中对应的里程记录（详见末尾「数据同步说明」）。

#### 示例
**请求 (Request):**
`DELETE /api/test_task/1`

**响应 (Response - 200 OK):**
```json
{
  "code": 200,
  "data": {
    "msg": "删除成功"
  },
  "message": null
}
```

---

## 统计接口

### 6. 获取任务统计数据 (Get Task Stats)
- **请求方式**: `GET`
- **路径**: `/api/test_task/stats/`
- **Query 参数 (URL Params)**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `start_date` | String | 否 | 统计开始日期（格式：YYYY-MM-DD） |
| `end_date` | String | 否 | 统计结束日期（格式：YYYY-MM-DD） |
| `project` | String | 否 | 按项目筛选 |

- **响应格式**: `200 OK`，返回 `{"code": 200, "data": {...}, "message": "任务统计数据获取成功"}` 格式，包含每日任务下发量、任务状态分布、各功能任务量的统计数据。

#### 示例
**请求 (Request):**
`GET /api/test_task/stats/?project=Project-B`

**响应 (Response - 200 OK):**
```json
{
  "code": 200,
  "data": {
    "daily_counts": [{"date": "2026-06-04", "count": 5}],
    "status_counts": [{"status": "完成", "count": 3}, {"status": "进行中", "count": 2}],
    "function_counts": [{"function": "紧急制动测试", "count": 4}]
  },
  "message": null
}
```

---

### 7. 获取每日任务下发量 (Get Daily Task Count)
- **请求方式**: `GET`
- **路径**: `/api/test_task/stats/daily`
- **Query 参数 (URL Params)**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `start_date` | String | 否 | 统计开始日期（格式：YYYY-MM-DD） |
| `end_date` | String | 否 | 统计结束日期（格式：YYYY-MM-DD） |

- **响应格式**: `200 OK`，返回 `{"code": 200, "data": {"daily_counts": [...]}, "message": "每日任务下发量获取成功"}` 格式，`data.daily_counts` 中每项包含 `date` 与 `count`。统计依据为 `TestTask.created_at`（按日期分组）。
- **图表适用**: 折线图（X轴：日期，Y轴：任务数量）

> **注意**: 此接口当前未提供 `project` 筛选参数（仅支持 `start_date` / `end_date`）。

---

### 8. 获取任务状态分布 (Get Task Status Count)
- **请求方式**: `GET`
- **路径**: `/api/test_task/stats/status`
- **Query 参数 (URL Params)**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `project` | String | 否 | 按项目筛选 |

- **响应格式**: `200 OK`，返回 `{"code": 200, "data": {"status_counts": [...]}, "message": "任务状态分布获取成功"}` 格式，`data.status_counts` 中每项包含 `status` 与 `count`。
- **图表适用**: 饼图/柱状图（X轴：任务状态，Y轴：任务数量）

> **说明**: 始终返回所有5个任务状态（完成、进行中、未开始、未达标、挂起），即使某个状态的记录数为0也会返回。

---

### 9. 获取各功能任务量 (Get Function Task Count)
- **请求方式**: `GET`
- **路径**: `/api/test_task/stats/function`
- **Query 参数 (URL Params)**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `project` | String | 否 | 按项目筛选 |

- **响应格式**: `200 OK`，返回 `{"code": 200, "data": {"function_counts": [...]}, "message": "各功能任务量获取成功"}` 格式。
- **图表适用**: 柱状图（X轴：测试功能，Y轴：任务数量）

---

## 数据同步说明

### 任务与里程表同步机制
- **创建任务**：自动同步到 `TestMiles` 表（根据 `project`、`vin_code`、`test_time` 匹配）
- **更新任务**：自动更新 `TestMiles` 表中匹配的记录
- **删除任务**：自动删除 `TestMiles` 表中匹配的记录
- **手动创建里程**：不会影响任务表

**匹配规则**：
| 匹配字段 | 是否必须 |
| --- | --- |
| `project` | ✅ 必须 |
| `vin_code` | ✅ 必须 |
| `test_time` | ❌ 可选 |
