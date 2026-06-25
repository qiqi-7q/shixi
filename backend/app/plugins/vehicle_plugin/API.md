# Vehicle Plugin API 接口文档

## 基础信息

- **Base URL**: `http://{host}:{port}`
- **Content-Type**: `application/json`（文件上传使用 `multipart/form-data`）
- **统一响应格式**:
  ```json
  { "data": ..., "message": "success", "code": 200 }
  ```
  | 字段 | 类型 | 说明 |
  |------|------|------|
  | data | any | 响应数据（对象/数组/null） |
  | message | string | 提示信息 |
  | code | int | 状态码（200 成功，400 失败） |

---

## 一、车辆管理 `/api/vehicle`

### 1.1 获取车辆概览统计 `GET /api/vehicle/stats/overview`

**请求参数** (Query)：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| model | string | 否 | 车型 |
| vin_code | string | 否 | VIN码 |
| group | string | 否 | 组别 |
| vehicle_status | string | 否 | 使用状态 |
| test_status | string | 否 | 车辆状态 |
| start_date | string | 否 | 起始日期 (YYYY-MM-DD) |
| end_date | string | 否 | 截止日期 (YYYY-MM-DD) |

**响应** `data`：
```json
{
  "total": 100,
  "available": 60,
  "borrowed": 20,
  "maintenance": 10,
  "reserved": 10
}
```
| 字段 | 类型 | 说明 |
|------|------|------|
| total | int | 总车辆数 |
| available | int | 可借用数 |
| borrowed | int | 已借出数 |
| maintenance | int | 维护中数 |
| reserved | int | 已预定数 |

---

### 1.2 获取车辆使用率统计 `GET /api/vehicle/stats/utilization`

**请求参数** (Query)：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| model | string | 否 | 车型（模糊匹配） |
| vin_code | string | 否 | VIN码（模糊匹配） |
| group | string | 否 | 组别 |
| vehicle_status | string | 否 | 使用状态 |
| test_status | string | 否 | 车辆状态 |
| start_date | string | 否 | 开始日期 (YYYY-MM-DD) |
| end_date | string | 否 | 结束日期 (YYYY-MM-DD) |

**响应** `data`：
```json
[
  {
    "vehicle_id": 1,
    "model": "C16_26款",
    "vehicle_code": "274",
    "vin_code": "LFZ93AN94SD000274",
    "borrow_count": 5,
    "percentage": 12.5
  }
]
```
| 字段 | 类型 | 说明 |
|------|------|------|
| vehicle_id | int | 车辆ID |
| model | string | 车型 |
| vehicle_code | string | 车辆编号 |
| vin_code | string | VIN码 |
| borrow_count | int | 借用次数（同天多次算1次） |
| percentage | float | 占比（%） |

---

### 1.3 获取车辆状态分布 `GET /api/vehicle/stats/status_distribution`

**请求参数** (Query)：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| model | string | 否 | 车型 |
| vin_code | string | 否 | VIN码 |
| group | string | 否 | 组别 |
| vehicle_status | string | 否 | 使用状态 |
| test_status | string | 否 | 车辆状态 |

**响应** `data`：
```json
[
  { "name": "可借用", "value": 60 },
  { "name": "已借出", "value": 20 },
  { "name": "维护中", "value": 10 },
  { "name": "已预定", "value": 10 }
]
```
| 字段 | 类型 | 说明 |
|------|------|------|
| name | string | 状态名称 |
| value | int | 数量 |

---

### 1.4 高级查询车辆 `POST /api/vehicle/advsearch`

**请求参数** (Query)：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skip | int | 否 | 偏移量，默认 0 |
| limit | int | 否 | 每页数量，默认 100，最大 1000 |

**请求体** `conditions`：
```json
[
  {
    "advanced_field": "model",
    "advanced_operator": "like",
    "advanced_value": "C16"
  }
]
```
> 时间字段 `created_at`, `updated_at` 仅支持 `between` / `not_between`，value 为 `["2026-01-01", "2026-06-30"]`

**响应** `data`：`VehicleResponse[]`（见下方通用结构）

---

### 1.5 固定字段查询车辆 `GET /api/vehicle/fixsearch`

**请求参数** (Query)：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skip | int | 否 | 偏移量，默认 0 |
| limit | int | 否 | 每页数量，默认 100 |
| model | string | 否 | 车型 |
| vin_code | string | 否 | VIN码 |
| group | string | 否 | 组别 |
| vehicle_status | string | 否 | 使用状态 |
| test_status | string | 否 | 车辆状态 |

**响应** `data`：`VehicleResponse[]`

---

### 1.6 创建车辆 `POST /api/vehicle/createvehicle`

**请求体** `VehicleCreate`：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| model | string | 否 | 车型，最长 100 |
| vehicle_code | string | 否 | 车辆编号，最长 50 |
| vin_code | string | **是** | VIN码，最长 17 |
| owner_name | string | 否 | 车主，最长 100 |
| plate_number | string | 否 | 车牌号，最长 20 |
| group | enum | 否 | 组别：行车组/泊车组/预警组 |
| vehicle_status | enum | 否 | 使用状态：可借用/已借出/维护中/已预定 |
| test_status | enum | 否 | 车辆测试状态 |
| vehicle_stage | string | 否 | 车辆阶段，最长 20 |
| configuration | string | 否 | 车辆配置，最长 200 |
| parking_location | string | 否 | 停车地点，最长 200 |
| engine_num | string | 否 | 电机号/发动机号，最长 100 |
| temp_plate_expire_date | date | 否 | 临牌到期时间 (YYYY-MM-DD) |
| temp_plate_count | int | 否 | 临牌数量 |
| remarks | string | 否 | 备注 |

**响应**：
```json
{ "data": null, "message": "车辆信息创建成功", "code": 200 }
```

---

### 1.7 获取车辆 `GET /api/vehicle/getvehicle/{vehicle_id}`

**请求参数**：

| 参数 | 类型 | 必填 | 位置 | 说明 |
|------|------|------|------|------|
| vehicle_id | int | 是 | Path | 车辆ID |

**响应** `data` (`VehicleResponse`)：
```json
{
  "id": 1,
  "model": "C16_26款",
  "vehicle_code": "274",
  "vin_code": "LFZ93AN94SD000274",
  "owner_name": "张三",
  "plate_number": "浙G3599试",
  "group": "泊车组",
  "vehicle_status": "可借用",
  "test_status": "支持全部测试",
  "vehicle_stage": "PPV",
  "configuration": "增程高配",
  "parking_location": "一分厂",
  "engine_num": "25564082",
  "temp_plate_expire_date": "2026-09-21",
  "temp_plate_count": 0,
  "remarks": "",
  "created_at": "2026-01-01T00:00:00",
  "updated_at": "2026-06-24T00:00:00"
}
```

---

### 1.8 获取车辆状态 `GET /api/vehicle/getstatus/{vehicle_id}`

**请求参数**：

| 参数 | 类型 | 必填 | 位置 | 说明 |
|------|------|------|------|------|
| vehicle_id | int | 是 | Path | 车辆ID |

**响应** `data`：`VehicleResponse`

---

### 1.9 更新车辆 `PUT /api/vehicle/updatevehicle/{vehicle_id}`

**请求参数**：

| 参数 | 类型 | 必填 | 位置 | 说明 |
|------|------|------|------|------|
| vehicle_id | int | 是 | Path | 车辆ID |

**请求体** `VehicleUpdate`：所有字段同 `VehicleCreate`，但全部可选，仅更新传入字段。

**响应**：
```json
{ "data": null, "message": "车辆信息更新成功", "code": 200 }
```

---

### 1.10 删除车辆 `DELETE /api/vehicle/delvehicle/{vehicle_id}`

**请求参数**：

| 参数 | 类型 | 必填 | 位置 | 说明 |
|------|------|------|------|------|
| vehicle_id | int | 是 | Path | 车辆ID |

**响应**：
```json
{ "data": null, "message": "车辆信息删除成功", "code": 200 }
```

---

### 1.11 Excel 批量导入 `POST /api/vehicle/vehicle_import`

**请求参数**：

| 参数 | 类型 | 必填 | 位置 | 说明 |
|------|------|------|------|------|
| file | file | 是 | Form | Excel 文件 (.xlsx/.xls) |

**响应**：
```json
{ "data": null, "message": "导入成功，共导入 X 条记录", "code": 200 }
```
> 除 vin_code 外，其他字段均可为空

---

## 二、借用管理 `/api/borrow`

### 2.1 借用概览统计 `GET /api/borrow/stats/overview`

**请求参数** (Query)：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| model | string | 否 | 车型 |
| vin_code | string | 否 | VIN码 |
| borrow_status | string | 否 | 借用状态 |
| driver_name | string | 否 | 司机姓名 |

**响应** `data`：
```json
{
  "total": 50,
  "borrowing": 5,
  "returned": 40,
  "cancelled": 3,
  "reserved": 2
}
```
| 字段 | 类型 | 说明 |
|------|------|------|
| total | int | 总借用记录数 |
| borrowing | int | 借用中 |
| returned | int | 已归还 |
| cancelled | int | 已取消 |
| reserved | int | 已预约 |

---

### 2.2 借用状态分布 `GET /api/borrow/stats/status_distribution`

**请求参数** (Query)：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| model | string | 否 | 车型 |
| vin_code | string | 否 | VIN码 |
| borrow_status | string | 否 | 借用状态 |
| driver_name | string | 否 | 司机姓名 |

**响应** `data`：
```json
[
  { "name": "borrowing", "value": 5 },
  { "name": "returned", "value": 40 },
  { "name": "cancelled", "value": 3 },
  { "name": "reserved", "value": 2 }
]
```

---

### 2.3 高级查询借用记录 `POST /api/borrow/advsearch`

**请求参数** (Query)：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skip | int | 否 | 偏移量，默认 0 |
| limit | int | 否 | 每页数量，默认 100 |

**请求体** `conditions`：同车辆高级查询格式。
> 时间字段 `created_at`, `updated_at`, `borrow_time` 仅支持 `between` / `not_between`

**响应** `data`：`BorrowRecordResponse[]`

---

### 2.4 固定字段查询借用记录 `GET /api/borrow/fixsearch`

**请求参数** (Query)：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skip | int | 否 | 偏移量 |
| limit | int | 否 | 每页数量 |
| model | string | 否 | 车型 |
| vin_code | string | 否 | VIN码 |
| borrow_status | string | 否 | 借用状态 |
| driver_name | string | 否 | 司机姓名 |

**响应** `data`：`BorrowRecordResponse[]`

---

### 2.5 获取车辆其他借用记录 `POST /api/borrow/borrowed`

**请求参数** (Query)：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| record_id | int | 是 | 当前记录ID（排除自身） |
| vehicle_id | int | 是 | 车辆ID |

**说明**：借车时判断该车在当天及未来是否有其他借用/预约。

**响应** `data`：
```json
[
  {
    "borrower": "张三",
    "borrow_time": "2026-06-25"
  }
]
```
| 字段 | 类型 | 说明 |
|------|------|------|
| borrower | string | 借用人 |
| borrow_time | date | 借用时间 |

---

### 2.6 创建借用记录 `POST /api/borrow/createborrow`

**请求体** `BorrowRecordCreate`：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| vehicle_id | int | **是** | 车辆ID |
| vin_code | string | **是** | VIN码，最长 17 |
| borrower | string | **是** | 借用人，最长 100 |
| borrow_time | date | **是** | 借用时间 (YYYY-MM-DD) |
| model | string | 否 | 车型 |
| vehicle_code | string | 否 | 车辆编号 |
| driver_name | string | 否 | 司机姓名 |
| driver_work | string | 否 | 司机工作安排 |
| driver_performance | string | 否 | 司机绩效 |
| record_creator | string | 否 | 记录创建人 |
| borrow_status | string | 否 | 借用状态 |
| remarks | string | 否 | 备注 |

**响应**：
```json
{ "data": null, "message": "借用记录创建成功", "code": 200 }
```

---

### 2.7 获取借用记录 `GET /api/borrow/getborrow/{record_id}`

**请求参数**：

| 参数 | 类型 | 必填 | 位置 | 说明 |
|------|------|------|------|------|
| record_id | int | 是 | Path | 记录ID |

**响应** `data` (`BorrowRecordResponse`)：
```json
{
  "id": 1,
  "vehicle_id": 1,
  "model": "C16_26款",
  "vehicle_code": "274",
  "vin_code": "LFZ93AN94SD000274",
  "borrower": "张三",
  "borrow_time": "2026-06-24",
  "driver_name": "李四",
  "driver_work": "路试",
  "driver_performance": "8h+200km",
  "record_creator": "王五",
  "borrow_status": "borrowing",
  "remarks": "",
  "created_at": "2026-06-24",
  "updated_at": "2026-06-24"
}
```

---

### 2.8 更新借用记录 `PUT /api/borrow/updateborrow/{record_id}`

**请求参数**：

| 参数 | 类型 | 必填 | 位置 | 说明 |
|------|------|------|------|------|
| record_id | int | 是 | Path | 记录ID |

**请求体** `BorrowRecordUpdate`：所有字段同 `BorrowRecordCreate`，全部可选。

**响应**：
```json
{ "data": null, "message": "借用记录更新成功", "code": 200 }
```

---

### 2.9 删除借用记录 `DELETE /api/borrow/delborrow/{record_id}`

**请求参数**：

| 参数 | 类型 | 必填 | 位置 | 说明 |
|------|------|------|------|------|
| record_id | int | 是 | Path | 记录ID |

**响应**：
```json
{ "data": null, "message": "借用记录删除成功", "code": 200 }
```

---

### 2.10 归还车辆 `POST /api/borrow/returnvehicle/{record_id}`

**请求参数**：

| 参数 | 类型 | 必填 | 位置 | 说明 |
|------|------|------|------|------|
| record_id | int | 是 | Path | 记录ID |

**说明**：borrow_status → `returned`，同时自动更新车辆状态（若无其他今日借用/未来预约则设为 `可借用`）。

**响应**：
```json
{ "data": null, "message": "车辆已归还", "code": 200 }
```

---

### 2.11 取消借用 `POST /api/borrow/cancelborrow/{record_id}`

**请求参数**：

| 参数 | 类型 | 必填 | 位置 | 说明 |
|------|------|------|------|------|
| record_id | int | 是 | Path | 记录ID |

**说明**：borrow_status → `cancelled`，同时自动更新车辆状态。

**响应**：
```json
{ "data": null, "message": "借用记录取消成功", "code": 200 }
```

---

## 三、枚举值

### 车辆使用状态 (vehicle_status)
| 值 | 说明 |
|------|------|
| 可借用 | 空闲可用 |
| 已借出 | 已被借出 |
| 维护中 | 正在维护 |
| 已预定 | 已被预约 |

### 车辆测试状态 (test_status)
| 值 |
|------|
| 支持全部测试 |
| 不支持泊车测试 |
| 不支持行车测试 |
| 不支持后向预警测试 |
| 不支持全部测试 |
| 生产中 |
| 外借中 |

### 借用记录状态 (borrow_status)
| 值 | 说明 |
|------|------|
| borrowing | 借用中 |
| returned | 已归还 |
| cancelled | 已取消 |
| reserved | 已预约 |

### 组别 (group)
| 值 | 说明 |
|------|------|
| 行车组 | 行车测试 |
| 泊车组 | 泊车测试 |
| 预警组 | 预警测试 |

---

## 四、定时任务

| 任务 | 执行时间 | 说明 |
|------|------|------|
| re_vs_task | 每日 00:30 | 根据借用记录更新车辆使用状态 |
| re_bs_task | 每日 01:00 | 过期借用记录自动标记为已归还 |