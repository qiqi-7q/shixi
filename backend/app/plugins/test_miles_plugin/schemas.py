from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TestMilesBase(BaseModel):
    project: str
    test_version: Optional[str] = None
    # test_time: datetime
    test_start_time: datetime
    test_end_time: datetime

    vin_code: str
    test_function: Optional[str] = None
    mileage: Optional[float] = None
    driving_mileage: Optional[float] = None
    is_kpi: Optional[bool] = False
    remarks: Optional[str] = None


class TestMilesCreate(TestMilesBase):
    pass


class TestMilesUpdate(BaseModel):
    project: Optional[str] = None
    test_version: Optional[str] = None
    # test_time: Optional[datetime] = None
    test_start_time: Optional[datetime] = None
    test_end_time: Optional[datetime] = None
    
    vin_code: Optional[str] = None
    test_function: Optional[str] = None
    mileage: Optional[float] = None
    driving_mileage: Optional[float] = None
    is_kpi: Optional[bool] = None
    remarks: Optional[str] = None


class TestMiles(TestMilesBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 统计相关模型 ====================
class VersionMileage(BaseModel):
    """版本里程统计"""
    version: str
    total_mileage: float


class DailyMileage(BaseModel):
    """每日里程统计"""
    date: str
    total_mileage: float


class FunctionMileage(BaseModel):
    """功能里程统计"""
    function: str
    total_mileage: float


class MileageStatsResponse(BaseModel):
    """里程统计响应"""
    version_mileage: list[VersionMileage]
    daily_mileage: list[DailyMileage]
    function_mileage: list[FunctionMileage]
