from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


# 任务状态可选值
TASK_STATUS_VALUES = ["完成", "进行中", "未开始", "未达标", "挂起"]

class TestTaskBase(BaseModel):
    project: str
    test_version: Optional[str] = None
    test_time: datetime
    vin_code: str
    test_function: Optional[str] = None
    task_desc: Optional[str] = None
    task_publisher: Optional[str] = None
    test_mileage: Optional[float] = None
    test_person: Optional[str] = None
    actual_mileage: Optional[float] = None
    task_status: Literal["完成", "进行中", "未开始", "未达标", "挂起"] = "未开始"
    is_kpi: Optional[bool] = False
    reason_desc: Optional[str] = None
    remarks: Optional[str] = None


class TestTaskCreate(TestTaskBase):
    pass


class TestTaskUpdate(BaseModel):
    project: Optional[str] = None
    test_version: Optional[str] = None
    test_time: Optional[datetime] = None
    vin_code: Optional[str] = None
    test_function: Optional[str] = None
    task_desc: Optional[str] = None
    task_publisher: Optional[str] = None
    test_mileage: Optional[float] = None
    test_person: Optional[str] = None
    actual_mileage: Optional[float] = None
    task_status: Optional[Literal["完成", "进行中", "未开始", "未达标", "挂起"]] = None
    is_kpi: Optional[bool] = None
    reason_desc: Optional[str] = None
    remarks: Optional[str] = None


class TestTask(TestTaskBase):
    id: int
    task_achievement_rate: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 统计相关模型 ====================
class DailyTaskCount(BaseModel):
    """每日任务下发量"""
    date: str
    count: int


class TaskStatusCount(BaseModel):
    """任务状态分布"""
    status: str
    count: int


class FunctionTaskCount(BaseModel):
    """各功能任务量"""
    function: str
    count: int


class TaskStatsResponse(BaseModel):
    """任务统计响应"""
    daily_counts: list[DailyTaskCount]
    status_counts: list[TaskStatusCount]
    function_counts: list[FunctionTaskCount]