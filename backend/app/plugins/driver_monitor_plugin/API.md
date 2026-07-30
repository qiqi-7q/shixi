# Driver Monitor Plugin 接口文档

## 基本信息

- **路由前缀**：`/api/driver_monitor`
- **Tags**：司机监控
- **统一响应格式**：

```json
{
  "code": 200,
  "message": "操作成功",
  "data": ...
}
```

- **错误码说明**：

| code | 含义 |
|---|---|
| 200 | 成功 |
| 400 | 失败（平台返回错误、参数错误等） |

- **时间格式**：未特别说明时，时间字符串格式为 `YYYY-MM-DD HH:MM:SS`

---

## 一、平台接口（本地数据库）

### 1. 获取监控信息

`GET /api/driver_monitor/info`

查询本地数据库中的驾驶员监控记录，支持按 VIN、时间范围过滤和分页。

**请求参数**（Query）：

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| vin_code | string | 否 | - | 测试车辆 VIN 号 |
| start_time | string | 否 | - | 开始时间 |
| end_time | string | 否 | - | 结束时间 |
| sort_by | string | 否 | - | 排序字段 |
| sort_order | string | 否 | - | 排序方向（asc/desc） |
| page | int | 否 | 1 | 页码，≥1 |
| page_size | int | 否 | 10 | 每页数量，1-100 |

**请求示例**：

```
GET /api/driver_monitor/info?vin_code=LSVAM4187C2014001&page=1&page_size=10
```

**响应示例**：

```json
{
  "code": 200,
  "message": "获取监控信息成功",
  "data": {
    "items": [
      {
        "id": 1,
        "test_date": "2026-07-28",
        "vin_code": "LSVAM4187C2014001",
        "device_code": "527086498786",
        "fatigue": 2,
        "calling": 0,
        "smoke": 1,
        "distract": 3,
        "abnormal": 0,
        "snapshot": 5,
        "driver_change": 1,
        "no_belt": 0,
        "mileage": 156.8,
        "duration": 28800,
        "remark": "测试记录",
        "created_at": "2026-07-28T10:00:00",
        "updated_at": "2026-07-28T10:00:00"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10
  }
}
```

**返回参数解析**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码，200 成功，400 失败 |
| message | string | 状态描述 |
| data | object | 数据对象 |
| data.items | array | 监控记录列表 |
| data.items[].id | int | 记录 ID |
| data.items[].test_date | string | 测试日期 `YYYY-MM-DD` |
| data.items[].vin_code | string | 车辆 VIN 号（17 位） |
| data.items[].device_code | string | 设备号 |
| data.items[].fatigue | int | 疲劳驾驶次数 |
| data.items[].calling | int | 接打电话次数 |
| data.items[].smoke | int | 抽烟次数 |
| data.items[].distract | int | 分神驾驶次数 |
| data.items[].abnormal | int | 驾驶员异常次数 |
| data.items[].snapshot | int | 自动抓拍次数 |
| data.items[].driver_change | int | 驾驶员变更次数 |
| data.items[].no_belt | int | 未系安全带次数 |
| data.items[].mileage | decimal | 行驶里程（km） |
| data.items[].duration | int | 车辆上电时长（秒） |
| data.items[].remark | string | 备注 |
| data.items[].created_at | datetime | 创建时间 |
| data.items[].updated_at | datetime | 更新时间 |
| data.total | int | 总记录数 |
| data.page | int | 当前页码 |
| data.page_size | int | 每页数量 |

---

## 二、第三方平台接口（iotsmart 转发）

> 以下接口均通过 token 认证后转发到 iotsmart 平台，token 由后端自动获取管理。返回的 `data` 字段直接透传 iotsmart 平台原始响应的 `data` 部分。

### 2. 获取用户车辆基础信息

`GET /api/driver_monitor/car_info`

获取当前账号下所有车辆的基础信息。

**请求示例**：

```
GET /api/driver_monitor/car_info
```

**响应示例**：

```json
{
  "code": 200,
  "message": "获取用户车辆基础信息成功",
  "data": {
    "hdr": {"code": 200, "msgType": 1234},
    "vehicleInfo": [
      {"vehicleGuid": 14307, "vehicleNo": "527086498786"},
      {"vehicleGuid": 14349, "vehicleNo": "527086468243"}
    ]
  }
}
```

**返回参数解析**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| message | string | 状态描述 |
| data | object | iotsmart 平台原始数据 |
| data.hdr | object | 响应头 |
| data.hdr.code | int | 平台状态码，200 成功 |
| data.hdr.msgType | int | 消息类型 |
| data.vehicleInfo | array | 车辆信息列表 |
| data.vehicleInfo[].vehicleGuid | int | 车辆 GUID（全局唯一） |
| data.vehicleInfo[].vehicleNo | string | 车牌号 |

### 3. 实时视频

`GET /api/driver_monitor/realtime_audio`

请求指定车辆指定通道的实时视频流。

**请求参数**（Query）：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| vehicleNo | string | 是 | 车牌号 |
| channelNo | int | 是 | 通道号 |

**请求示例**：

```
GET /api/driver_monitor/realtime_audio?vehicleNo=527086498786&channelNo=1
```

**响应示例**：

```json
{
  "code": 200,
  "message": "获取实时视频成功",
  "data": {
    "streamID": "abc123",
    "url": "http://10.192.8.193:8012/live/abc123.flv",
    "deviceSn": "527086498786",
    "channelNo": 1
  }
}
```

**返回参数解析**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| message | string | 状态描述 |
| data | object | 实时视频流信息 |
| data.streamID | string | 流 ID（用于控制、关闭等后续操作） |
| data.url | string | 播放地址（FLV/HLS 流） |
| data.deviceSn | string | 设备序列号 |
| data.channelNo | int | 通道号 |

### 4. 实时音频监听

`GET /api/driver_monitor/realtime_monitor`

监听指定车辆指定通道的实时音频。

**请求参数**（Query）：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| vehicleNo | string | 是 | 车牌号 |
| channelNo | int | 是 | 通道号 |

**请求示例**：

```
GET /api/driver_monitor/realtime_monitor?vehicleNo=527086498786&channelNo=1
```

**返回参数解析**：同 [3. 实时视频](#3-实时视频)。

### 5. 实时对讲

`GET /api/driver_monitor/realtime_talk`

与指定车辆进行实时对讲。

**请求参数**（Query）：

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| vehicleNo | string | 是 | - | 车牌号 |
| channelNo | int | 是 | - | 通道号 |
| playerProtocol | int | 否 | 2 | 播放协议（1-RTSP，2-FLV，3-HLS） |

**请求示例**：

```
GET /api/driver_monitor/realtime_talk?vehicleNo=527086498786&channelNo=1&playerProtocol=2
```

**返回参数解析**：同 [3. 实时视频](#3-实时视频)。

### 6. 视频回放-获取媒体列表

`GET /api/driver_monitor/media_list`

查询指定时间范围内的录像媒体列表。

**请求参数**（Query）：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| vehicleNo | string | 是 | 车牌号 |
| startTime | string | 是 | 开始时间 `YYYY-MM-DD HH:MM:SS` |
| endTime | string | 是 | 结束时间 |
| channelNo | int | 否 | 通道号 |
| alarmFlag | int | 否 | 报警标志（0-全部，1-报警录像） |
| mediaType | int | 否 | 媒体类型（0-视频，1-音频，2-音视频） |
| bitStreamType | int | 否 | 码流类型（0-主码流，1-子码流） |
| storageType | int | 否 | 存储类型（0-设备，1-平台） |

**请求示例**：

```
GET /api/driver_monitor/media_list?vehicleNo=527086498786&startTime=2026-07-28 00:00:00&endTime=2026-07-28 23:59:59&channelNo=1
```

**响应示例**：

```json
{
  "code": 200,
  "message": "获取视频回放媒体列表成功",
  "data": {
    "hdr": {"code": 200, "msgType": 1234},
    "mediaList": [
      {
        "channelNo": 1,
        "startTime": "2026-07-28 08:00:00",
        "endTime": "2026-07-28 09:00:00",
        "mediaType": 0,
        "storageType": 0,
        "bitStreamType": 0,
        "alarmFlag": 0
      }
    ]
  }
}
```

**返回参数解析**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| message | string | 状态描述 |
| data | object | iotsmart 平台原始数据 |
| data.hdr | object | 响应头 |
| data.mediaList | array | 媒体列表 |
| data.mediaList[].channelNo | int | 通道号 |
| data.mediaList[].startTime | string | 录像开始时间 `YYYY-MM-DD HH:MM:SS` |
| data.mediaList[].endTime | string | 录像结束时间 |
| data.mediaList[].mediaType | int | 媒体类型（0-视频，1-音频，2-音视频） |
| data.mediaList[].storageType | int | 存储类型（0-设备，1-平台） |
| data.mediaList[].bitStreamType | int | 码流类型（0-主码流，1-子码流） |
| data.mediaList[].alarmFlag | int | 报警标志（0-普通，1-报警） |

### 7. 视频回放-请求历史流

`GET /api/driver_monitor/history_video`

请求指定时间范围内的历史视频流。

**请求参数**（Query）：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| vehicleNo | string | 是 | 车牌号 |
| channelNo | int | 是 | 通道号 |
| startTime | string | 是 | 开始时间 `YYYY-MM-DD HH:MM:SS` |
| endTime | string | 是 | 结束时间 |
| playType | int | 否 | 播放类型（0-播放，1-下载） |
| mediaType | int | 否 | 媒体类型 |
| speed | int | 否 | 倍速（1-正常，2-2倍，4-4倍） |
| storageType | int | 否 | 存储类型（0-设备，1-平台） |
| isDownload | bool | 否 | 是否下载 |
| isSubCode | bool | 否 | 是否子码流 |

**请求示例**：

```
GET /api/driver_monitor/history_video?vehicleNo=527086498786&channelNo=1&startTime=2026-07-28 08:00:00&endTime=2026-07-28 09:00:00
```

**返回参数解析**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| message | string | 状态描述 |
| data | object | 历史流信息 |
| data.streamID | string | 流 ID（用于回放控制、获取进度） |
| data.url | string | 播放地址 |
| data.deviceSn | string | 设备序列号 |
| data.channelNo | int | 通道号 |

### 8. 视频回放-控制

`GET /api/driver_monitor/ctrl_history_video`

控制历史视频回放（播放/暂停/拖拽/倍速）。

**请求参数**（Query）：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| vehicleNo | string | 是 | 车牌号 |
| channelNo | int | 是 | 通道号 |
| ctrlType | int | 否 | 控制类型（0-播放，1-暂停，2-拖拽） |
| speed | int | 否 | 倍速 |
| dragTime | string | 否 | 格式："YYYY-MM-DD HH:MM:SS" |

**请求参数解析**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| message | string | 状态描述 |
| data | object | 控制结果 |

### 9. 视频回放-获取播放进度

`GET /api/driver_monitor/playback_time`

获取当前历史视频的播放进度。

**请求参数**（Query）：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| zlmStreamID | string | 是 | 流 ID（请求历史流时返回） |

**请求示例**：

```
GET /api/driver_monitor/playback_time?zlmStreamID=abc123
```

**返回参数解析**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| message | string | 状态描述 |
| data | object | 播放进度信息 |
| data.currentTime | int | 当前播放时间（秒） |
| data.totalTime | int | 总时长（秒） |
| data.progress | int | 进度百分比（0-100） |

### 10. 视频回放-获取下载的 streamID

`GET /api/driver_monitor/streamid`

获取已下载视频的 streamID。

**请求参数**（Query）：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| deviceNo | string | 是 | 设备号 |
| startTime | int | 是 | 开始时间戳（秒） |
| endTime | int | 是 | 结束时间戳（秒） |

**请求示例**：

```
GET /api/driver_monitor/streamid?startTime=1785224102&endTime=1785224402
```

**返回参数解析**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| message | string | 状态描述 |
| data | string | streamID |

### 11. 录像下载-获取下载进度

`GET /api/driver_monitor/download_progress`

查询录像下载进度。

**请求参数**（Query）：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| streamID | string | 是 | 流 ID |
| deviceNo | string | 是 | 设备号 |

**请求示例**：

```
GET /api/driver_monitor/download_progress?streamID=abc123&deviceNo=527086498786
```

**响应示例**：

```json
{
  "code": 200,
  "message": "获取录像下载进度成功",
  "data": {
    "hdr": {"code": 200, "msgType": 1234},
    "progress": 65,
    "status": 1
  }
}
```

**返回参数解析**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| message | string | 状态描述 |
| data | object | 下载进度信息 |
| data.hdr | object | 响应头 |
| data.progress | int | 下载进度（0-100） |
| data.status | int | 下载状态（0-下载中，1-已完成，2-失败） |



### 12. 录像下载-下载到本地

`GET /api/driver_monitor/file_download`

将已下载完成的录像文件下载到本地。

**请求参数**（Query）：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| streamID | string | 是 | 流 ID |
| fileName | string | 是 | 保存的文件名 |

**请求示例**：

```
GET /api/driver_monitor/file_download?streamID=abc123&fileName=video_20260728.mp4
```

**返回**：`StreamingResponse`，二进制文件流。

**返回头解析**：

| 字段 | 类型 | 说明 |
|---|---|---|
| Content-Type | string | 文件 MIME 类型（如 `video/mp4`） |
| Content-Disposition | string | `attachment; filename="video_20260728.mp4"` |

### 13. 获取 WebSocket 服务器信息

`GET /api/driver_monitor/ws_info`

获取 iotsmart 平台 WebSocket 服务器地址等信息。

**请求示例**：

```
GET /api/driver_monitor/ws_info
```

**返回参数解析**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| message | string | 状态描述 |
| data | object | WS 服务器信息 |
| data.wsUrl | string | WebSocket 服务器地址 |
| data.port | int | 端口 |

---

## 三、iotsmart 平台拓展接口

### 14. 获取用户分组信息

`GET /api/driver_monitor/user_org`

获取当前账号的用户分组（组织）信息。

**请求示例**：

```
GET /api/driver_monitor/user_org
```

**返回参数解析**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| message | string | 状态描述 |
| data | object | 用户分组信息 |
| data.hdr | object | 响应头 |
| data.orgList | array | 组织列表 |
| data.orgList[].orgGuid | int | 组织 GUID |
| data.orgList[].orgName | string | 组织名称 |

### 15. 查询单页轨迹数据

`GET /api/driver_monitor/track_page`

查询单台车辆在指定时间范围内的单页轨迹数据。

**请求参数**（Query）：

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| vehicleNo | string | 是 | - | 车牌号 |
| startTime | string | 是 | - | 开始时间 `YYYY-MM-DD HH:MM:SS` |
| endTime | string | 是 | - | 结束时间 |
| curPage | int | 否 | 1 | 页码 |
| pageNum | int | 否 | 100 | 每页数量 |

**请求示例**：

```
GET /api/driver_monitor/track_page?vehicleNo=527086498786&startTime=2026-07-28 08:00:00&endTime=2026-07-28 09:00:00&curPage=1&pageNum=100
```

**响应示例**：

```json
{
  "code": 200,
  "message": "查询单页轨迹成功",
  "data": {
    "hdr": {"code": 200, "msgType": 1234},
    "trackList": [
      {
        "devNo": "527086498786",
        "time": 1785224102,
        "longitude": 120061486,
        "latitude": 30178434,
        "speed": 822,
        "direction": 139,
        "altitude": 26,
        "vehicleGuid": 14307,
        "vehicleNo": "527086498786"
      }
    ],
    "total": 1,
    "curPage": 1,
    "pageNum": 100
  }
}
```

**返回参数解析**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| message | string | 状态描述 |
| data | object | 轨迹数据 |
| data.hdr | object | 响应头 |
| data.trackList | array | 轨迹点列表（按时间升序） |
| data.trackList[].devNo | string | 设备号 |
| data.trackList[].time | int | 定位时间戳（秒） |
| data.trackList[].longitude | int | 经度（×10^6，如 120.061486° → 120061486） |
| data.trackList[].latitude | int | 纬度（×10^6） |
| data.trackList[].speed | int | 速度（×10，km/h，如 82.2 km/h → 822） |
| data.trackList[].direction | int | 方向（0-359，正北为 0，顺时针） |
| data.trackList[].altitude | int | 海拔（米） |
| data.trackList[].vehicleGuid | int | 车辆 GUID |
| data.trackList[].vehicleNo | string | 车牌号 |
| data.total | int | 总记录数 |
| data.curPage | int | 当前页码 |
| data.pageNum | int | 每页数量 |

### 16. 查询全部轨迹数据

`GET /api/driver_monitor/track_all`

查询单台车辆在指定时间范围内的全部轨迹数据（自动分页拉取）。

**请求参数**（Query）：

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| vehicleNo | string | 是 | - | 车牌号 |
| startTime | string | 是 | - | 开始时间 `YYYY-MM-DD HH:MM:SS` |
| endTime | string | 是 | - | 结束时间 |
| pageNum | int | 否 | 100 | 每页数量（内部循环使用） |

**请求示例**：

```
GET /api/driver_monitor/track_all?vehicleNo=527086498786&startTime=2026-07-28 08:00:00&endTime=2026-07-28 09:00:00
```

**响应示例**：

```json
{
  "code": 200,
  "message": "查询全部轨迹成功",
  "data": [
    {
      "devNo": "527086498786",
      "time": 1785224102,
      "longitude": 120061486,
      "latitude": 30178434,
      "speed": 822,
      "direction": 139
    }
  ],
  "total": 1
}
```

**返回参数解析**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| message | string | 状态描述 |
| data | array | 全部轨迹点列表（已合并所有分页） |
| data[].devNo | string | 设备号 |
| data[].time | int | 定位时间戳（秒） |
| data[].longitude | int | 经度（×10^6） |
| data[].latitude | int | 纬度（×10^6） |
| data[].speed | int | 速度（×10，km/h） |
| data[].direction | int | 方向（0-359） |
| data[].altitude | int | 海拔（米） |
| data[].vehicleGuid | int | 车辆 GUID |
| data[].vehicleNo | string | 车牌号 |
| total | int | 总记录数 |

### 17. 获取所有车辆最后状态

`GET /api/driver_monitor/last_vehicle_status`

获取当前账号下所有车辆的最后状态（含最后定位数据）。

**请求示例**：

```
GET /api/driver_monitor/last_vehicle_status
```

**响应示例**：

```json
{
  "code": 200,
  "message": "获取所有车辆最后状态成功",
  "data": [
    {
      "devNo": "527086498786",
      "vehicleGuid": 14307,
      "vehicleNo": "527086498786",
      "time": 1785224102,
      "longitude": 120061486,
      "latitude": 30178434,
      "speed": 822,
      "direction": 139,
      "altitude": 26,
      "deviceMileage": 426900,
      "platformMileage": 441891
    }
  ]
}
```

**返回参数解析**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| message | string | 状态描述 |
| data | array | 车辆状态列表 |
| data[].devNo | string | 设备号 |
| data[].vehicleGuid | int | 车辆 GUID |
| data[].vehicleNo | string | 车牌号 |
| data[].time | int | 最后定位时间戳（秒） |
| data[].longitude | int | 经度（×10^6） |
| data[].latitude | int | 纬度（×10^6） |
| data[].speed | int | 速度（×10，km/h） |
| data[].direction | int | 方向（0-359） |
| data[].altitude | int | 海拔（米） |
| data[].deviceMileage | int | 设备里程（米） |
| data[].platformMileage | int | 平台里程（米） |

### 18. 获取指定车辆最后位置

`GET /api/driver_monitor/vehicle_last_position`

获取指定车辆的最后位置信息。

**请求参数**（Query）：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| vehicleNo | string | 是 | 车牌号 |

**请求示例**：

```
GET /api/driver_monitor/vehicle_last_position?vehicleNo=527086498786
```

**返回参数解析**：返回单个对象，字段同 [17. 获取所有车辆最后状态](#17-获取所有车辆最后状态) 中 `data[]` 的结构。

### 19. 终端重启（批量）

`GET /api/driver_monitor/device_reboot`

向多台车辆终端下发重启指令。

**请求参数**（Query）：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| vehicleNos | string | 是 | 车牌号，多个用英文逗号分隔 |

**请求示例**：

```
GET /api/driver_monitor/device_reboot?vehicleNos=527086498786,527086468243
```

**返回参数解析**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| message | string | 状态描述 |
| data | object | 下发结果 |
| data.hdr | object | 响应头 |
| data.hdr.code | int | 平台状态码，200 成功 |
| data.successList | array | 成功车牌列表 |
| data.failList | array | 失败车牌列表 |

### 20. 重启单台车辆

`GET /api/driver_monitor/restart_vehicle`

向单台车辆终端下发重启指令。

**请求参数**（Query）：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| vehicleNo | string | 是 | 车牌号 |

**返回参数解析**：同 [19. 终端重启](#19-终端重启批量)。

### 21. 下发文本到终端（批量）

`GET /api/driver_monitor/device_text`

向多台车辆终端下发文本信息（在终端屏幕上显示）。

**请求参数**（Query）：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| vehicleNos | string | 是 | 车牌号，多个用英文逗号分隔 |
| text | string | 是 | 文本内容 |
| flag | int | 否 | 显示标志（0-紧急，1-普通） |
| taskName | string | 否 | 任务名 |

**请求示例**：

```
GET /api/driver_monitor/device_text?vehicleNos=527086498786&text=请减速行驶&flag=1
```

**返回参数解析**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| message | string | 状态描述 |
| data | object | 下发结果 |
| data.hdr | object | 响应头 |
| data.taskId | string | 任务 ID |

### 22. 查询 WebSocket 状态

`GET /api/driver_monitor/ws_status`

查询后端与 iotsmart 平台 WebSocket 长连接的运行状态。

**请求示例**：

```
GET /api/driver_monitor/ws_status
```

**响应示例**：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "running": true
  }
}
```

**返回参数解析**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| message | string | 状态描述 |
| data | object | 状态信息 |
| data.running | bool | WS 是否运行中（true-运行，false-未运行） |

### 23. 获取定位数据

`GET /api/driver_monitor/location_data`

从 MinIO 读取定位数据。每 30 秒落盘一次。

**请求参数**（Query）：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| devNo | string | 否 | 设备号。不传返回所有设备号列表；传了返回该设备当天的全部点位 |

**请求示例 1**（获取所有设备号列表）：

```
GET /api/driver_monitor/location_data
```

**响应示例 1**：

```json
{
  "code": 200,
  "message": "获取设备列表成功",
  "data": {
    "devNos": ["527086498786", "527086468243"]
  }
}
```

**返回参数解析 1**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| message | string | 状态描述 |
| data | object | 数据对象 |
| data.devNos | array | 设备号列表 |

**请求示例 2**（获取指定设备当天定位数据）：

```
GET /api/driver_monitor/location_data?devNo=527086498786
```

**响应示例 2**：

```json
{
  "code": 200,
  "message": "获取定位数据成功",
  "data": {
    "items": [
      {
        "devNo": "527086498786",
        "time": 1785224102,
        "longitude": 120061486,
        "latitude": 30178434,
        "speed": 822,
        "direction": 139,
        "altitude": 26,
        "vehicleGuid": 14307,
        "vehicleNo": "527086498786",
        "receiveTime": 1785224104,
        "deviceMileage": 426900,
        "platformMileage": 441891
      }
    ],
    "total": 1
  }
}
```

**返回参数解析 2**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| message | string | 状态描述 |
| data | object | 数据对象 |
| data.items | array | 定位点列表（按时间升序，当天数据） |
| data.items[].devNo | string | 设备号 |
| data.items[].time | int | 定位时间戳（秒） |
| data.items[].longitude | int | 经度（×10^6） |
| data.items[].latitude | int | 纬度（×10^6） |
| data.items[].speed | int | 速度（×10，km/h） |
| data.items[].direction | int | 方向（0-359） |
| data.items[].altitude | int | 海拔（米） |
| data.items[].vehicleGuid | int | 车辆 GUID |
| data.items[].vehicleNo | string | 车牌号 |
| data.items[].receiveTime | int | 平台接收时间戳（秒） |
| data.items[].deviceMileage | int | 设备里程（米） |
| data.items[].platformMileage | int | 平台里程（米） |
| data.total | int | 总记录数 |

**存储说明**：数据存于 MinIO，路径 `test/driver_monitor/location/{devNo}.json`，每个文件是点位数组。

---

## 四、实时报警记录接口

### 24. 创建报警记录

`POST /api/driver_monitor/alarm_record`

创建一条报警记录到本地数据库。

**请求体**（JSON，`AlarmRecordCreate`）：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| alarm_time | datetime | 是 | 报警时间 |
| alarm_type | string | 是 | 报警类型，≤100 字符 |
| speed | decimal | 否 | 速度 |
| vin_code | string | 否 | VIN 号，≤50 |
| photo_url | string | 否 | 照片 URL，≤255 |
| video_url | string | 否 | 视频 URL，≤255 |
| remark | string | 否 | 备注 |

**请求示例**：

```bash
POST /api/driver_monitor/alarm_record
Content-Type: application/json

{
  "alarm_time": "2026-07-28 15:50:10",
  "alarm_type": "fatigue",
  "speed": 76.6,
  "vin_code": "LSVAM4187C2014001",
  "photo_url": "http://10.192.8.193:8011/lpatmp/alarm/123.jpg",
  "remark": "疲劳驾驶报警"
}
```

**响应示例**：

```json
{
  "code": 200,
  "message": "报警记录创建成功",
  "data": {
    "id": 1,
    "alarm_time": "2026-07-28T15:50:10",
    "alarm_type": "fatigue",
    "speed": 76.6,
    "vin_code": "LSVAM4187C2014001",
    "remark": "疲劳驾驶报警",
    "photo_url": "http://10.192.8.193:8011/lpatmp/alarm/123.jpg",
    "video_url": null,
    "create_time": "2026-07-28T15:50:11"
  }
}
```

**返回参数解析**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| message | string | 状态描述 |
| data | object | 创建的报警记录 |
| data.id | int | 记录 ID |
| data.alarm_time | datetime | 报警时间 |
| data.alarm_type | string | 报警类型 |
| data.speed | decimal | 速度 |
| data.vin_code | string | VIN 号 |
| data.remark | string | 备注 |
| data.photo_url | string | 照片 URL |
| data.video_url | string | 视频 URL |
| data.create_time | datetime | 创建时间（数据库自动生成） |

### 25. 分页查询报警记录

`GET /api/driver_monitor/alarm_records`

分页查询本地数据库中的报警记录。

**请求参数**（Query）：

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| start_time | datetime | 否 | - | 开始时间 |
| end_time | datetime | 否 | - | 结束时间 |
| alarm_type | string | 否 | - | 报警类型 |
| page | int | 否 | 1 | 页码 |
| page_size | int | 否 | 20 | 每页数量 |

**请求示例**：

```
GET /api/driver_monitor/alarm_records?start_time=2026-07-28 00:00:00&end_time=2026-07-28 23:59:59&alarm_type=fatigue&page=1&page_size=20
```

**响应示例**：

```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "total": 1,
    "page": 1,
    "page_size": 20,
    "records": [
      {
        "id": 1,
        "alarm_time": "2026-07-28T15:50:10",
        "alarm_type": "fatigue",
        "speed": 76.6,
        "vin_code": "LSVAM4187C2014001",
        "remark": "疲劳驾驶报警",
        "photo_url": "http://10.192.8.193:8011/lpatmp/alarm/123.jpg",
        "video_url": null,
        "create_time": "2026-07-28T15:50:11"
      }
    ]
  }
}
```

**返回参数解析**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| message | string | 状态描述 |
| data | object | 分页数据 |
| data.total | int | 总记录数 |
| data.page | int | 当前页码 |
| data.page_size | int | 每页数量 |
| data.records | array | 报警记录列表 |
| data.records[].id | int | 记录 ID |
| data.records[].alarm_time | datetime | 报警时间 |
| data.records[].alarm_type | string | 报警类型 |
| data.records[].speed | decimal | 速度 |
| data.records[].vin_code | string | VIN 号 |
| data.records[].remark | string | 备注 |
| data.records[].photo_url | string | 照片 URL |
| data.records[].video_url | string | 视频 URL |
| data.records[].create_time | datetime | 创建时间 |

### 26. 获取单台车辆报警信息（iotsmart）

`POST /api/driver_monitor/query_alarm_data`

从 iotsmart 平台查询报警信息。

**请求体**（JSON）：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| startTime | string | 是 | 开始时间 `YYYY-MM-DD HH:MM:SS` |
| endTime | string | 是 | 结束时间 |
| alarmTypes | list[int] | 是 | 报警类型列表（见附录） |
| handleStatus | int | 是 | 处理状态（0-未处理，1-已处理，2-全部） |
| curPage | int | 是 | 当前页 |
| pageNum | int | 是 | 每页数量 |
| vehicleNo | string | 否 | 车牌号 |
| vehicleGuids | list[int] | 否 | 车辆 GUID 列表 |
| isAll | bool | 否 | true 时不分页 |

**请求示例**：

```bash
POST /api/driver_monitor/query_alarm_data
Content-Type: application/json

{
  "startTime": "2026-07-28 00:00:00",
  "endTime": "2026-07-28 23:59:59",
  "alarmTypes": [1, 2, 5],
  "handleStatus": 0,
  "curPage": 1,
  "pageNum": 20,
  "vehicleNo": "527086498786"
}
```

**响应示例**：

```json
{
  "code": 200,
  "message": "获取单台车辆的报警信息成功",
  "data": {
    "hdr": {"code": 200, "msgType": 1234},
    "alarmList": [
      {
        "vehicleGuid": 14307,
        "devNo": "527086498786",
        "vehicleNo": "527086498786",
        "time": 1785225009,
        "alarmType": 5,
        "longitude": 120184526,
        "latitude": 30108256,
        "speed": 766,
        "alarmID": "1279508275721977856",
        "alarmLevel": 2,
        "hasAttachment": 1
      }
    ],
    "total": 1
  }
}
```

**返回参数解析**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| message | string | 状态描述 |
| data | object | 报警数据 |
| data.hdr | object | 响应头 |
| data.alarmList | array | 报警列表 |
| data.alarmList[].vehicleGuid | int | 车辆 GUID |
| data.alarmList[].devNo | string | 设备号 |
| data.alarmList[].vehicleNo | string | 车牌号 |
| data.alarmList[].time | int | 报警时间戳（秒） |
| data.alarmList[].alarmType | int | 报警类型（见附录） |
| data.alarmList[].longitude | int | 经度（×10^6） |
| data.alarmList[].latitude | int | 纬度（×10^6） |
| data.alarmList[].speed | int | 速度（×10，km/h） |
| data.alarmList[].alarmID | string | 报警 ID（用于查询附件） |
| data.alarmList[].alarmLevel | int | 报警级别（1-提示，2-警告，3-严重） |
| data.alarmList[].hasAttachment | int | 是否有附件（0-无，1-有） |
| data.total | int | 总记录数 |

### 27. 获取附件信息

`GET /api/driver_monitor/get_attachment_info`

获取报警附件信息（图片/视频 URL）。

**请求参数**（Query）：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| alarmID | string | 是 | 报警 ID |

**请求示例**：

```
GET /api/driver_monitor/get_attachment_info?alarmID=1279508275721977856
```

**返回参数解析**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| message | string | 状态描述 |
| data | object | 附件信息 |
| data.hdr | object | 响应头 |
| data.attachmentList | array | 附件列表 |
| data.attachmentList[].attachmentType | int | 附件类型（1-图片，2-视频） |
| data.attachmentList[].url | string | 附件下载 URL |
| data.attachmentList[].fileSize | int | 文件大小（字节） |

### 28. 获取某辆车某月每天的日统计信息

`GET /api/driver_monitor/daily_info`

获取指定车辆在指定月份的每日统计信息（里程、时长等）。

**请求参数**（Query）：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| dateTime | string | 是 | 月份，格式 `YYYY-MM` |
| vehicleNo | string | 是 | 车牌号 |

**请求示例**：

```
GET /api/driver_monitor/daily_info?dateTime=2026-07&vehicleNo=527086498786
```

**响应示例**：

```json
{
  "code": 200,
  "message": "获取527086498786的日统计信息成功",
  "data": {
    "hdr": {"code": 200, "msgType": 1234},
    "dailyList": [
      {
        "date": "2026-07-28",
        "mileage": 156.8,
        "duration": 28800,
        "onlineTime": 28800
      }
    ]
  }
}
```

**返回参数解析**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| message | string | 状态描述 |
| data | object | 日统计数据 |
| data.hdr | object | 响应头 |
| data.dailyList | array | 每日统计列表 |
| data.dailyList[].date | string | 日期 `YYYY-MM-DD` |
| data.dailyList[].mileage | decimal | 当日里程（km） |
| data.dailyList[].duration | int | 当日行驶时长（秒） |
| data.dailyList[].onlineTime | int | 当日在线时长（秒） |

### 29. 获取车辆上下线记录

`GET /api/driver_monitor/onoffline`

查询指定车辆在指定时间范围内的上下线记录。

**请求参数**（Query）：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| vehicleNo | string | 是 | 车牌号 |
| startTime | string | 是 | 开始时间 `YYYY-MM-DD HH:MM:SS` |
| endTime | string | 是 | 结束时间 |
| curPage | int | 是 | 当前页 |
| pageNum | int | 是 | 每页数量 |
| isAll | int | 否 | 是否全部（1=是） |

**请求示例**：

```
GET /api/driver_monitor/onoffline?vehicleNo=527086498786&startTime=2026-07-28 00:00:00&endTime=2026-07-28 23:59:59&curPage=1&pageNum=20
```

**响应示例**：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "hdr": {"code": 200, "msgType": 1234},
    "onofflineList": [
      {
        "vehicleGuid": 14307,
        "vehicleNo": "527086498786",
        "onlineTime": 1785224102,
        "offlineTime": null,
        "isOnline": true
      }
    ]
  }
}
```

**返回参数解析**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| message | string | 状态描述 |
| data | object | 上下线数据 |
| data.hdr | object | 响应头 |
| data.onofflineList | array | 上下线记录列表 |
| data.onofflineList[].vehicleGuid | int | 车辆 GUID |
| data.onofflineList[].vehicleNo | string | 车牌号 |
| data.onofflineList[].onlineTime | int | 上线时间戳（秒，null 表示未上线） |
| data.onofflineList[].offlineTime | int | 下线时间戳（秒，null 表示仍在线） |
| data.onofflineList[].isOnline | bool | 当前是否在线 |

---

### 30. 统计指定车辆某天各报警类型的次数

`GET /api/driver_monitor/alarm_type_stats`

统计指定车辆在某个日期内各报警类型的次数，按次数从高到低排序。数据来源于本地 MySQL `alarm_records` 表（由 WebSocket 报警推送自动入库）。

**请求参数**（Query）：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| vin_code | string | 是 | 车辆VIN号（对应 alarm_records.vin_code） |
| target_date | string | 否 | 日期 `YYYY-MM-DD`，默认当天 |

**请求示例**：

```
GET /api/driver_monitor/alarm_type_stats?vin_code=527086498786&target_date=2026-07-29
```

**响应示例**：

```json
{
  "message": "查询成功",
  "code": 200,
  "data": {
    "vin_code": "527086498786",
    "date": "2026-07-29",
    "total": 7,
    "stats": [
      {"alarm_type": "疲劳驾驶", "count": 3},
      {"alarm_type": "急加速报警", "count": 2},
      {"alarm_type": "驾驶员异常", "count": 1},
      {"alarm_type": "急减速报警", "count": 1}
    ]
  }
}
```

**返回参数解析**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码（200 成功） |
| message | string | 状态描述 |
| data | object | 统计结果 |
| data.vin_code | string | 车辆VIN号 |
| data.date | string | 查询日期 `YYYY-MM-DD` |
| data.total | int | 当天报警总数 |
| data.stats | array | 各报警类型统计列表（按 count 降序） |
| data.stats[].alarm_type | string | 报警类型（中文名称，如"疲劳驾驶"） |
| data.stats[].count | int | 该类型报警次数 |

**说明**：
- 报警类型对照表见 [附录 - 报警类型对照表](#报警类型对照表)
- 若该车辆当天无报警记录，`total=0`，`stats` 为空数组
- 对应 SQL：`SELECT alarm_type, COUNT(*) FROM alarm_records WHERE vin_code=? AND DATE(alarm_time)=? GROUP BY alarm_type ORDER BY COUNT(*) DESC`

---

## 五、SSE 实时推送（main.py 注册）

### 31. SSE 订阅

`GET /api/driver_monitor/sse/sub`

订阅 SSE 实时推送。统一入口，所有业务推送共用此连接，用 event 字段区分。

**请求参数**（Query）：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| username | string | 是 | 用户标识（用于区分客户端） |

**事件类型**：

| event | 说明 | 触发时机 |
|---|---|---|
| `vehicle_online_list` | 车辆在线列表 | 首次连接推送快照；WS 收到 8000 消息时广播 |
| `vehicle_status` | 车辆上下线状态 | WS 收到 8001 消息时推送 |
| `location` | 定位数据 | 每 30 秒推送最新一个点（按 devNo 分组） |
| `alert` | 报警数据 | WS 收到 8003 消息时推送 |

**前端示例**：

```javascript
const es = new EventSource('/api/driver_monitor/sse/sub?username=user_001');

// 监听车辆在线列表
es.addEventListener('vehicle_online_list', e => {
    console.log('在线车辆:', JSON.parse(e.data));
});

// 监听车辆上下线状态
es.addEventListener('vehicle_status', e => {
    console.log('车辆状态变更:', JSON.parse(e.data));
});

// 监听定位数据
es.addEventListener('location', e => {
    console.log('定位数据:', JSON.parse(e.data));
});

// 监听报警
es.addEventListener('alert', e => {
    console.log('报警:', JSON.parse(e.data));
});
```

**消息示例 - `vehicle_online_list`**：

```json
{
  "data": [
    {"vehicleGuid": 14307, "vehicleNo": "527086498786"},
    {"vehicleGuid": 14349, "vehicleNo": "527086468243"}
  ]
}
```

**消息字段解析 - `vehicle_online_list`**：

| 字段 | 类型 | 说明 |
|---|---|---|
| data | array | 在线车辆列表 |
| data[].vehicleGuid | int | 车辆 GUID |
| data[].vehicleNo | string | 车牌号 |
| data[].devNo | string | 设备号（可能存在） |
| data[].isOnline | bool | 是否在线（true） |

**消息示例 - `vehicle_status`**：

```json
{
  "data": {
    "vehicleGuid": 14307,
    "vehicleNo": "527086498786",
    "devNo": "527086498786",
    "isOnline": true
  }
}
```

**消息字段解析 - `vehicle_status`**：

| 字段 | 类型 | 说明 |
|---|---|---|
| data | object | 车辆状态 |
| data.vehicleGuid | int | 车辆 GUID |
| data.vehicleNo | string | 车牌号 |
| data.devNo | string | 设备号 |
| data.isOnline | bool | 是否在线（true-上线，false-下线） |

**消息示例 - `location`**：

```json
{
  "saveTime": "2026-07-28 15:50:09",
  "data": {
    "devNo": "527086498786",
    "time": 1785225009,
    "longitude": 120184526,
    "latitude": 30108256,
    "speed": 766,
    "direction": 348,
    "altitude": 33,
    "vehicleGuid": 14307,
    "vehicleNo": "527086498786"
  }
}
```

**消息字段解析 - `location`**：

| 字段 | 类型 | 说明 |
|---|---|---|
| saveTime | string | 后端推送时间 `YYYY-MM-DD HH:MM:SS` |
| data | object | 定位点（每 30 秒最新一个） |
| data.devNo | string | 设备号 |
| data.time | int | 定位时间戳（秒） |
| data.longitude | int | 经度（×10^6） |
| data.latitude | int | 纬度（×10^6） |
| data.speed | int | 速度（×10，km/h） |
| data.direction | int | 方向（0-359） |
| data.altitude | int | 海拔（米） |
| data.vehicleGuid | int | 车辆 GUID |
| data.vehicleNo | string | 车牌号 |

**消息示例 - `alert`**：

```json
{
  "data": {
    "vehicleGuid": 14307,
    "devNo": "527086498786",
    "vehicleNo": "527086498786",
    "time": 1785225009,
    "alarmType": 5,
    "alarmID": "1279508275721977856",
    "alarmLevel": 2,
    "longitude": 120184526,
    "latitude": 30108256,
    "speed": 766
  }
}
```

**消息字段解析 - `alert`**：

| 字段 | 类型 | 说明 |
|---|---|---|
| data | object | 报警数据 |
| data.vehicleGuid | int | 车辆 GUID |
| data.devNo | string | 设备号 |
| data.vehicleNo | string | 车牌号 |
| data.time | int | 报警时间戳（秒） |
| data.alarmType | int | 报警类型（见附录） |
| data.alarmID | string | 报警 ID |
| data.alarmLevel | int | 报警级别（1-提示，2-警告，3-严重） |
| data.longitude | int | 经度（×10^6） |
| data.latitude | int | 纬度（×10^6） |
| data.speed | int | 速度（×10，km/h） |

### 32. 按设备号订阅 SSE

`GET /api/driver_monitor/sse/sub_device`

按设备号订阅 SSE，只接收指定设备的消息。

**请求参数**（Query）：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| username | string | 是 | 用户标识 |
| devNo | string | 是 | 设备号 |

**前端示例**：

```javascript
const es = new EventSource('/api/driver_monitor/sse/sub_device?username=user_001&devNo=527086498786');
es.addEventListener('location', e => console.log(JSON.parse(e.data)));
```

**返回参数解析**：同 [30. SSE 订阅](#30-sse-订阅)，但只推送匹配 `devNo` 的消息。

---

## 六、WebSocket 管理（main.py 注册）

### 33. 启动 WebSocket

`GET /api/driver_monitor/ws_start`

启动与 iotsmart 平台的 WebSocket 长连接（SSE 订阅时会自动触发，也可手动启动）。

**请求示例**：

```
GET /api/driver_monitor/ws_start
```

**响应示例**：

```json
{
  "code": 200,
  "message": "启动成功"
}
```

**返回参数解析**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| message | string | 状态描述（"启动成功"/"已运行中"） |

### 34. 停止 WebSocket

`GET /api/driver_monitor/ws_stop`

停止 WebSocket 长连接。

**请求示例**：

```
GET /api/driver_monitor/ws_stop
```

**返回参数解析**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| message | string | 状态描述（"已停止"） |

---

## 七、数据存储说明

| 数据类型 | 存储位置 | 说明 |
|---|---|---|
| 监控信息 | MySQL `driver_monitor` 表 | 驾驶员监控记录 |
| 报警记录 | MySQL `alarm_records` 表 | 实时报警记录 |
| 定位数据 | MinIO `test/driver_monitor/location/{devNo}.json` | 每 30 秒落盘一次，按 devNo 分文件 |
| 车辆在线状态 | 内存 `online_vehicle_cache` | 三套 key（guid/no/dev）索引同一辆车，重启后丢失 |

---

## 八、附录

### WebSocket 消息类型

| msgType | 含义 | 方向 |
|---|---|---|
| 5000 | 心跳请求 | 后端 → 平台 |
| 5001 | 心跳响应 | 平台 → 后端 |
| 8000 | 车辆在线列表（初始全量） | 平台 → 后端 |
| 8001 | 车辆上下线 | 平台 → 后端 |
| 8002 | 定位数据 | 平台 → 后端 |
| 8003 | 报警数据 | 平台 → 后端 |

### 定位数据字段说明

| 字段 | 类型 | 单位/精度 | 说明 |
|---|---|---|---|
| devNo | string | - | 设备号 |
| time | int | 秒 | 定位时间戳 |
| longitude | int | ×10^6 | 经度（如 120.061486° → 120061486） |
| latitude | int | ×10^6 | 纬度 |
| speed | int | ×10 km/h | 速度（如 82.2 km/h → 822） |
| direction | int | 度 | 方向（0-359，正北为 0，顺时针） |
| altitude | int | 米 | 海拔 |
| vehicleGuid | int | - | 车辆 GUID |
| vehicleNo | string | - | 车牌号 |
| deviceMileage | int | 米 | 设备记录里程 |
| platformMileage | int | 米 | 平台记录里程 |
| curDayMileage | int | 米 | 当日里程 |
| driveTimeLen | int | 秒 | 驾驶时长 |
| receiveTime | int | 秒 | 平台接收时间戳 |
| netSignal | int | - | 网络信号强度 |
| satelliteNum | int | 颗 | 卫星数 |
| statusFlag | int | - | 状态标志位 |
| dataValidFlag | int | - | 数据有效标志位 |

### 报警类型对照表

| alarmType | 含义 |
|---|---|
| 1 | 疲劳驾驶 |
| 2 | 接打电话 |
| 3 | 抽烟 |
| 4 | 分神驾驶 |
| 5 | 驾驶员异常 |
| 6 | 自动抓拍 |
| 7 | 驾驶员变更 |
| 8 | 未系安全带 |

### 报警级别对照表

| alarmLevel | 含义 |
|---|---|
| 1 | 提示 |
| 2 | 警告 |
| 3 | 严重 |

### 数据模型

#### MonitorInfo（驾驶员监控记录）

对应数据库表 `monitor_infos`，用于存储每日驾驶员行为监控统计数据。

| 字段 | 类型 | 说明 |
|---|---|---|
| id | int | 主键 ID |
| test_date | date | 日期（索引） |
| vin_code | string(17) | 测试车辆 VIN 号（索引） |
| device_code | string(50) | 设备号 |
| fatigue | int | 疲劳驾驶次数 |
| calling | int | 接打电话次数 |
| smoke | int | 抽烟次数 |
| distract | int | 分神驾驶次数 |
| abnormal | int | 驾驶员异常次数 |
| snapshot | int | 自动抓拍次数 |
| driver_change | int | 驾驶员变更次数 |
| no_belt | int | 未系安全带次数 |
| mileage | decimal(10,1) | 行驶里程（km） |
| duration | int | 车辆上电时长（秒） |
| remark | text | 备注 |
| created_at | datetime | 创建时间 |
