from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EmployeeBase(BaseModel):
    name: str
    contact_engineer: Optional[str] = None
    third_party_company: Optional[str] = None
    contact_info: Optional[str] = None
    remarks: Optional[str] = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    contact_engineer: Optional[str] = None
    third_party_company: Optional[str] = None
    contact_info: Optional[str] = None
    remarks: Optional[str] = None


class Employee(EmployeeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
