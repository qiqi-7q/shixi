# vehicle_import 接口文档

## 接口概述

| 项目 | 说明 |
|------|------|
| 接口路径 | `POST /api/vehicle/vehicle_import` |
| 请求方法 | `POST` |
| Content-Type | `multipart/form-data` |
| 功能描述 | 上传车辆资源 Excel 文件，解析数据并批量导入 Vehicle 表 |

---

## 请求参数

| 参数名 | 类型 | 位置 | 必填 | 说明 |
|--------|------|------|------|------|
| file | `UploadFile` | Body (form-data) | 是 | 车辆资源 Excel 文件，仅支持 `.xlsx` / `.xls` 格式 |

**请求示例（curl）：**

```bash
curl -X POST "http://localhost:8000/api/vehicle/vehicle_import" \
  -F "file=@车辆资源表.xlsx"
```

---

## 处理流程

```
前端上传 Excel 文件
      │
      ▼
校验文件（非空 / 后缀名）
      │
      ▼
内存读取 Excel（BytesIO + read_only 模式，不落盘）
      │  读取第一个工作表（Sheet1）
      │  第 1 行 = 表头，第 2 行起 = 数据行
      │  自动过滤全空行
      │
      ▼
单次遍历转换：中文表头映射 → 字符串类型转换 → 枚举值转换
      │
      ▼
第一重去重：内存去重（基于 vin_code + vehicle_code）
      │  过滤 Excel 文件内部的重复行
      │
      ▼
第二重去重：数据库去重（基于 vin_code + vehicle_code）
      │  过滤数据库中已存在的重复行
      │
      ▼
Pydantic 数据校验（VehicleCreate schema）
      │
      ▼
批量写入数据库（add_all + 单次 commit，事务安全）
      │
      ▼
返回导入结果统计
```

---

## Excel 文件规范

### 文件格式要求

| 要求项 | 说明 |
|--------|------|
| 文件格式 | `.xlsx` 或 `.xls` |
| 工作表 | 读取第一个工作表（Sheet1） |
| 表头行 | 第 1 行为表头 |
| 数据行 | 第 2 行起为数据 |
| 空行处理 | 全空行自动过滤 |

### 表头字段映射

Excel 表头使用**中文**，后端自动映射为英文字段名：

| Excel 表头（中文） | 对应字段 | 是否必填 | 说明 |
|-------------------|----------|----------|------|
| 车型 | model | 是 | 字符串，最长 100 字符 |
| 组别 | group | 否 | 行车组 / 泊车组 / 预警组 |
| 车辆阶段 | vehicle_stage | 否 | 字符串，最长 20 字符 |
| 车辆配置 | configuration | 否 | 字符串，最长 200 字符 |
| 车主权限 | owner_name | 是 | 字符串，最长 100 字符 |
| 车辆编号 | vehicle_code | 是 | 字符串，最长 50 字符，唯一 |
| 停车地点 | parking_location | 否 | 字符串，最长 200 字符 |
| 使用状态 | vehicle_status | 否 | 可借用 / 已借出 / 维护中 |
| 车辆状态 | test_status | 否 | 支持全部测试 / 不支持泊车测试 / 等 |
| 备注 | remarks | 否 | 文本 |
| VIN码 | vin_code | 是 | 字符串，最长 17 字符，唯一 |
| 驱动电机号/发动机号 | engine_num | 否 | 字符串，最长 100 字符 |
| 车牌号 | plate_number | 是 | 字符串，最长 20 字符 |
| 临牌到期时间 | temp_plate_expire_date | 否 | 日期格式 |
| 临牌已办理次数 | temp_plate_count | 否 | 整数，默认 0 |

### 枚举字段可选值

| 字段 | 可选值（Excel 中填写中文或英文均可） |
|------|-------------------------------------|
| group（组别） | `行车组` / `DRIVEING`，`泊车组` / `PARKING`，`预警组` / `WARNNING` |
| vehicle_status（使用状态） | `可借用` / `AVAILABLE`，`已借出` / `BORROWED`，`维护中` / `MAINTENANCE` |
| test_status（车辆状态） | `支持全部测试` / `ALL_SUPPORT`，`不支持泊车测试` / `NO_PARKING`，`不支持行车测试` / `NO_DRIVING`，`不支持后向预警测试` / `NO_BACKWARNING`，`不支持全部测试` / `NO_SUPPORT`，`生产中` / `PRODUCING`，`外借中` / `BORROWING` |

### 去重规则

- 唯一键组合：`vin_code + vehicle_code`
- 第一重去重：Excel 文件内如果存在相同 `vin_code + vehicle_code` 的行，只保留第一条
- 第二重去重：与数据库中已有数据比对，已存在的行跳过不导入

---

## 响应格式

### 成功响应（全部导入成功）

```json
{
  "code": 200,
  "message": "文件上传并导入成功",
  "data": {
    "msg": "批量导入完成",
    "total_excel_rows": 150,
    "excel_duplicate_rows": 5,
    "db_duplicate_rows": 10,
    "success_import_rows": 135,
    "failed_import_rows": 0
  }
}
```

### 成功响应（无有效数据）

```json
{
  "code": 200,
  "message": "文件中没有有效数据行",
  "data": {
    "msg": "无有效数据可导入",
    "total_excel_rows": 0,
    "excel_duplicate_rows": 0,
    "db_duplicate_rows": 0,
    "success_import_rows": 0,
    "failed_import_rows": 0
  }
}
```

### 成功响应（全部内存重复）

```json
{
  "code": 200,
  "message": "导入完成（所有数据均为 Excel 内部重复）",
  "data": {
    "msg": "无有效数据可导入",
    "total_excel_rows": 100,
    "excel_duplicate_rows": 100,
    "db_duplicate_rows": 0,
    "success_import_rows": 0,
    "failed_import_rows": 0
  }
}
```

### 成功响应（全部已在数据库）

```json
{
  "code": 200,
  "message": "导入完成（所有数据已在数据库中）",
  "data": {
    "msg": "所有数据已存在，无需导入",
    "total_excel_rows": 100,
    "excel_duplicate_rows": 0,
    "db_duplicate_rows": 100,
    "success_import_rows": 0,
    "failed_import_rows": 0
  }
}
```

### 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| code | int | 状态码，200 = 成功，400 = 失败 |
| message | string | 结果描述信息 |
| data | object / null | 导入统计数据（失败时为 null） |
| data.msg | string | 导入结果摘要 |
| data.total_excel_rows | int | Excel 读取到的有效数据总行数（过滤全空行后） |
| data.excel_duplicate_rows | int | Excel 内部过滤的重复行数（第一重去重） |
| data.db_duplicate_rows | int | 数据库中已存在的重复行数（第二重去重） |
| data.success_import_rows | int | 最终成功导入的新数据行数 |
| data.failed_import_rows | int | 导入失败的行数 |

---

## 错误响应

### 未接收到文件

```json
{
  "code": 400,
  "message": "文件上传失败：未接收到文件",
  "data": null
}
```

### 文件格式不支持

```json
{
  "code": 400,
  "message": "文件上传失败：仅支持 .xlsx 或 .xls 格式",
  "data": null
}
```

### 文件内容为空

```json
{
  "code": 400,
  "message": "文件上传失败：上传的文件内容为空",
  "data": null
}
```

### Excel 读取异常

```json
{
  "code": 400,
  "message": "文件上传失败：文件读取异常 - ...",
  "data": null
}
```

### 数据格式错误

```json
{
  "code": 400,
  "message": "第 5 行数据格式错误：...",
  "data": null
}
```

### 数据库写入失败

```json
{
  "code": 400,
  "message": "数据库写入失败：...",
  "data": null
}
```

---

## 错误码总览

| code | 说明 |
|------|------|
| 200 | 请求处理成功（含"无有效数据"等正常情况） |
| 400 | 请求失败（文件校验失败 / 格式错误 / 数据库写入失败） |