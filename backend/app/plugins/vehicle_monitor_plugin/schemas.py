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
    distance: Optional[Decimal] = Field(None, description="里程")


# 响应模型
class VehicleMonitorResponse(VehicleMonitorBase):
    """车辆监控记录响应模型 - 包含数据库自动生成的字段"""

    id: int
    create_time: datetime
    update_time: datetime

    model_config = ConfigDict(from_attributes=True)
