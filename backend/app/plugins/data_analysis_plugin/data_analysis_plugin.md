# 数据分析模块 (Data Analysis Plugin) API 文档

**基础路径 Base URL**: `/api/analysis`
**模块标签**: 数据分析

---

## 概述

数据分析插件提供 NAP（New Assessment Protocol）统计分析功能，用于分析和管理 KPI（关键性能指标）数据。支持：
- **线性KPI**：传入原始里程/比率（浮点数或百分比字符串如"96.40%"）
- **扣分型KPI**：传入字典 `{'percent': 95}` 直接给百分制，或传入整数（表示默认事件次数），或字典{事件:次数}
- **二分型KPI**：传入0/1或布尔值

---

## 数据模型参考

### 数据库表结构

| 表名 | 说明 |
|------|------|
| `kpi_main` | KPI总表 - 存储项目、车型、版本等基础信息 |
| `kpi_module` | KPI模块表 - 存储可靠性、法规安全性、舒适性、可用性得分 |
| `kpi_item` | KPI明细项表 - 存储各KPI项的详细数据 |

### 数据关系

```
kpi_main (1:N) kpi_module (1:N) kpi_item
    │                │              │
    ├─ project       ├─ reliability ├─ KPIType
    ├─ carModel      ├─ regulationsSafety ├─ KPICount
    ├─ version       ├─ comfort    ├─ MPI
    ├─ funcMode      └─ usability  ├─ RawScore
    ├─ kpiMileage                 └─ KPIScore
    └─ totalScore
```

### KpiMain 对象

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | Integer | 主键ID |
| `project` | String(50) | 项目名称 |
| `carModel` | String(50) | 车型 |
| `version` | String(50) | 版本 |
| `funcMode` | String(50) | 功能模式 |
| `kpiMileage` | Decimal(10,2) | KPI里程 |
| `totalScore` | Decimal(8,2) | 总分 |
| `createTime` | DateTime | 创建时间 |
| `updateTime` | DateTime | 更新时间 |

### KpiModule 对象

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | Integer | 模块ID |
| `main_id` | Integer | 关联总表ID |
| `reliability` | Decimal(10,2) | 可靠性得分 |
| `regulationsSafety` | Decimal(10,2) | 法规/安全性得分 |
| `comfort` | Decimal(10,2) | 舒适性得分 |
| `usability` | Decimal(10,2) | 可用性得分 |
| `create_time` | DateTime | 创建时间 |

### KpiItem 对象

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | Integer | KPI明细ID |
| `module_id` | Integer | 关联模块表ID |
| `KPIType` | String(64) | KPI项名称 |
| `KPICount` | Integer | KPI事件次数 |
| `MPI` | Integer | MPI值 |
| `RawScore` | Decimal(8,2) | 原始得分（按每小项100分计） |
| `KPIScore` | Decimal(8,2) | 加权得分（最终得分） |
| `create_time` | DateTime | 创建时间 |

---

## 接口详情

### 1. 创建分析数据 (Create Analysis)

- **请求方式**: `POST`
- **路径**: `/api/analysis/create_analysis`
- **请求参数 (Query)**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `project` | String | **是** | 项目名称 |
| `model` | String | **是** | 车型 |
| `version` | String | **是** | 版本 |
| `funcMode` | String | **是** | 测试功能模式 |

- **响应格式**: `200 OK`

#### 示例

**请求 (Request):**
```http
POST /api/analysis/create_analysis?project=ADAS&model=T03&version=V1.0&funcMode=NAP
```

**响应 (Response - 成功):**
```json
{
  "message": "项目名为：ADAS，车型为：T03，版本为：V1.0，测试功能为：NAP 的分析已完成",
  "code": 200,
  "data": null
}
```

**响应 (Response - 失败):**
```json
{
  "message": "错误信息",
  "code": 400,
  "data": null
}
```

---

### 2. 获取分析列表 (Get Analysis List)

- **请求方式**: `GET`
- **路径**: `/api/analysis/fixsearch`
- **请求参数 (Query)**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `skip` | Integer | 否 | 0 | 分页跳过数量（>=0） |
| `limit` | Integer | 否 | 10 | 每页获取数量（1-1000） |
| `project` | String | 否 | null | 按项目筛选 |
| `carModel` | String | 否 | null | 按车型筛选 |
| `version` | String | 否 | null | 按版本筛选 |
| `funcMode` | String | 否 | null | 按功能模式筛选 |

- **响应格式**: `200 OK`

#### 示例

**请求 (Request):**
```http
GET /api/analysis/fixsearch?skip=0&limit=10&project=ADAS&carModel=T03
```

**响应 (Response):**
```json
{
  "message": "success",
  "code": 200,
  "data": [
    {
      "id": 1,
      "project": "ADAS",
      "carModel": "T03",
      "version": "V1.0",
      "funcMode": "NAP",
      "kpiMileage": 1000.00,
      "totalScore": 85.50,
      "createTime": "2024-01-01T10:00:00",
      "updateTime": "2024-01-01T10:00:00"
    }
  ],
  "total": 100
}
```

---

### 3. 获取单个分析详情 (Get Analysis Info)

- **请求方式**: `GET`
- **路径**: `/api/analysis/get_analysis/{analysis_id}`
- **路径参数**:
  - `analysis_id` (Integer): 分析数据ID，必填

- **响应格式**: `200 OK`

#### 示例

**请求 (Request):**
```http
GET /api/analysis/get_analysis/1
```

**响应 (Response - 成功):**
```json
{
  "data": {
    "id": 1,
    "project": "ADAS",
    "carModel": "T03",
    "version": "V1.0",
    "funcMode": "NAP",
    "kpiMileage": 1000.00,
    "totalScore": 85.50,
    "createTime": "2024-01-01T10:00:00",
    "updateTime": "2024-01-01T10:00:00",
    "module_list": [
      {
        "id": 1,
        "main_id": 1,
        "reliability": 90.00,
        "regulationsSafety": 85.00,
        "comfort": 80.00,
        "usability": 88.00,
        "create_time": "2024-01-01T10:00:00",
        "kpi_item_list": [
          {
            "id": 1,
            "module_id": 1,
            "KPIType": "ACC",
            "KPICount": 10,
            "MPI": 50,
            "RawScore": 95.00,
            "KPIScore": 9.50,
            "create_time": "2024-01-01T10:00:00"
          }
        ]
      }
    ]
  },
  "message": "success",
  "code": 200
}
```

**响应 (Response - 失败):**
```json
{
  "message": "分析数据不存在",
  "code": 400,
  "data": null
}
```

---

### 4. 对比分析数据 (Compare Analysis)

- **请求方式**: `PUT`
- **路径**: `/api/analysis/analysis_compare`
- **请求参数 (Query)**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `analysis_id1` | Integer | **是** | 第一个分析数据ID |
| `analysis_id2` | Integer | **是** | 第二个分析数据ID |

- **响应格式**: `200 OK`

#### 示例

**请求 (Request):**
```http
PUT /api/analysis/analysis_compare?analysis_id1=1&analysis_id2=2
```

**响应 (Response - 成功):**
```json
{
  "data": [
    {
      "id": 1,
      "project": "ADAS",
      "carModel": "T03",
      "version": "V1.0",
      "totalScore": 85.50,
      "module_list": [...]
    },
    {
      "id": 2,
      "project": "ADAS",
      "carModel": "T03",
      "version": "V2.0",
      "totalScore": 90.00,
      "module_list": [...]
    }
  ],
  "code": 200,
  "message": "分析对比完成"
}
```

**响应 (Response - 失败):**
```json
{
  "message": "分析数据不存在",
  "code": 400,
  "data": null
}
```

---

### 5. 删除分析数据 (Delete Analysis)

- **请求方式**: `DELETE`
- **路径**: `/api/analysis/delete_analysis`
- **请求参数 (Query)**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `analysis_id` | Integer | **是** | 要删除的分析数据ID |

- **响应格式**: `200 OK`

#### 示例

**请求 (Request):**
```http
DELETE /api/analysis/delete_analysis?analysis_id=1
```

**响应 (Response - 成功):**
```json
{
  "message": "分析删除成功",
  "code": 200,
  "data": null
}
```

**响应 (Response - 失败):**
```json
{
  "message": "分析数据不存在",
  "code": 400,
  "data": null
}
```

---

### 6. 获取分析数据总览统计 (Get Analysis Overview)

- **请求方式**: `GET`
- **路径**: `/api/analysis/stats/overview`
- **请求参数 (Query)**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `project` | String | 否 | null | 项目筛选（模糊匹配） |
| `carModel` | String | 否 | null | 车型筛选 |
| `funcMode` | String | 否 | null | 功能模式筛选 |

- **响应格式**: `200 OK`

#### 示例

**请求 (Request):**
```http
GET /api/analysis/stats/overview?project=test1
```

**响应 (Response):**
```json
{
  "code": 200,
  "data": {
    "total_records": 2,
    "avg_mileage": 115400.00,
    "avg_score": 28.32,
    "max_score": 32.33
  },
  "message": "获取分析数据总览成功"
}
```

**响应字段说明**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `total_records` | Integer | 总记录数 |
| `avg_mileage` | Decimal | 平均KPI里程 |
| `avg_score` | Decimal | 平均总分 |
| `max_score` | Decimal | 最高总分 |

---

### 7. 获取项目列表 (Get Projects)

- **请求方式**: `GET`
- **路径**: `/api/analysis/stats/projects`
- **请求参数**: 无

- **响应格式**: `200 OK`

#### 示例

**请求 (Request):**
```http
GET /api/analysis/stats/projects
```

**响应 (Response):**
```json
{
  "code": 200,
  "data": {
    "projects": ["test1", "test2", "ADAS测试"]
  },
  "message": "获取项目列表成功"
}
```

---

### 8. 获取版本得分统计 (Get Version Stats)

- **请求方式**: `GET`
- **路径**: `/api/analysis/stats/version`
- **请求参数 (Query)**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `project` | String | 否 | null | 项目名称（精确匹配） |
| `carModel` | String | 否 | null | 车型筛选 |
| `funcMode` | String | 否 | null | 功能模式筛选 |

- **响应格式**: `200 OK`

#### 示例

**请求 (Request):**
```http
GET /api/analysis/stats/version?project=test1
```

**响应 (Response):**
```json
{
  "code": 200,
  "data": {
    "version_stats": [
      {
        "project": "test1",
        "carModel": "A10",
        "version": "v2026.1",
        "funcMode": "NAP",
        "avg_score": 24.31,
        "total_mileage": 118900.00,
        "record_count": 1
      },
      {
        "project": "test1",
        "carModel": "A10",
        "version": "v2026.2",
        "funcMode": "NAP",
        "avg_score": 32.33,
        "total_mileage": 111900.00,
        "record_count": 1
      }
    ]
  },
  "message": "获取版本得分统计成功"
}
```

**响应字段说明**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `project` | String | 项目名称 |
| `carModel` | String | 车型 |
| `version` | String | 版本号 |
| `funcMode` | String | 功能模式 |
| `avg_score` | Decimal | 平均得分 |
| `total_mileage` | Decimal | 总里程 |
| `record_count` | Integer | 记录数 |

---

## 错误码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误或数据不存在 |

---

## 索引说明

| 表名 | 索引字段 | 说明 |
|------|----------|------|
| `kpi_main` | `project`, `carModel`, `version`, `funcMode` | 支持多条件筛选 |
| `kpi_module` | `main_id` | 关联查询优化 |
| `kpi_item` | `module_id` | 关联查询优化 |

---

## 数据流向

```
创建分析
    ↓
计算 KPI 得分（NAP统计函数）
    ↓
保存 kpi_main（总表）
    ↓
保存 kpi_module（模块得分）
    ↓
保存 kpi_item（明细项）
```

---

## NAP 统计函数支持类型

| KPI类型 | 输入格式 | 说明 |
|---------|----------|------|
| **线性KPI** | 浮点数（如 `96.40`）或百分比字符串（如 `"96.40%"`） | 直接使用原始里程/比率 |
| **扣分型KPI** | 字典 `{'percent': 95}` 或整数（事件次数）或字典 `{事件:次数}` | 支持多种输入方式 |
| **二分型KPI** | `0` / `1` 或布尔值 `True` / `False` | 二选一类型 |

---

## 数据库表结构 SQL

```sql
-- KPI总表
CREATE TABLE kpi_main (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    project VARCHAR(50) NOT NULL COMMENT '项目',
    carModel VARCHAR(50) NOT NULL COMMENT '车型',
    version VARCHAR(50) NOT NULL COMMENT '版本',
    funcMode VARCHAR(50) NOT NULL COMMENT '功能模式',
    kpiMileage DECIMAL(10,2) NOT NULL COMMENT 'KPI里程',
    totalScore DECIMAL(8,2) NOT NULL COMMENT '总分',
    is_del BOOLEAN DEFAULT FALSE COMMENT '是否删除',
    createTime DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updateTime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_project (project),
    INDEX idx_carModel (carModel),
    INDEX idx_version (version),
    INDEX idx_funcMode (funcMode)
);

-- KPI模块表
CREATE TABLE kpi_module (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '模块ID',
    main_id INT NOT NULL COMMENT '关联总表ID',
    reliability DECIMAL(10,2) NOT NULL COMMENT '可靠性',
    regulationsSafety DECIMAL(10,2) NOT NULL COMMENT '法规\安全性',
    comfort DECIMAL(10,2) NOT NULL COMMENT '舒适性',
    usability DECIMAL(10,2) NOT NULL COMMENT '可用性',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_main_id (main_id),
    FOREIGN KEY (main_id) REFERENCES kpi_main(id) ON DELETE CASCADE
);

-- KPI明细项表
CREATE TABLE kpi_item (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'KPI明细ID',
    module_id INT NOT NULL COMMENT '关联模块表ID',
    KPIType VARCHAR(64) NOT NULL COMMENT 'KPI项',
    KPICount INT DEFAULT 0 COMMENT 'KPI事件次数',
    MPI INT DEFAULT 0 COMMENT 'MPI',
    RawScore DECIMAL(8,2) NOT NULL COMMENT '原始得分',
    KPIScore DECIMAL(8,2) NOT NULL COMMENT '加权得分',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_module_id (module_id),
    FOREIGN KEY (module_id) REFERENCES kpi_module(id) ON DELETE CASCADE
);
```