from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.plugins.vehicle_monitor_plugin.models import VehicleMonitor


# ========== VehicleMonitor Schemas ==========
class VehicleMonitorBase(BaseModel):
    """车辆监控基础模型 - 创建和更新时的核心字段"""

    monitor_date: Optional[date] = Field(None, description="日期")
    vin_code: Optional[str] = Field(None, max_length=17, description="测试车辆VIN号")
    power_duration: Optional[Decimal] = Field(None, description="车辆上电时间")
    usage: Optional[Decimal] = Field(None, description="使用率")
    distance: Optional[Decimal] = Field(None, description="里程")
    group: Optional[str] = Field(None, max_length=50, description="组别")
    model: Optional[str] = Field(None, max_length=50, description="车辆型号")
    power: Optional[int] = Field(None, description="上电状态(0:未上电, 1:已上电)")
    dataMQ: Optional[int] = Field(None, description="数采MQ状态(0:未连接, 1:已连接)")
    TCP: Optional[int] = Field(None, description="TCP状态(0:未连接, 1:已连接)")
    remoteMQ: Optional[int] = Field(None, description="远程MQ状态(0:未连接, 1:已连接)")
    smart_distance: Optional[Decimal] = Field(None, description="智驾里程")
    position: Optional[str] = Field(None, max_length=100, description="位置")
    max_speed: Optional[Decimal] = Field(None, description="最高车速")
    remain_battery: Optional[Decimal] = Field(None, description="剩余电量")
    charge_count: Optional[int] = Field(None, description="充电次数")
    is_del: Optional[int] = Field(None, description="是否删除(0:未删除, 1:已删除)")


# 创建
class VehicleMonitorCreate(VehicleMonitorBase):
    """创建车辆监控记录请求模型"""

    pass


# 更新
class VehicleMonitorUpdate(BaseModel):
    """更新车辆监控记录请求模型 - 所有字段可选"""

    monitor_date: Optional[date] = Field(None, description="日期")
    vin_code: Optional[str] = Field(None, max_length=17, description="测试车辆VIN号")
    power_duration: Optional[Decimal] = Field(None, description="车辆上电时间")
    usage: Optional[Decimal] = Field(None, description="使用率")
    distance: Optional[Decimal] = Field(None, description="行驶里程")
    group: Optional[str] = Field(None, max_length=50, description="组别")
    model: Optional[str] = Field(None, max_length=50, description="车辆型号")
    power: Optional[int] = Field(None, description="上电状态(0:未上电, 1:已上电)")
    dataMQ: Optional[int] = Field(None, description="数采MQ状态(0:未连接, 1:已连接)")
    TCP: Optional[int] = Field(None, description="TCP状态(0:未连接, 1:已连接)")
    remoteMQ: Optional[int] = Field(None, description="远程MQ状态(0:未连接, 1:已连接)")
    smart_distance: Optional[Decimal] = Field(None, description="智驾里程")
    position: Optional[str] = Field(None, max_length=100, description="位置")
    max_speed: Optional[Decimal] = Field(None, description="最高车速")
    remain_battery: Optional[Decimal] = Field(None, description="剩余电量")
    charge_count: Optional[int] = Field(None, description="充电次数")
    is_del: Optional[int] = Field(None, description="是否删除(0:未删除, 1:已删除)")


# 响应模型
class VehicleMonitorResponse(VehicleMonitorBase):
    """车辆监控记录响应模型 - 包含数据库自动生成的字段"""

    id: int
    create_time: datetime
    update_time: datetime

    model_config = ConfigDict(from_attributes=True)


# 获取VehicleMonitor模型所有的字段
VEHICLE_MONITOR_WHITELIST = set(VehicleMonitorResponse.model_fields.keys())
