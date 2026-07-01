from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime, date


class EmployeeBase(BaseModel):
    name: str
    # 新增字段
    module_name: Optional[str] = None
    module_manager: Optional[str] = None
    job_type: Optional[Literal["司机", "外协"]] = None
    task: Optional[str] = None
    card_validity: Optional[date] = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    card_validity: Optional[date] = None
    module_name: Optional[str] = None
    module_manager: Optional[str] = None
    job_type: Optional[Literal["司机", "外协"]] = None
    task: Optional[str] = None


class Employee(EmployeeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


EMPLOYEE_WHITELIST = set(Employee.model_fields.keys())
