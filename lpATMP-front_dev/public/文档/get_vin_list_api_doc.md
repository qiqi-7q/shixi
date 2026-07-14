# get_vin_list 接口文档

## 接口信息

| 属性 | 值 |
| :--- | :--- |
| **HTTP 方法** | GET |
| **接口路径** | `/getvinlist` |
| **所属文件** | `router.py` |
| **函数名** | `get_vin_list` |

## 功能描述

获取车辆 VIN 码列表，返回去重后的 VIN 码数据，最多返回 20 条记录。

## 请求参数

### 路径参数

无

### 查询参数

无

### 请求体

无

### 依赖注入

| 参数名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `db` | `AsyncSession` | 异步数据库会话，由 `Depends(get_db)` 自动注入 |

## 返回结构

### 成功响应

**HTTP 状态码**: 200

```json
{
  "data": ["vin_code_1", "vin_code_2", ...],
  "message": "success",
  "code": 200
}
```

### 响应字段说明

| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `data` | `List[str]` | VIN 码字符串列表，最多包含 20 条记录 |
| `message` | `str` | 响应消息，成功时为 `"success"` |
| `code` | `int` | 状态码，成功时为 `200` |

## 数据库查询逻辑

```python
stmt = await db.execute(
    select(Vehicle.vin_code).distinct().limit(20)
)
return list(stmt.scalars().all())
```

从 `Vehicle` 表中查询不重复的 `vin_code` 字段，使用 `LIMIT 20` 限制返回数量。

## 调用示例

### cURL

```bash
curl -X GET "http://localhost:8000/getvinlist"
```

### Python (requests)

```python
import requests

response = requests.get("http://localhost:8000/getvinlist")
print(response.json())
```

### 预期返回示例

```json
{
  "data": [
    "LSGBL5337KF000001",
    "LSGBL5337KF000002",
    "LSGBL5337KF000003"
  ],
  "message": "success",
  "code": 200
}
```