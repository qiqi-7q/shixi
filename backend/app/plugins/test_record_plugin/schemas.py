from datetime import datetime

from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.plugins.test_record_plugin.models import (
    FunctionMode,
    EvaluationDimension,
    KPIType,
)


# 基础模型
class TestRecordBase(BaseModel):
    project: Optional[str] = None
    car_type: Optional[str] = None
    function_mode: Optional[FunctionMode] = None
    problem_desc: Optional[str] = None
    problem_category: Optional[EvaluationDimension] = None
    kpi_type: Optional[KPIType] = None
    problem_scene: Optional[str] = None
    problem_type: Optional[str] = None
    problem_phenomenon: Optional[str] = None
    takeover_type: Optional[str] = None
    problem_time: Optional[datetime] = None
    vin_code: Optional[str] = None
    data_link: Optional[str] = None
    wetrack_link: Optional[str] = None
    analyze_result: Optional[str] = None
    analyze_user: Optional[str] = None
    analyze_attach: Optional[str] = None
    software_version: Optional[str] = None
    remarks: Optional[str] = None


# 创建
class TestRecordCreate(TestRecordBase):
    pass


# 更新
class TestRecordUpdate(BaseModel):
    project: Optional[str] = None
    car_type: Optional[str] = None
    function_mode: Optional[FunctionMode] = None
    problem_desc: Optional[str] = None
    problem_category: Optional[EvaluationDimension] = None
    vin_code: Optional[str] = None
    kpi_type: Optional[KPIType] = None
    problem_scene: Optional[str] = None
    problem_type: Optional[str] = None
    problem_phenomenon: Optional[str] = None
    takeover_type: Optional[str] = None
    problem_time: Optional[datetime] = None
    data_link: Optional[str] = None
    wetrack_link: Optional[str] = None
    analyze_result: Optional[str] = None
    analyze_user: Optional[str] = None
    analyze_attach: Optional[str] = None
    software_version: Optional[str] = None
    remarks: Optional[str] = None


# 批量导入模型
class TestRecordBatchImport(BaseModel):
    pass
    # records: List[TestRecordCreate]


# 响应模型
class TestRecord(TestRecordBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
