from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ========== DriverMonitor Schemas ==========
class MonitorBase(BaseModel):
    """驾驶员监控基础模型 - 创建和更新时的核心字段"""

    test_date: date = Field(..., description="日期")
    vin_code: str = Field(..., max_length=17, description="测试车辆VIN号")
    device_code: Optional[str] = Field(None, max_length=50, description="设备号")
    fatigue: Optional[int] = Field(None, ge=0, description="疲劳驾驶次数")
    calling: Optional[int] = Field(None, ge=0, description="接打电话次数")
    smoke: Optional[int] = Field(None, ge=0, description="抽烟次数")
    distract: Optional[int] = Field(None, ge=0, description="分神驾驶次数")
    abnormal: Optional[int] = Field(None, ge=0, description="驾驶员异常次数")
    snapshot: Optional[int] = Field(None, ge=0, description="自动抓拍次数")
    driver_change: Optional[int] = Field(None, ge=0, description="驾驶员变更次数")
    no_belt: Optional[int] = Field(None, ge=0, description="未系安全带次数")

    mileage: Optional[Decimal] = Field(None, description="行驶里程(km)")
    duration: Optional[int] = Field(None, description="车辆上电时长(s)")
    # 可选字段
    remark: Optional[str] = Field(None, description="备注")


# 创建
class MonitorCreate(MonitorBase):
    """创建驾驶员监控记录请求模型"""

    pass


# 更新
class MonitorUpdate(BaseModel):
    """更新驾驶员监控记录请求模型 - 所有字段可选"""

    test_date: date = Field(..., description="日期")
    vin_code: str = Field(..., max_length=17, description="测试车辆VIN号")
    device_code: Optional[str] = Field(None, max_length=50, description="设备号")
    fatigue: Optional[int] = Field(None, ge=0, description="疲劳驾驶次数")
    calling: Optional[int] = Field(None, ge=0, description="接打电话次数")
    smoke: Optional[int] = Field(None, ge=0, description="抽烟次数")
    distract: Optional[int] = Field(None, ge=0, description="分神驾驶次数")
    abnormal: Optional[int] = Field(None, ge=0, description="驾驶员异常次数")
    snapshot: Optional[int] = Field(None, ge=0, description="自动抓拍次数")
    driver_change: Optional[int] = Field(None, ge=0, description="驾驶员变更次数")
    no_belt: Optional[int] = Field(None, ge=0, description="未系安全带次数")

    mileage: Optional[Decimal] = Field(None, description="行驶里程(km)")
    duration: Optional[int] = Field(None, description="车辆上电时长(s)")
    # 可选字段
    remark: Optional[str] = Field(None, description="备注")


# 响应模型
class MonitorResponse(MonitorBase):
    """驾驶员监控记录响应模型 - 包含数据库自动生成的字段"""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)




# ========== IoT 平台接口 Schemas ==========

class AlarmQueryRequest(BaseModel):
    """报警数据查询请求"""

    vehicleNo: Optional[str] = Field(None, description="车牌号")
    alarmType: Optional[int] = Field(None, description="报警类型")
    alarmSource: Optional[int] = Field(None, description="报警来源")
    startTime: Optional[str] = Field(None, description="开始时间，格式: YYYY-MM-DD HH:MM:SS")
    endTime: Optional[str] = Field(None, description="结束时间，格式: YYYY-MM-DD HH:MM:SS")
    curPage: int = Field(1, ge=1, description="当前页码")
    pageNum: int = Field(1000, ge=1, le=1000, description="每页条数")
    alarmTypes: Optional[list] = Field(None, description="报警类型列表")
    handleStatus: Optional[int] = Field(None, description="处理状态")


class AttachmentRequest(BaseModel):
    """附件信息查询请求"""

    alarmID: str = Field(..., description="报警ID")


# ========== 实时报警记录 Schemas ==========

class AlarmRecordCreate(BaseModel):
    """创建报警记录请求"""
    alarm_time: datetime = Field(..., description="报警时间")
    alarm_type: str = Field(..., max_length=100, description="报警类型")
    speed: Optional[Decimal] = Field(None, description="速度")
    vin_code: Optional[str] = Field(None, max_length=50, description="车辆VIN号")
    remark: Optional[str] = Field(None, description="备注")

class AlarmRecordResponse(BaseModel):
    """报警记录响应"""
    id: int
    alarm_time: datetime
    alarm_type: str
    speed: Optional[Decimal] = None
    vin_code: Optional[str] = None
    remark: Optional[str] = None
    create_time: datetime

    model_config = ConfigDict(from_attributes=True)
    
MONITOR_WHITELIST = set(MonitorResponse.model_fields.keys())
