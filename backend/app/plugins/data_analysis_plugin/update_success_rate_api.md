# 更新成功率指标接口文档

## 接口概述

**接口名称**：手动更新NAP成功率指标并重新计算KPI得分

**功能说明**：支持用户在前端手动输入以下6个成功率指标（0-100的百分比），系统会根据输入值重新计算KPI得分，并更新 `kpi_item`、`kpi_main`、`kpi_module` 三张表中的相关数据。

---

## 接口详情

### 请求信息

- **请求方式**: `PUT`
- **路径**: `/api/analysis/update_success_rate`
- **Content-Type**: `application/json`

### 请求参数（JSON Body）

| 参数名 | 类型 | 必填 | 范围 | 说明 |
|--------|------|------|------|------|
| `project` | String | **是** | - | 项目名称 |
| `carModel` | String | **是** | - | 车型 |
| `version` | String | **是** | - | 软件版本 |
| `funcMode` | String | **是** | - | 功能模式（如NAP） |
| `change_lane_success_rate` | Float | **是** | 0-100 | 变道成功率(%) |
| `inflow_success_rate` | Float | **是** | 0-100 | 汇入成功率(%) |
| `outflow_success_rate` | Float | **是** | 0-100 | 汇出成功率(%) |
| `diverge_converge_rate` | Float | **是** | 0-100 | 分合流成功率(%) |
| `special_rate` | Float | **是** | 0-100 | 特殊场景成功率(%) |
| `recog_rate` | Float | **是** | 0-100 | 限速识别成功率(%) |

---

## 请求示例

```json
{
    "project": "ADAS测试",
    "carModel": "B10-27款",
    "version": "20260622",
    "funcMode": "NAP",
    "change_lane_success_rate": 95.5,
    "inflow_success_rate": 92.0,
    "outflow_success_rate": 93.5,
    "diverge_converge_rate": 88.0,
    "special_rate": 85.0,
    "recog_rate": 98.0
}
```

---

## 响应信息

### 成功响应（HTTP 200）

```json
{
    "message": "成功率指标更新成功",
    "code": 200,
    "data": null
}
```

### 失败响应（HTTP 400）

```json
{
    "message": "未找到对应的KPI分析记录",
    "code": 400,
    "data": null
}
```

---

## 响应字段说明

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `message` | String | 操作结果描述 |
| `code` | Integer | 状态码（200成功，400失败） |
| `data` | Object | 返回数据（成功时为null） |

---

## 评分计算规则

### 各指标评分配置

| 指标 | min（0分） | mid（60分） | max（100分） | 满分权重 |
|------|-----------|------------|-------------|----------|
| 变道成功率 | 80% | 90% | 99.5% | 4.0分 |
| 汇入成功率 | 80% | 90% | 98% | 4.0分 |
| 汇出成功率 | 80% | 90% | 98% | 4.0分 |
| 分合流成功率 | 80% | 90% | 98% | 2.0分 |
| 特殊场景成功率 | 60% | 70% | 95% | 2.0分 |
| 限速识别成功率 | 90% | 95% | 99.5% | 1.0分 |

### 线性分段评分公式

```
原始分 = 0,                              当 value <= min
原始分 = 60 / (mid - min) * (value - min),  当 min < value <= mid
原始分 = 60 + 40 / (max - mid) * (value - mid), 当 mid < value < max
原始分 = 100,                            当 value >= max

加权分 = 原始分 * 满分权重 / 100
```

---

## 更新的数据表

调用此接口后，以下三张表的数据会被更新：

| 表名 | 更新字段 |
|------|----------|
| `kpi_main` | `totalScore`（总分） |
| `kpi_module` | `usability`（可用性模块得分） |
| `kpi_item` | `RawScore`、`KPIScore`、`MPI`（各KPI项的得分） |

---

## 业务流程

```
1. 用户输入成功率指标（0-100）
    ↓
2. 系统验证项目、车型、版本、功能模式是否存在对应记录
    ↓
3. 查询测试记录获取其他KPI统计数据（如异常退出次数等）
    ↓
4. 使用手动输入的成功率重新计算可用性模块得分
    ↓
5. 更新 kpi_item 表中相关KPI项的得分
    ↓
6. 更新 kpi_module 表中的可用性得分
    ↓
7. 更新 kpi_main 表中的总分
    ↓
8. 返回更新成功响应
```

---

## 错误码说明

| 状态码 | 错误信息 | 说明 |
|--------|----------|------|
| 400 | 项目、车型、版本、功能不能为空 | 缺少必要的查询条件 |
| 400 | 未找到对应的KPI分析记录 | 指定条件的KPI记录不存在 |
| 400 | 未找到对应的KPI模块记录 | KPI模块表记录缺失 |
| 400 | 更新失败，错误信息: xxx | 其他未知错误 |

---

## 使用建议

1. **前置条件**：必须先调用 `POST /api/analysis/create_analysis` 创建分析记录，然后才能使用此接口更新成功率
2. **输入范围**：成功率输入值建议在 0-100 之间，超过100会按100分处理
3. **数据一致性**：更新后建议调用 `GET /api/analysis/get_analysis/{id}` 验证结果

---

## 输入输出示例

### 输入
```json
{
    "project": "ADAS测试",
    "carModel": "B10-27款",
    "version": "20260622",
    "funcMode": "NAP",
    "change_lane_success_rate": 95.5,
    "inflow_success_rate": 92.0,
    "outflow_success_rate": 93.5,
    "diverge_converge_rate": 88.0,
    "special_rate": 85.0,
    "recog_rate": 98.0
}
```

### 输出
```json
{
    "message": "成功率指标更新成功",
    "code": 200,
    "data": null
}
```