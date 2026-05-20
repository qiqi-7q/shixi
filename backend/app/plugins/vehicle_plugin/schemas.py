from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from app.plugins.vehicle_plugin.models import VehicleStatus


class VehicleBase(BaseModel):
    vehicle_code: str = Field(..., max_length=50)
    vin: str = Field(..., max_length=17)
    model: str = Field(..., max_length=100)
    configuration: Optional[str] = Field(None, max_length=200)
    plate_number: Optional[str] = Field(None, max_length=20)
    temp_plate_expire_date: Optional[date] = None
    owner_name: Optional[str] = Field(None, max_length=100)
    parking_location: Optional[str] = Field(None, max_length=200)
    temp_plate_count: int = 0
    remarks: Optional[str] = None


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    vehicle_code: Optional[str] = None
    model: Optional[str] = None
    configuration: Optional[str] = None
    plate_number: Optional[str] = None
    temp_plate_expire_date: Optional[date] = None
    owner_name: Optional[str] = None
    parking_location: Optional[str] = None
    temp_plate_count: Optional[int] = None
    status: Optional[VehicleStatus] = None
    remarks: Optional[str] = None


class VehicleResponse(VehicleBase):
    id: int
    status: VehicleStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BorrowRecordBase(BaseModel):
    vehicle_id: int
    borrow_time: datetime
    return_time: Optional[datetime] = None
    borrower: str = Field(..., max_length=100)
    driver_name: Optional[str] = Field(None, max_length=100)
    task_content: Optional[str] = None
    remarks: Optional[str] = None


class BorrowRecordCreate(BorrowRecordBase):
    pass


class BorrowRecordUpdate(BaseModel):
    return_time: Optional[datetime] = None
    driver_name: Optional[str] = None
    task_content: Optional[str] = None
    status: Optional[str] = None
    remarks: Optional[str] = None


class BorrowRecordResponse(BorrowRecordBase):
    id: int
    vehicle_code: Optional[str] = None
    model: Optional[str] = None
    vin: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True