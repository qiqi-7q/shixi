# 测试里程插件接口文档

## 基础信息

- **模块名称**: test_miles_plugin
- **API 前缀**: `/test_miles`
- **数据库表**: `test_miles`

## 数据模型

### TestMiles 字段说明

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | Integer | - | 主键 ID |
| project | String(100) | 是 | 项目 |
| test_version | String(50) | 否 | 测试版本 |
| test_start_time | DateTime | 是 | 测试开始时间 |
| test_end_time | DateTime | 是 | 测试结束时间 |
| vin_code | String(17) | 是 | 测试车辆 VIN |
| test_function | String(200) | 否 | 测试功能 |
| mileage | Float | 否 | 功能测试里程 |
| driving_mileage | Float | 否 | 车辆行驶里程 |
| is_kpi | Boolean | 否 | 是否用于 KPI 统计 |
| remarks | Text | 否 | 备注 |
| created_at | DateTime | - | 创建时间 |
| updated_at | DateTime | - | 更新时间 |

---

## 接口列表

### 1. 创建里程记录

- **路径**: `POST /test_miles/`
- **描述**: 创建一条测试里程记录

**请求体**:

```json
{
  "project": "string",
  "test_version": "string (可选)",
  "test_start_time": "datetime",
  "test_end_time": "datetime",
  "vin_code": "string",
  "test_function": "string (可选)",
  "mileage": "float (可选)",
  "driving_mileage": "float (可选)",
  "is_kpi": "boolean (可选，默认false)",
  "remarks": "string (可选)"
}
```

**成功响应**:

```json
{
  "code": 200,
  "data": { ... },
  "message": "里程记录创建成功"
}
```

---

### 2. 获取当前项目列表

- **路径**: `POST /test_miles/get_cur_project`
- **描述**: 获取所有不重复的项目名称

**请求参数**: 无

**成功响应**:

```json
{
  "code": 200,
  "data": ["项目A", "项目B"],
  "message": "获取当前项目成功"
}
```

---

### 3. 获取里程记录列表

- **路径**: `GET /test_miles/`
- **描述**: 获取里程记录列表，支持分页和多条件筛选

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| skip | Integer | 否 | 跳过的记录数，默认 0 |
| limit | Integer | 否 | 每页显示的记录数，默认 10 |
| project | String | 否 | 按项目精准筛选 |
| test_version | String | 否 | 按测试版本模糊筛选 |
| test_function | String | 否 | 按测试功能精准筛选 |
| test_start_date | String | 否 | 按测试开始时间筛选 |
| test_end_date | String | 否 | 按测试结束时间筛选 |

**成功响应**:

```json
{
  "code": 200,
  "data": {
    "items": [...],
    "total": 100,
    "skip": 0,
    "limit": 10
  },
  "message": "获取里程记录列表成功"
}
```

---

### 4. 获取单条里程记录

- **路径**: `GET /test_miles/{miles_id}`
- **描述**: 根据 ID 获取单条里程记录详情

**路径参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| miles_id | Integer | 里程记录 ID |

**成功响应**:

```json
{
  "code": 200,
  "data": { ... },
  "message": "获取里程记录成功"
}
```

**失败响应**:

```json
{
  "code": 404,
  "data": null,
  "message": "里程记录不存在"
}
```

---

### 5. 更新里程记录

- **路径**: `PUT /test_miles/{miles_id}`
- **描述**: 更新指定的里程记录

**路径参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| miles_id | Integer | 里程记录 ID |

**请求体**:

```json
{
  "project": "string (可选)",
  "test_version": "string (可选)",
  "test_start_time": "datetime (可选)",
  "test_end_time": "datetime (可选)",
  "vin_code": "string (可选)",
  "test_function": "string (可选)",
  "mileage": "float (可选)",
  "driving_mileage": "float (可选)",
  "is_kpi": "boolean (可选)",
  "remarks": "string (可选)"
}
```

**成功响应**:

```json
{
  "code": 200,
  "data": { ... },
  "message": "更新里程记录成功"
}
```

**失败响应**:

```json
{
  "code": 404,
  "data": null,
  "message": "里程记录不存在"
}
```

---

### 6. 删除里程记录

- **路径**: `DELETE /test_miles/{miles_id}`
- **描述**: 删除指定的里程记录

**路径参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| miles_id | Integer | 里程记录 ID |

**成功响应**:

```json
{
  "code": 200,
  "data": {"msg": "删除成功"},
  "message": "删除成功"
}
```

**失败响应**:

```json
{
  "code": 404,
  "data": null,
  "message": "里程记录不存在"
}
```

---

## 统计接口

### 7. 获取里程统计总览

- **路径**: `GET /test_miles/stats`
- **描述**: 获取里程统计数据（包含总览、版本、每日、功能统计）

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| start_date | String | 否 | 统计开始日期（格式：YYYY-MM-DD） |
| end_date | String | 否 | 统计结束日期（格式：YYYY-MM-DD） |
| project | String | 否 | 按项目名称筛选 |
| test_version | String | 否 | 按测试版本筛选（模糊匹配） |
| test_function | String | 否 | 按测试功能筛选 |

**成功响应**:

```json
{
  "code": 200,
  "data": {
    "overview": {
      "total_records": 100,
      "total_mileage": 5000.0,
      "nap": 2000.0,
      "cnap": 1500.0
    },
    "version_mileage": [...],
    "daily_mileage": [...],
    "function_mileage": [...]
  },
  "message": "获取里程统计数据成功"
}
```

---

### 8. 获取版本里程统计

- **路径**: `GET /test_miles/stats/version`
- **描述**: 按测试版本统计里程

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| project | String | 否 | 按项目名称筛选 |
| test_version | String | 否 | 按测试版本筛选（模糊匹配） |
| test_function | String | 否 | 按测试功能筛选 |
| start_date | String | 否 | 统计开始日期（格式：YYYY-MM-DD） |
| end_date | String | 否 | 统计结束日期（格式：YYYY-MM-DD） |

**成功响应**:

```json
{
  "code": 200,
  "data": {
    "version_mileage": [
      {"version": "v1.0", "total_mileage": 1000.0},
      {"version": "v2.0", "total_mileage": 2000.0}
    ]
  },
  "message": "获取版本里程统计成功"
}
```

---

### 9. 获取每日里程统计

- **路径**: `GET /test_miles/stats/daily`
- **描述**: 按日期统计每日里程

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| start_date | String | 否 | 统计开始日期（格式：YYYY-MM-DD） |
| end_date | String | 否 | 统计结束日期（格式：YYYY-MM-DD） |
| project | String | 否 | 按项目名称筛选 |
| test_version | String | 否 | 按测试版本筛选（模糊匹配） |
| test_function | String | 否 | 按测试功能筛选 |

**成功响应**:

```json
{
  "code": 200,
  "data": {
    "daily_mileage": [
      {"date": "2024-01-01", "total_mileage": 100.0},
      {"date": "2024-01-02", "total_mileage": 150.0}
    ]
  },
  "message": "获取每日里程统计成功"
}
```

---

### 10. 获取功能里程统计

- **路径**: `GET /test_miles/stats/function`
- **描述**: 按测试功能统计里程

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| project | String | 否 | 按项目名称筛选 |
| test_version | String | 否 | 按测试版本筛选（模糊匹配） |
| test_function | String | 否 | 按测试功能筛选 |
| start_date | String | 否 | 统计开始日期（格式：YYYY-MM-DD） |
| end_date | String | 否 | 统计结束日期（格式：YYYY-MM-DD） |

**成功响应**:

```json
{
  "code": 200,
  "data": {
    "function_mileage": [
      {"function": "NAP", "total_mileage": 2000.0},
      {"function": "CNAP", "total_mileage": 1500.0}
    ]
  },
  "message": "获取功能里程统计成功"
}
```

---

## 通用响应格式

所有接口响应遵循统一格式：

```json
{
  "code": 200,
  "data": null,
  "message": "操作成功"
}
```

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 404 | 资源不存在 |
