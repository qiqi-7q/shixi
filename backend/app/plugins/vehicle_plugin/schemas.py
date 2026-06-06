from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.plugins.vehicle_plugin.models import TestStatus, VehicleGroup, VehicleStatus


class VehicleBase(BaseModel):
    """车辆基础模型 - 创建和更新时的核心字段"""

    model: str = Field(..., max_length=100, description="车型")
    vehicle_code: str = Field(..., max_length=50, description="车辆编号")
    vin_code: str = Field(..., max_length=17, description="VIN码")
    owner_name: str = Field(..., max_length=100, description="车主权限")
    plate_number: str = Field(..., max_length=20, description="车牌号")
    editor: str = Field(..., max_length=20, description="最后编辑人")

    # 可选字段
    vehicle_stage: Optional[str] = Field(None, max_length=20, description="车辆阶段")
    configuration: Optional[str] = Field(None, max_length=200, description="车辆配置")
    parking_location: Optional[str] = Field(
        None, max_length=200, description="停车地点"
    )
    engine_num: Optional[str] = Field(
        None, max_length=100, description="驱动电机号/发动机号"
    )
    temp_plate_expire_date: Optional[date] = Field(None, description="临牌到期时间")
    temp_plate_count: int = 0
    remarks: Optional[str] = None


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    """更新车辆请求模型 - 所有字段可选"""

    model: Optional[str] = Field(None, max_length=100, description="车型")
    group: Optional[VehicleGroup] = Field(None, description="组别")
    vehicle_code: Optional[str] = Field(None, max_length=50, description="车辆编号")
    vin_code: Optional[str] = Field(None, max_length=17, description="VIN码")
    owner_name: Optional[str] = Field(None, max_length=100, description="车主权限")
    plate_number: Optional[str] = Field(None, max_length=20, description="车牌号")
    vehicle_stage: Optional[str] = Field(None, max_length=20, description="车辆阶段")
    configuration: Optional[str] = Field(None, max_length=200, description="车辆配置")
    parking_location: Optional[str] = Field(
        None, max_length=200, description="停车地点"
    )
    vehicle_status: Optional[VehicleStatus] = Field(None, description="车辆状态")
    test_status: Optional[TestStatus] = Field(None, description="测试状态")
    engine_num: Optional[str] = Field(
        None, max_length=100, description="驱动电机号/发动机号"
    )
    temp_plate_expire_date: Optional[date] = Field(None, description="临牌到期时间")
    temp_plate_count: Optional[int] = None
    editor: Optional[str] = Field(None, max_length=20, description="最后编辑人")
    remarks: Optional[str] = Field(None, description="备注")


class VehicleResponse(VehicleBase):
    """车辆响应模型 - 包含数据库自动生成的字段"""

    id: int
    vehicle_status: VehicleStatus = Field(
        VehicleStatus.AVAILABLE, description="车辆状态"
    )
    test_status: TestStatus = Field(TestStatus.ALL_SUPPORT, description="测试状态")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BorrowRecordBase(BaseModel):
    """借用记录基础模型"""

    vehicle_id: int = Field(..., description="车辆ID")
    model: Optional[str] = Field(None, max_length=100, description="车型")
    vehicle_code: Optional[str] = Field(None, max_length=50, description="车辆编号")
    vin_code: str = Field(..., max_length=17, description="VIN码")
    borrower: str = Field(..., max_length=100, description="借用人")
    borrow_time: date = Field(..., description="借用时间")
    driver_name: Optional[str] = Field(None, max_length=100, description="司机姓名")
    driver_work: Optional[str] = Field(None, max_length=50, description="司机工作安排")
    driver_performance: Optional[str] = Field(
        None, max_length=100, description="司机绩效"
    )
    record_creator: Optional[str] = Field(None, max_length=50, description="记录创建人")
    borrow_status: Optional[str] = Field(
        None, max_length=20, description="借用状态：active/returned/cancelled"
    )
    remarks: Optional[str] = Field(None, description="备注")


class BorrowRecordCreate(BorrowRecordBase):
    pass


class BorrowRecordUpdate(BaseModel):
    """更新借用记录请求模型 - 所有字段可选"""

    model: Optional[str] = Field(None, max_length=100, description="车型")
    vehicle_code: Optional[str] = Field(None, max_length=50, description="车辆编号")
    vin_code: Optional[str] = Field(None, max_length=17, description="VIN码")
    borrower: Optional[str] = Field(None, max_length=100, description="借用人")
    borrow_time: Optional[date] = Field(None, description="借用时间")
    driver_name: Optional[str] = Field(None, max_length=100, description="司机姓名")
    borrow_status: Optional[str] = Field(
        None, max_length=20, description="借用状态：active/returned/cancelled"
    )
    driver_work: Optional[str] = Field(None, max_length=50, description="司机工作安排")
    driver_performance: Optional[str] = Field(
        None, max_length=100, description="司机绩效"
    )
    record_creator: Optional[str] = Field(None, max_length=50, description="记录创建人")
    remarks: Optional[str] = Field(None, description="备注")


class BorrowRecordResponse(BorrowRecordBase):
    """借用记录响应模型"""

    id: int
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True


# 获取Vehicle模型所有的字段
VEHICLE_WHITELIST = set(VehicleResponse.model_fields.keys())
# 获取VehicleBorrow模型所有的字段
BORROW_WHITELIST = set(BorrowRecordResponse.model_fields.keys())
