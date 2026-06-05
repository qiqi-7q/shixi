from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
# from app.plugins.test_record_plugin.models import ProblemCategory, ProblemPhenomenon, TakeoverType
from typing import Optional

# 基础模型
class TestRecordBase(BaseModel):
    project: str
    car_type: str
    function_mode: Optional[str] = None
    problem_desc: Optional[str] = None
    problem_category: Optional[str] = None
    problem_phenomenon: Optional[str] = None
    takeover_type: Optional[str] = None
    problem_time: datetime
    vin_code: str
    data_link: Optional[str] = None
    wetrack_link: Optional[str] = None
    analyze_result: Optional[str] = None
    analyze_user: Optional[str] = None
    analyze_attach: Optional[str] = None
    software_version: Optional[str] = None
    remarks: Optional[str] = None
    # custom_fields: Optional[Dict[str, Any]] = None  # 自定义字段

# 创建
class TestRecordCreate(TestRecordBase):
    pass

# 更新
class TestRecordUpdate(BaseModel):
    project: Optional[str] = None
    car_type: Optional[str] = None
    function_mode: Optional[str] = None
    problem_desc: Optional[str] = None
    problem_category: Optional[str] = None
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
    # custom_fields: Optional[Dict[str, Any]] = None

# 批量导入模型
class TestRecordBatchImport(BaseModel):
    pass
    #records: List[TestRecordCreate]

# 响应模型
class TestRecord(TestRecordBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True