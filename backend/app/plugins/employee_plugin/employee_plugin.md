# 员工管理模块 (Employee Plugin) API 文档

**基础路径 Base URL**: `/api/employee`
**模块标签**: 员工管理

## 数据模型参考

### Employee 对象 (返回值)
前端获取到的员工数据通常包含以下字段：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `id` | Integer | 员工唯一标识 (ID) |
| `name` | String | 姓名 |
| `module_name` | String / null | 模块名称 |
| `module_manager` | String / null | 模块负责人 |
| `job_type` | String / null | 岗位类型（司机/外协） |
| `created_at` | Datetime (ISO 8601) | 创建时间 |
| `updated_at` | Datetime (ISO 8601) | 更新时间 |

---

## 接口详情

### 1. 新增员工 (Create Employee)
- **请求方式**: `POST`
- **路径**: `/api/employee/`
- **请求体 (JSON格式)**:

| 字段名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `name` | String | **是** | 姓名 |
| `module_name` | String | 否 | 模块名称 |
| `module_manager` | String | 否 | 模块负责人 |
| `job_type` | String | 否 | 岗位类型：`司机` / `外协` |

- **响应格式**: `200 OK`，返回 `{"code": 200, "data": Employee对象, "message": "员工创建成功"}` 格式的数据。

#### 示例
**请求 (Request):**
```json
{
  "name": "张三",
  "module_name": "车辆管理",
  "module_manager": "李四",
  "job_type": "司机"
}
```

**响应 (Response - 200 OK):**
```json
{
  "code": 200,
  "data": {
    "name": "张三",
    "module_name": "车辆管理",
    "module_manager": "李四",
    "job_type": "司机",
    "id": 1,
    "created_at": "2026-06-04T10:00:00Z",
    "updated_at": "2026-06-04T10:00:00Z"
  },
  "message": "员工创建成功"
}
```

---

### 2. 获取员工列表 (Get Employees List)
- **请求方式**: `GET`
- **路径**: `/api/employee/`
- **Query 参数 (URL Params)**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `skip` | Integer | 否 | 0 | 分页跳过数量（用于翻页） |
| `limit` | Integer | 否 | 10 | 每页获取的最大数量 |
| `name` | String | 否 | null | 按姓名筛选（模糊匹配） |
| `module_name` | String | 否 | null | 按模块名称筛选（模糊匹配） |

- **响应格式**: `200 OK`，返回 `{"code": 200, "data": {"items": [Employee对象, ...], "total": 总数, "skip": 跳过数, "limit": 每页大小}, "message": "获取员工列表成功"}` 数据。

#### 示例
**请求 (Request):**
`GET /api/employee/?skip=0&limit=10&name=张&module_name=车辆`

**响应 (Response - 200 OK):**
```json
{
  "code": 200,
  "data": {
    "items": [
      {
        "name": "张三",
        "module_name": "车辆管理",
        "module_manager": "李四",
        "job_type": "司机",
        "id": 1,
        "created_at": "2026-06-04T10:00:00Z",
        "updated_at": "2026-06-04T10:00:00Z"
      }
    ],
    "total": 1,
    "skip": 0,
    "limit": 10
  },
  "message": "获取员工列表成功"
}
```

---

### 3. 获取员工详情 (Get Employee)
- **请求方式**: `GET`
- **路径**: `/api/employee/{employee_id}`
- **Path 路径参数**:
  - `employee_id` (Integer): 员工 ID，必填。
- **响应格式**: `200 OK`，返回 `{"code": 200, "data": Employee对象, "message": "获取员工成功"}` 格式的数据。
- **异常响应**: `200 OK`，当员工不存在时返回 `{"code": 404, "data": null, "message": "员工不存在"}`。

#### 示例
**请求 (Request):**
`GET /api/employee/1`

**响应 (Response - 200 OK):**
```json
{
  "code": 200,
  "data": {
    "name": "张三",
    "module_name": "车辆管理",
    "module_manager": "李四",
    "job_type": "司机",
    "id": 1,
    "created_at": "2026-06-04T10:00:00Z",
    "updated_at": "2026-06-04T10:00:00Z"
  },
  "message": "获取员工成功"
}
```

---

### 4. 更新员工信息 (Update Employee)
- **请求方式**: `PUT`
- **路径**: `/api/employee/{employee_id}`
- **Path 路径参数**:
  - `employee_id` (Integer): 员工 ID，必填。
- **请求体 JSON**: *(字段均为**选填**，传哪个说明更新哪个)*

| 字段名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `name` | String | 否 | 新的姓名 |
| `module_name` | String | 否 | 新的模块名称 |
| `module_manager` | String | 否 | 新的模块负责人 |
| `job_type` | String | 否 | 新的岗位类型：`司机` / `外协` |

- **响应格式**: `200 OK`，返回 `{"code": 200, "data": Employee对象, "message": "更新员工成功"}` 格式的数据。
- **异常响应**: `200 OK`，当员工不存在时返回 `{"code": 404, "data": null, "message": "员工不存在"}`。

#### 示例
**请求 (Request):**
`PUT /api/employee/1`
```json
{
  "job_type": "外协"
}
```

**响应 (Response - 200 OK):**
```json
{
  "code": 200,
  "data": {
    "name": "张三",
    "module_name": "车辆管理",
    "module_manager": "李四",
    "job_type": "外协",
    "id": 1,
    "created_at": "2026-06-04T10:00:00Z",
    "updated_at": "2026-06-04T11:30:00Z"
  },
  "message": "更新员工成功"
}
```

---

### 5. 删除员工 (Delete Employee)
- **请求方式**: `DELETE`
- **路径**: `/api/employee/{employee_id}`
- **Path 路径参数**:
  - `employee_id` (Integer): 员工 ID，必填。
- **响应格式**: `200 OK`，成功时返回 `{"code": 200, "data": {"msg": "删除成功"}, "message": "删除成功"}` 格式的数据。
- **异常响应**: `200 OK`，当员工不存在时返回 `{"code": 404, "data": null, "message": "员工不存在"}`。

#### 示例
**请求 (Request):**
`DELETE /api/employee/1`

**响应 (Response - 200 OK):**
```json
{
  "code": 200,
  "data": {
    "msg": "删除成功"
  },
  "message": "删除成功"
}
```

---

## 枚举值说明

### job_type 岗位类型枚举

| 值 | 说明 |
| --- | --- |
| `司机` | 司机岗位 |
| `外协` | 外协岗位 |

---

## 索引说明

| 字段 | 是否索引 | 说明 |
| --- | --- | --- |
| `id` | ✅ 是 | 主键索引 |
| `name` | ✅ 是 | 姓名索引（支持模糊查询） |
| `module_name` | ✅ 是 | 模块名称索引（支持模糊查询） |

---

## 数据库表结构

```sql
CREATE TABLE employees (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    module_name VARCHAR(100) COMMENT '模块名称',
    module_manager VARCHAR(100) COMMENT '模块负责人',
    name VARCHAR(100) NOT NULL COMMENT '姓名',
    job_type ENUM('司机', '外协') COMMENT '岗位（司机/外协）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_name (name),
    INDEX idx_module_name (module_name)
);
```