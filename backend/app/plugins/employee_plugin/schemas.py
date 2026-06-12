from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime


class EmployeeBase(BaseModel):
    name: str
    # 新增字段
    module_name: Optional[str] = None
    module_manager: Optional[str] = None
    job_type: Optional[Literal["司机", "外协"]] = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    module_name: Optional[str] = None
    module_manager: Optional[str] = None
    job_type: Optional[Literal["司机", "外协"]] = None


class Employee(EmployeeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
