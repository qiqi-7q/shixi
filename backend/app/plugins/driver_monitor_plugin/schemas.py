from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.plugins.driver_monitor_plugin.models import DriverStatus


# ========== DriverMonitor Schemas ==========
class DriverMonitorBase(BaseModel):
    """驾驶员监控基础模型 - 创建和更新时的核心字段"""

    test_date: date = Field(..., description="日期")
    test_start_time: datetime = Field(..., description="测试开始时间")
    test_end_time: datetime = Field(..., description="测试结束时间")
    vin_code: str = Field(..., max_length=17, description="测试车辆VIN号")
    driver_name: str = Field(..., max_length=50, description="司机姓名")
    dms_trigger_count: int = Field(..., ge=0, description="DMS触发次数")
    distance: Decimal = Field(..., description="行驶里程")
    power_start_duration: datetime = Field(..., description="车辆上电开始时间")
    power_end_duration: datetime = Field(..., description="车辆上电结束时间")
    driver_status: Optional[DriverStatus] = Field(..., description="司机状态")
    # 可选字段
    remark: Optional[str] = Field(None, description="备注")


# 创建
class DriverMonitorCreate(DriverMonitorBase):
    """创建驾驶员监控记录请求模型"""

    pass


# 更新
class DriverMonitorUpdate(BaseModel):
    """更新驾驶员监控记录请求模型 - 所有字段可选"""

    test_date: Optional[date] = Field(None, description="日期")
    test_start_time: Optional[datetime] = Field(None, description="测试开始时间")
    test_end_time: Optional[datetime] = Field(None, description="测试结束时间")
    vin_code: Optional[str] = Field(None, max_length=17, description="测试车辆VIN号")
    driver_name: Optional[str] = Field(None, max_length=50, description="司机姓名")
    dms_trigger_count: Optional[int] = Field(None, ge=0, description="DMS触发次数")
    distance: Optional[Decimal] = Field(None, description="行驶里程")
    power_start_duration: Optional[datetime] = Field(
        None, description="车辆上电开始时间"
    )
    power_end_duration: Optional[datetime] = Field(None, description="车辆上电结束时间")
    remark: Optional[str] = Field(None, description="备注")
    driver_status: Optional[DriverStatus] = Field(None, description="司机状态")


# 批量导入模型
class DriverMonitorBatchImport(BaseModel):
    """批量导入模型"""

    pass
    # records: List[DriverMonitorCreate]


# 响应模型
class DriverMonitorResponse(DriverMonitorBase):
    """驾驶员监控记录响应模型 - 包含数据库自动生成的字段"""

    id: int
    create_time: datetime
    update_time: datetime

    model_config = ConfigDict(from_attributes=True)
